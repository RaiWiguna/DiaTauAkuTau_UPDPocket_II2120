import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox

class TCPClient:
    def __init__(self, log_func, login_success_func):
        self.server_address = None
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False
        self.log_func = log_func
        self.login_success_func = login_success_func
        self.is_logged_in = False

    def connect(self, host, port):
        self.server_address = (host, port)
        try:
            self.client_socket.connect(self.server_address)
            self.connected = True
            self.log_func("Connected to server.")
            self.receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
            self.receive_thread.start()
        except ConnectionRefusedError:
            self.log_func("Failed to connect to server.")
            return False
        return True

    def login(self, username, password):
        self.send_message(username)
        self.send_message(password)

    def send_message(self, message):
        if self.connected:
            self.client_socket.sendall(message.encode())

    def receive_messages(self):
        while self.connected:
            try:
                message = self.client_socket.recv(1024)
                if message:
                    message_decoded = message.decode().strip()
                    if message_decoded == "Login successful! Welcome to the chatroom.":
                        self.is_logged_in = True
                        self.login_success_func()
                    else:
                        self.log_func(message_decoded)
            except ConnectionResetError:
                self.log_func("Disconnected from server.")
                break

    def close(self):
        self.connected = False
        self.client_socket.close()

def start_client_gui():
    def log_message(message):
        chat_box.config(state='normal')
        chat_box.insert('end', message + '\n')
        chat_box.see('end')
        chat_box.config(state='disabled')

    def connect_to_server():
        host = ip_entry.get().strip()
        port = int(port_entry.get().strip())
        if client.connect(host, port):
            login_button.config(state='normal')
            connect_button.config(state='disabled')

    def login_to_server():
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        client.login(username, password)

    def login_successful():
        log_message("Login successful! Welcome to the chatroom.")
        root.after(3000, clear_login_message)  # Clear message after 3 seconds
        username_entry.config(state='disabled')
        password_entry.config(state='disabled')
        chat_frame.pack(padx=10, pady=10)  # Show chat room frame

    def clear_login_message():
        chat_box.config(state='normal')
        chat_box.delete('1.0', 'end')
        chat_box.config(state='disabled')

    def send_chat_message(event=None):  # Modified to handle "Enter" key
        message = message_entry.get().strip()
        if message:
            client.send_message(message)
            log_message(f'You: {message}')  # Display user message in the chat
            message_entry.delete(0, 'end')
        if message.lower() == 'exit':
            client.close()
            root.quit()

    def toggle_password_visibility():
        if password_entry.cget('show') == '*':
            password_entry.config(show='')
            root.after(3000, lambda: password_entry.config(show='*'))  # Hide password after 3 seconds
        else:
            password_entry.config(show='*')

    client = TCPClient(log_func=log_message, login_success_func=login_successful)

    root = tk.Tk()
    root.title("Client GUI")

    # Connection Frame
    connection_frame = tk.Frame(root)
    connection_frame.pack(padx=10, pady=10)

    tk.Label(connection_frame, text="IP:").grid(row=0, column=0, sticky='e')
    ip_entry = tk.Entry(connection_frame)
    ip_entry.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(connection_frame, text="Port:").grid(row=1, column=0, sticky='e')
    port_entry = tk.Entry(connection_frame)
    port_entry.grid(row=1, column=1, padx=5, pady=5)

    connect_button = tk.Button(connection_frame, text="Connect", command=connect_to_server)
    connect_button.grid(row=2, columnspan=2, pady=5)

    # Login Frame
    tk.Label(connection_frame, text="Username:").grid(row=3, column=0, sticky='e')
    username_entry = tk.Entry(connection_frame)
    username_entry.grid(row=3, column=1, padx=5, pady=5)

    tk.Label(connection_frame, text="Password:").grid(row=4, column=0, sticky='e')
    password_entry = tk.Entry(connection_frame, show='*')
    password_entry.grid(row=4, column=1, padx=5, pady=5)

    password_toggle = tk.Button(connection_frame, text="Show Password", command=toggle_password_visibility)
    password_toggle.grid(row=4, column=2, padx=5)

    login_button = tk.Button(connection_frame, text="Login", command=login_to_server, state='disabled')
    login_button.grid(row=5, columnspan=2, pady=5)

    # Chat Frame (Initially hidden)
    chat_frame = tk.Frame(root)

    chat_box = scrolledtext.ScrolledText(chat_frame, width=60, height=20, state='disabled')
    chat_box.pack(padx=10, pady=10)

    message_entry = tk.Entry(chat_frame, width=50)
    message_entry.pack(side='left', padx=10, pady=10)
    message_entry.bind('<Return>', send_chat_message)  # Bind "Enter" key to send message

    send_button = tk.Button(chat_frame, text="Send", command=send_chat_message)
    send_button.pack(side='left', padx=5, pady=10)

    root.mainloop()

if __name__ == '__main__':
    start_client_gui()