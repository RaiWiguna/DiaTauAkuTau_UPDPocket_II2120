import socket
import threading
import tkinter as tk
from tkinter import scrolledtext

class UDPClient:
    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_ip = None
        self.server_port = None
        self.username = None
        self.connected = False

    def connect(self, ip, port):
        self.clear_feedback()  # Clear previous feedback
        try:
            self.server_ip = ip
            self.server_port = int(port)
            self.client_socket.sendto("CHECK_CONNECTION".encode("utf-8"), (self.server_ip, self.server_port))
            response, _ = self.client_socket.recvfrom(1024)
            if response.decode("utf-8") == "CONNECTED":
                self.connected = True
                self.display_message("Terhubung ke server.")
                connect_button.config(state=tk.DISABLED)
                login_button.config(state=tk.NORMAL)
                username_entry.config(state=tk.NORMAL)
                password_entry.config(state=tk.NORMAL)
            else:
                self.display_feedback("Koneksi belum berhasil. Coba lagi.")
        except Exception as e:
            self.display_feedback("Koneksi gagal. Pastikan IP dan Port benar.")

    def login(self, username, password):
        self.clear_feedback()  # Clear previous feedback
        if self.connected:
            self.username = username
            self.client_socket.sendto(f"LOGIN {username} {password}".encode("utf-8"), (self.server_ip, self.server_port))
            response, _ = self.client_socket.recvfrom(1024)
            message = response.decode("utf-8")
            if message == "Login berhasil.":
                self.after_login()
                self.listen_for_messages()
                send_button.config(state=tk.NORMAL)
            else:
                self.display_feedback("Salah memasukkan username atau password.")

    def after_login(self):
        # Remove the connection and login UI
        connection_frame.pack_forget()  # Hide connection frame
        chat_frame.pack(padx=10, pady=10)  # Show chat room frame
        self.display_username()  # Display the username

    def display_username(self):
        username_label = tk.Label(chat_frame, text=self.username, font=("Arial", 12, "bold"))
        username_label.pack(anchor="w", padx=10, pady=(10, 0))  # Add padding to the label

    def listen_for_messages(self):
        def receive():
            while self.connected:
                try:
                    response, _ = self.client_socket.recvfrom(1024)
                    self.display_message(response.decode("utf-8"))
                except Exception as e:
                    print(f"Error: {e}")
                    break
        threading.Thread(target=receive, daemon=True).start()

    def send_message(self, message):
        if self.connected and message:
            self.client_socket.sendto(message.encode("utf-8"), (self.server_ip, self.server_port))
            self.display_message(f'You: {message}')
            message_entry.delete(0, tk.END)

    def display_message(self, message):
        chat_text.config(state='normal')
        chat_text.insert(tk.END, message + '\n')
        chat_text.see(tk.END)
        chat_text.config(state='disabled')

    def display_feedback(self, message):
        feedback_label.config(text=message, fg="red")

    def clear_feedback(self):
        feedback_label.config(text="")

def on_connect():
    ip = ip_entry.get()
    port = port_entry.get()
    client.connect(ip, port)

def on_login():
    username = username_entry.get()
    password = password_entry.get()
    client.login(username, password)

def on_send():
    message = message_entry.get()
    client.send_message(message)
    message_entry.delete(0, tk.END)

def toggle_password_visibility():
    if password_entry.cget('show') == '*':
        password_entry.config(show='')
        app.after(3000, lambda: password_entry.config(show='*'))  # Hide after 3 seconds
    else:
        password_entry.config(show='*')

app = tk.Tk()
app.title("UDP Client")
app.geometry("600x700")  # Height and width of the window
app.resizable(False, False)

client = UDPClient()

# Connection Frame
connection_frame = tk.Frame(app)
connection_frame.pack(padx=10, pady=10)

# Adding labels for input fields
tk.Label(connection_frame, text="Server IP:").grid(row=0, column=0, sticky='e')
ip_entry = tk.Entry(connection_frame)
ip_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(connection_frame, text="Server Port:").grid(row=1, column=0, sticky='e')
port_entry = tk.Entry(connection_frame)
port_entry.grid(row=1, column=1, padx=5, pady=5)

# Feedback Label - Positioned above the buttons
feedback_label = tk.Label(connection_frame, text="", fg="red", font=("Arial", 10))  # Smaller font size
feedback_label.grid(row=2, column=0, columnspan=2)

connect_button = tk.Button(connection_frame, text="Connect", command=on_connect)
connect_button.grid(row=3, columnspan=2, pady=5)

# Login Frame
tk.Label(connection_frame, text="Username:").grid(row=4, column=0, sticky='e')
username_entry = tk.Entry(connection_frame, state=tk.DISABLED)
username_entry.grid(row=4, column=1, padx=5, pady=5)

tk.Label(connection_frame, text="Password:").grid(row=5, column=0, sticky='e')
password_entry = tk.Entry(connection_frame, show="*", state=tk.DISABLED)
password_entry.grid(row=5, column=1, padx=5, pady=5)

password_toggle = tk.Button(connection_frame, text="Show Password", command=toggle_password_visibility)
password_toggle.grid(row=5, column=2, padx=5)

login_button = tk.Button(connection_frame, text="Login", command=on_login, state=tk.DISABLED)
login_button.grid(row=6, columnspan=2, pady=5)

# Chat Frame
chat_frame = tk.Frame(app)

# Username Label will be added here after login
tk.Label(chat_frame, text="Chat:").pack()
chat_text = scrolledtext.ScrolledText(chat_frame, width=70, height=25, state='disabled')  # Adjusted height for a larger chat area
chat_text.pack(padx=10, pady=10)

tk.Label(chat_frame, text="Message:").pack()

# Frame for message entry and send button
message_frame = tk.Frame(chat_frame)
message_frame.pack(padx=10, pady=5)

message_entry = tk.Entry(message_frame, width=60)
message_entry.pack(side=tk.LEFT, padx=(0, 5))

send_button = tk.Button(message_frame, text="Send", command=on_send, state=tk.DISABLED)
send_button.pack(side=tk.LEFT)

app.mainloop()
