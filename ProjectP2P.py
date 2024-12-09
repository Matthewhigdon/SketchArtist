import socket
import threading

class Peer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        self.connections = []

    def start_listening(self):
        while True:
            conn, addr = self.socket.accept()
            self.connections.append(conn)
            print(f"Connection from {addr}")
            threading.Thread(target=self.handle_connection, args=(conn,)).start()

    def handle_connection(self, conn):
        while True:
            data = conn.recv(1024)
            if not data:
                break
            print(f"Received: {data.decode()}")
            conn.sendall(b"Message received")

    def connect_to_peer(self, host, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        self.connections.append(sock)
        print(f"Connected to {host}:{port}")

    def send_message(self, message):
        for conn in self.connections:
            conn.sendall(message.encode())

if __name__ == "__main__":
    # Create a peer
    peer1 = Peer("localhost", 5000)

    # Start listening for connections
    threading.Thread(target=peer1.start_listening).start()

    # Connect to another peer (if available)
    peer1.connect_to_peer("localhost", 5000)

    while True:
        peer1.send_message(input("Please State your message: "))