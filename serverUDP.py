import socket 
import threading
import tkinter as tk
from tkinter import messagebox

class UDPServer:
    def __init__(self, host='127.0.0.1', port=12345):
        self.host = host
        self.port = port
        self.buffer_size = 1024
        self.connected_clients = {}
        self.global_password = "globalpass123"
        self.server_socket = None

    def start_server(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.server_socket.bind((self.host, self.port))
            self.log(f"Server berjalan pada {self.host}:{self.port}")
            self.listen_for_clients()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal memulai server: {e}")

    def listen_for_clients(self):
        def handle_clients():
            while True:
                try:
                    message, client_address = self.server_socket.recvfrom(self.buffer_size)
                    message = message.decode("utf-8")

                    if message == "CHECK_CONNECTION":
                        self.server_socket.sendto("CONNECTED".encode("utf-8"), client_address)

                    elif client_address not in self.connected_clients:
                        if message.startswith("LOGIN"):
                            parts = message.split(' ')
                            username = ' '.join(parts[1:-1])  # Join all but last part as username
                            password = parts[-1]  # The last part is the password

                            if password != self.global_password:
                                self.server_socket.sendto("Password salah.".encode("utf-8"), client_address)
                                continue
                            if username in self.connected_clients.values():
                                self.server_socket.sendto("Username sudah digunakan.".encode("utf-8"), client_address)
                                continue
                            self.connected_clients[client_address] = username
                            self.server_socket.sendto("Login berhasil.".encode("utf-8"), client_address)
                            self.log(f"[Login] Klien {username} ({client_address}) telah terhubung.")
                        else:
                            self.server_socket.sendto("Silakan login terlebih dahulu.".encode("utf-8"), client_address)

                    else:
                        username = self.connected_clients[client_address]
                        self.log(f"[Aktivitas] Dari {username} ({client_address}): {message}")
                        self.broadcast_message(f"{username}: {message}", client_address)

                except Exception as e:
                    print(f"Error: {e}")
                    break

        threading.Thread(target=handle_clients, daemon=True).start()

    def broadcast_message(self, message, sender_address):
        for client_address in self.connected_clients.keys():
            if client_address != sender_address:
                self.server_socket.sendto(message.encode("utf-8"), client_address)

    def log(self, message):
        log_text.insert(tk.END, message + "\n")
        log_text.see(tk.END)

def start_server():
    host = ip_entry.get()
    port = int(port_entry.get())
    server = UDPServer(host, port)
    server.start_server()

app = tk.Tk()
app.title("UDP Server")
app.geometry("500x500")  # Updated size for consistency
app.resizable(False, False)

tk.Label(app, text="Server IP:").pack()
ip_entry = tk.Entry(app)
ip_entry.pack()

tk.Label(app, text="Server Port:").pack()
port_entry = tk.Entry(app)
port_entry.pack()

start_button = tk.Button(app, text="Start Server", command=start_server)
start_button.pack(pady=5)

tk.Label(app, text="Log Aktivitas:").pack()
log_text = tk.Text(app, height=20, width=60)  # Updated text box size
log_text.pack(padx=10, pady=10)

app.mainloop()