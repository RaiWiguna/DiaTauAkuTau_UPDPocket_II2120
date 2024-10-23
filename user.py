import socket
import threading

class TCPClient:
    def __init__(self, host, port):
        self.server_address = (host, port)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False

    def connect(self):
        try:
            self.client_socket.connect(self.server_address)
            print("Terhubung ke server.")
            self.connected = True
            self.receive_thread = threading.Thread(target=self.receive_messages)
            self.receive_thread.start()
        except ConnectionRefusedError:
            print("Tidak dapat terhubung ke server. Periksa IP dan port.")
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
                    print(message_decoded)

                    if message_decoded == "Login failed. Incorrect password.":
                        retry = input("Apakah Anda ingin login lagi? (y/n): ").strip().lower()
                        if retry == 'y':
                            username = input("Masukkan username: ")
                            password = input("Masukkan password: ")
                            self.login(username, password)
                        else:
                            print("Keluar dari program...")
                            self.close()
                            break
            except ConnectionResetError:
                print("Terputus dari server.")
                break

    def close(self):
        self.connected = False
        self.client_socket.close()

if __name__ == '__main__':
    host = input("Masukkan IP server: ")
    port = int(input("Masukkan port server: "))

    client = TCPClient(host, port)
    
    if client.connect():
        username = input("Masukkan username: ")
        password = input("Masukkan password: ")
        client.login(username, password)

        while client.connected:
            message = input()
            if message.lower() == 'exit':
                client.close()
                break
            client.send_message(message)
            