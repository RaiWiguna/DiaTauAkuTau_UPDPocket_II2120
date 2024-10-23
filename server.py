import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox

class ClientHandler(threading.Thread):
    def __init__(self, client_socket, client_address, server):
        super().__init__()
        self.client_socket = client_socket
        self.client_address = client_address
        self.server = server
        self.username = None
        self.is_authenticated = False

    def run(self):
        try:
            self.client_socket.sendall(b'Enter username:\n')
            username = self.client_socket.recv(1024).decode().strip()

            self.client_socket.sendall(b'Enter password:\n')
            password = self.client_socket.recv(1024).decode().strip()

            if self.server.authenticate(username, password):
                self.username = username
                self.is_authenticated = True
                self.client_socket.sendall(b'Login successful! Welcome to the chatroom.\n')
                self.server.log_func(f'{self.username} has joined the chat!')
                self.server.broadcast(f'{self.username} has joined the chat!', self)

                while True:
                    message = self.client_socket.recv(1024).decode().strip()
                    if message:
                        formatted_message = f'{self.username}: {message}'
                        self.server.log_func(formatted_message)
                        self.server.broadcast(formatted_message, self)
            else:
                self.client_socket.sendall(b'Login failed. Incorrect username or password.\n')
        except ConnectionResetError:
            pass
        finally:
            self.server.remove_client(self)
            self.client_socket.close()

class TCPServer(threading.Thread):
    def __init__(self, host='127.0.0.1', port=65432, log_func=None):
        super().__init__()
        self.server_address = (host, port)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.clients = []
        self.global_password = 'globalpass123'
        self.log_func = log_func
        self.running = True

    def run(self):
        self.server_socket.bind(self.server_address)
        self.server_socket.listen(5)
        self.log_func(f'Server started on {self.server_address[0]}:{self.server_address[1]}')

        while self.running:
            try:
                client_socket, client_address = self.server_socket.accept()
                self.log_func(f'Connection from {client_address}')
                client_handler = ClientHandler(client_socket, client_address, self)
                self.clients.append(client_handler)
                client_handler.start()
            except OSError:
                break

    def broadcast(self, message, sender=None):
        for client in self.clients:
            if client != sender and client.is_authenticated:
                try:
                    client.client_socket.sendall(message.encode() + b'\n')
                except:
                    self.remove_client(client)

    def remove_client(self, client):
        if client in self.clients:
            self.clients.remove(client)
            if client.is_authenticated:
                self.broadcast(f'{client.username} has left the chat.', client)

    def authenticate(self, username, password):
        return password == self.global_password

    def stop_server(self):
        self.running = False
        self.broadcast('Server is shutting down...')
        self.server_socket.close()
        self.log_func('Server stopped.')

def start_server_gui():
    def log_message(message):
        log_box.config(state='normal')
        log_box.insert('end', message + '\n')
        log_box.see('end')
        log_box.config(state='disabled')

    def start_server():
        host = ip_entry.get().strip()
        port = int(port_entry.get().strip())
        global server
        server = TCPServer(host=host, port=port, log_func=log_message)
        server.start()
        start_button.config(state='disabled')
        stop_button.config(state='normal')

    def stop_server():
        if server:
            server.stop_server()
            stop_button.config(state='disabled')
            start_button.config(state='normal')

    root = tk.Tk()
    root.title("Server GUI")

    frame = tk.Frame(root)
    frame.pack(padx=10, pady=10)

    tk.Label(frame, text="IP:").grid(row=0, column=0, sticky='e')
    ip_entry = tk.Entry(frame)
    ip_entry.grid(row=0, column=1, padx=5, pady=5)
    ip_entry.insert(0, "127.0.0.1")

    tk.Label(frame, text="Port:").grid(row=1, column=0, sticky='e')
    port_entry = tk.Entry(frame)
    port_entry.grid(row=1, column=1, padx=5, pady=5)
    port_entry.insert(0, "65432")

    start_button = tk.Button(frame, text="Start Server", command=start_server)
    start_button.grid(row=2, column=0, pady=5)

    stop_button = tk.Button(frame, text="Stop Server", command=stop_server, state='disabled')
    stop_button.grid(row=2, column=1, pady=5)

    log_box = scrolledtext.ScrolledText(root, width=60, height=20, state='disabled')
    log_box.pack(padx=10, pady=10)

    root.mainloop()

if __name__ == '__main__':
    start_server_gui()