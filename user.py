import socket
import threading

class TCPClient:
    def __init__(self, host, port):
        self.server_address = (host, port)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        try:
            self.client_socket.connect(self.server_address)
            print("Connected to server.")
            self.receive_thread = threading.Thread(target=self.receive_messages)
            self.receive_thread.start()
        except ConnectionRefusedError:
            print("Unable to connect to the server. Please check the IP and port.")
            return False
        return True
    
    def login(self, username, password):
        self.send_message(username)
        self.send_message(password)

    def send_message(self, message):
        self.client_socket.sendall(message.encode())

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024)
                if message:
                    print(message.decode().strip())
            except ConnectionResetError:
                print("Disconnected from server.")
                break

    def close(self):
        self.client_socket.close()

if __name__ == '__main__':
    host = input("Enter server IP: ")
    port = int(input("Enter server port: "))

    client = TCPClient(host, port)
    
    if client.connect():
        username = input("Enter your username: ")
        password = input("Enter your password: ")
        client.login(username, password)

        while True:
            message = input()
            if message.lower() == 'exit':
                client.close()
                break
            client.send_message(message)
