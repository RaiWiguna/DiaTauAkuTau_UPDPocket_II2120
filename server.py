import socket
import threading

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
            self.client_socket.sendall(b'Enter your username: ')
            username = self.client_socket.recv(1024).decode().strip()

            self.client_socket.sendall(b'Enter your password: ')
            password = self.client_socket.recv(1024).decode().strip()

            if self.server.authenticate(username, password):
                self.username = username
                self.is_authenticated = True
                self.client_socket.sendall(b'Login successful! Welcome to the chatroom.\n')
                self.server.broadcast(f'{self.username} has joined the chat!', self)

                while True:
                    message = self.client_socket.recv(1024).decode().strip()
                    if message:
                        formatted_message = f'{self.username}: {message}'
                        print(formatted_message)
                        self.server.broadcast(formatted_message, self)
            else:
                self.client_socket.sendall(b'Login failed. Incorrect username or password.\n')
        except ConnectionResetError:
            pass
        finally:
            self.server.remove_client(self)
            self.client_socket.close()

class TCPServer:
    def __init__(self, host='127.0.0.1', port=65432):
        self.server_address = (host, port)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = []
        self.users = {
            'admin': 'admin123',
            'user1': 'password1',
            'Rai': 'Rai12',
            'Timy':'Timy12'
        }

    def start_server(self):
        self.server_socket.bind(self.server_address)
        self.server_socket.listen(5)
        print(f'Server started on {self.server_address[0]}:{self.server_address[1]}')

        while True:
            client_socket, client_address = self.server_socket.accept()
            print(f'Connection from {client_address}')
            client_handler = ClientHandler(client_socket, client_address, self)
            self.clients.append(client_handler)
            client_handler.start()

    def broadcast(self, message, sender):
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
        return username in self.users and self.users[username] == password

if __name__ == '__main__':
    server = TCPServer()
    server.start_server()
