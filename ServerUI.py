import tkinter as tk
from tkinter import ttk
import socket
import threading
import json
import subprocess
import time
import os
from PIL.ImageTk import PhotoImage

from DetectiveIU import DetectiveApp
from SketchArtistUI import NotepadApp
from WitnessUI import WitnessApp

# If you are hosting locally, use localhost. If another machine is joining, use the host machine's LAN IP.
HOST = '10.20.193.115'  # Host IP for connecting as client; if joining from another machine, replace with host LAN IP
PORT = 50000

class GameClient:
    def __init__(self, role_ui_callback):
        self.sock = None
        self.role_ui_callback = role_ui_callback
        self.listen_thread = None
        self.current_ui = None

    def connect_to_server(self, host, port):
        print(f"Attempting to connect to server at {host}:{port}...")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(30)  # 5-second timeout for debugging
        try:
            self.sock.connect((host, port))
            print("Connected to server successfully.")
        except socket.timeout:
            print("Connection timed out. The server did not respond.")
            return
        except socket.error as e:
            print(f"Socket error: {e}")
            return

        self.listen_thread = threading.Thread(target=self.listen_for_messages, daemon=True)
        self.listen_thread.start()

    def listen_for_messages(self):
        while True:
            msg = self.recv_message()
            if msg is None:
                print("Disconnected from server (no message received).")
                break
            self.handle_message(msg)

    def recv_message(self):
        try:
            length_data = self.sock.recv(4)
            if not length_data:
                return None
            length = int.from_bytes(length_data, 'big')
            data = self.sock.recv(length)
            if not data:
                return None
            return json.loads(data.decode('utf-8'))
        except:
            return None

    def send_message(self, msg_dict):
        try:
            msg = json.dumps(msg_dict).encode('utf-8')
            self.sock.sendall(len(msg).to_bytes(4, 'big'))
            self.sock.sendall(msg)
        except socket.error as e:
            print(f"Error sending message: {e}")

    def handle_message(self, msg):
        action = msg.get('action')
        if action == 'ASSIGN_ROLE':
            role = msg['role']
            culprit_id = msg.get('culprit_id')
            print(f"Received ASSIGN_ROLE: {role}, culprit_id: {culprit_id}")
            self.role_ui_callback(role, culprit_id)
        elif action == 'START_ROUND':
            round_num = msg['round_number']
            if hasattr(self.current_ui, 'start_round'):
                self.current_ui.start_round(round_num)
        elif action == 'CLUE':
            clue = msg['message']
            if hasattr(self.current_ui, 'display_clue'):
                self.current_ui.display_clue(clue)
        elif action == 'ROUND_END':
            if hasattr(self.current_ui, 'update_scores'):
                self.current_ui.update_scores(msg['scores'])
        elif action == 'GAME_OVER':
            if hasattr(self.current_ui, 'game_over'):
                self.current_ui.game_over(msg['scores'])

    def set_current_ui(self, ui_instance):
        self.current_ui = ui_instance

    def send_clue(self, clue):
        self.send_message({"action": "CLUE", "message": clue})

    def send_guess(self, guess_id):
        self.send_message({"action": "GUESS", "guess_id": guess_id})


def start_server(num_players):
    # Use absolute path for ServerMain.py
    script_dir = os.path.dirname(os.path.abspath(__file__))
    server_script = os.path.join(script_dir, "ServerMain.py")

    # Start the server in a new process
    print("Starting server...")
    process = subprocess.Popen([os.sys.executable, server_script], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    time.sleep(2)  # Give server some time to start listening
    print("Server start attempted.")


class MainUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sketch Artist Game - Setup")
        self.client = None

        frame = tk.Frame(root, bg="white")
        frame.pack(padx=20, pady=20)

        tk.Label(frame, text="Sketch Artist Game", font=("Helvetica", 24, "bold"), bg="white").pack(pady=10)

        self.mode_var = tk.StringVar(value="host")
        host_radio = tk.Radiobutton(frame, text="Host Game", variable=self.mode_var, value="host", bg="white")
        join_radio = tk.Radiobutton(frame, text="Join Game", variable=self.mode_var, value="join", bg="white")
        host_radio.pack(anchor='w')
        join_radio.pack(anchor='w')

        tk.Label(frame, text="Number of Players:", bg="white").pack()
        self.num_players_spin = tk.Spinbox(frame, from_=1, to=10, width=5)
        self.num_players_spin.pack()

        tk.Label(frame, text="Server Host (if joining):", bg="white").pack()
        self.host_entry = tk.Entry(frame)
        self.host_entry.insert(0, HOST)
        self.host_entry.pack()

        tk.Label(frame, text="Server Port (if joining):", bg="white").pack()
        self.port_entry = tk.Entry(frame)
        self.port_entry.insert(0, str(PORT))
        self.port_entry.pack()

        start_button = tk.Button(frame, text="Start", command=self.start_game_setup, bg="green", fg="white")
        start_button.pack(pady=20)

    def start_game_setup(self):
        mode = self.mode_var.get()
        num_players = int(self.num_players_spin.get())
        host = self.host_entry.get()
        port = int(self.port_entry.get())

        # Clear UI first, show a message
        for widget in self.root.winfo_children():
            widget.destroy()
        waiting_label = tk.Label(self.root, text="Starting...", font=("Helvetica", 18))
        waiting_label.pack(pady=50)
        self.root.update()

        if mode == "host":
            start_server(num_players)
            # Increase wait time to ensure server is listening
            time.sleep(3)

            self.client = GameClient(role_ui_callback=self.init_role_ui)
            self.client.connect_to_server(HOST, PORT)
        else:
            self.client = GameClient(role_ui_callback=self.init_role_ui)
            self.client.connect_to_server(host, port)

        # Update waiting message
        for widget in self.root.winfo_children():
            widget.destroy()
        tk.Label(self.root, text="Waiting for role assignment...", font=("Helvetica", 18)).pack(pady=50)

    def init_role_ui(self, role, culprit_id):
        for widget in self.root.winfo_children():
            widget.destroy()

        print(f"Initializing role UI for role: {role}")
        if role == 'witness':
            self.app = WitnessApp(self.root, on_clue_submit=self.client.send_clue)
            if culprit_id is not None:
                self.app.set_culprit_id(culprit_id)
        elif role == 'artist':
            self.app = NotepadApp(self.root)
        elif role == 'detective':
            self.app = DetectiveApp(self.root, on_guess_submit=self.client.send_guess)
        else:
            tk.Label(self.root, text=f"Unknown role: {role}", font=("Helvetica", 18), fg="red").pack(pady=50)
            return

        self.client.set_current_ui(self.app)


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x600")

    bg_image = PhotoImage(file="assets/UI Background.png")
    bg_label = tk.Label(root, image=bg_image)
    bg_label.place(relwidth=1, relheight=1)

    MainUI(root)
    root.mainloop()
