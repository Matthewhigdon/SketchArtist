import socket
import threading

class Peer:
	def __init__(self, host, port):
		self.host = host
		self.port = port
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.connections = []
        
def connect(self, peer_host, peer_port):
    try:
        connection = self.socket.connect((peer_host, peer_port))
        self.connections.append(connection)
        print("Connected to other Player!")
    except socket.error as e:
        print("Failed! Figure out what's wrong!")
        
def listen(self):
    self.socket.bind((self.host, self.port))
    self.socket.listen(10)
    print("Listening, Listening...")
    
    while True:
        connection, address = self.socket.accept()
        self.connections.append(connection)
        print("Connected! Good job!")
        
def send_data(self, data):
    for connection in self.connections:
        try:
            connection.sendall(data.encode())
        except socket.error as e:
            print("Failed! Cause? {e}")
            
def start(self):
    listen_thread = threading.Thread(target = self.listen)
    listen_thread.start()
    
def listener():
    name = input("Enter hostname: ")
    port = int(input("Enter the port you would like to connect on: "))

    a = Peer(name, port)
    print("Hello " + name + "!")

    listen(a)
    
def connector():
    name = input("Enter hostname of Player you would like to play with: ")
    port = int(input("Enter the port you would like to connect to: "))
    
    b = Peer(name, port)
    print("Hello " + name + "!")
    
    connect(b, name, port)
    
choice = input("Are you starting the connection or connecting to one already in place? Start or Connect: ")

if choice == "Start":
    listener()
elif choice == "Connect":
    connector()