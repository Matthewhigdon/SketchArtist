import tkinter as tk
from tkinter import ttk
import socket
import threading
import json
import subprocess

# Import the role-specific UIs
# Make sure these files expose classes like DetectiveApp, NotepadApp, WitnessApp
from DetectiveIU import DetectiveApp
from SketchArtistUI import NotepadApp  # Assuming NotepadApp is the artist UI
from WitnessUI import WitnessApp

HOST = '127.0.0.1'  # Host IP for connecting to or hosting a server
PORT = 5000  # Port must match the server


class GameClient:
    def __init__(self, role_ui_callback):
        self.sock = None
        self.role_ui_callback = role_ui_callback
        self.listen_thread = None

    def connect_to_server(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        # Start a thread to listen for server messages
        self.listen_thread = threading.Thread(target=self.listen_for_messages, daemon=True)
        self.listen_thread.start()

    def listen_for_messages(self):
        while True:
            msg = self.recv_message()
            if msg is None:
                print("Disconnected from server")
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
        msg = json.dumps(msg_dict).encode('utf-8')
        self.sock.sendall(len(msg).to_bytes(4, 'big'))
        self.sock.sendall(msg)

    def handle_message(self, msg):
        action = msg.get('action')
        if action == 'ASSIGN_ROLE':
            # We got our role from the server
            role = msg['role']
            culprit_id = msg.get('culprit_id')  # only if witness
            self.role_ui_callback(role, culprit_id)
        elif action == 'START_ROUND':
            # Notify current UI about round start
            # The UI classes should provide a method like `start_round(round_number)`
            round_num = msg['round_number']
            if hasattr(self.current_ui, 'start_round'):
                self.current_ui.start_round(round_num)
        elif action == 'CLUE':
            # Witness clue broadcast
            clue = msg['message']
            if hasattr(self.current_ui, 'display_clue'):
                self.current_ui.display_clue(clue)
        elif action == 'ROUND_END':
            # Update scores if needed
            if hasattr(self.current_ui, 'update_scores'):
                self.current_ui.update_scores(msg['scores'])
        elif action == 'GAME_OVER':
            if hasattr(self.current_ui, 'game_over'):
                self.current_ui.game_over(msg['scores'])

    def set_current_ui(self, ui_instance):
        self.current_ui = ui_instance

    def send_clue(self, clue):
        # Called by witness UI when clue is submitted
        self.send_message({"action": "CLUE", "message": clue})

    def send_guess(self, guess_id):
        # Called by detective UI when guess is submitted
        self.send_message({"action": "GUESS", "guess_id": guess_id})


def start_server(num_players):
    # Start the server in a separate process
    # Requires that Main.py is set up as a server with TOTAL_PLAYERS = num_players
    subprocess.Popen(["python", "Main.py"])


class MainUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sketch Artist Game - Setup")
        self.client = None

        # Host/Join Selection
        frame = tk.Frame(root, bg="white")
        frame.pack(padx=20, pady=20)

        tk.Label(frame, text="Sketch Artist Game", font=("Helvetica", 24, "bold"), bg="white").pack(pady=10)

        self.mode_var = tk.StringVar(value="host")
        host_radio = tk.Radiobutton(frame, text="Host Game", variable=self.mode_var, value="host", bg="white")
        join_radio = tk.Radiobutton(frame, text="Join Game", variable=self.mode_var, value="join", bg="white")
        host_radio.pack(anchor='w')
        join_radio.pack(anchor='w')

        # Number of players (if hosting)
        tk.Label(frame, text="Number of Players:", bg="white").pack()
        self.num_players_spin = tk.Spinbox(frame, from_=1, to=10, width=5)
        self.num_players_spin.pack()

        # Host and Port for joining
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

        if mode == "host":
            # Start the server locally
            start_server(num_players)
            # Wait a moment for the server to start (in production, check properly)
            time.sleep(1)
            # Connect as a client to the local server
            self.client = GameClient(role_ui_callback=self.init_role_ui)
            self.client.connect_to_server(HOST, PORT)
        else:
            # Join game as a client
            self.client = GameClient(role_ui_callback=self.init_role_ui)
            self.client.connect_to_server(host, port)

        # Clear the setup UI
        for widget in self.root.winfo_children():
            widget.destroy()
        tk.Label(self.root, text="Waiting for role assignment...", font=("Helvetica", 18)).pack(pady=50)

    def init_role_ui(self, role, culprit_id):
        # Clear the waiting screen
        for widget in self.root.winfo_children():
            widget.destroy()

        # Now based on the role, open the corresponding UI
        # We'll pass a reference to the client so the UI can send messages
        if role == 'witness':
            self.app = WitnessApp(self.root, on_clue_submit=self.client.send_clue)
            if culprit_id is not None:
                # In a real implementation, you'd also have a way for the witness
                # to know who the culprit is. The culprit_id would map to a player.
                # This might require additional logic or a players list.
                self.app.set_culprit_id(culprit_id)
        elif role == 'artist':
            self.app = NotepadApp(self.root)
        elif role == 'detective':
            # Detective guesses might need to call self.client.send_guess(guess_id)
            self.app = DetectiveApp(self.root, on_guess_submit=self.client.send_guess)
        else:
            tk.Label(self.root, text=f"Unknown role: {role}", font=("Helvetica", 18), fg="red").pack(pady=50)
            return

        self.client.set_current_ui(self.app)


# Run the Application
if __name__ == "__main__":
    import time  # Moved here to avoid issues if time wasn't imported above

    root = tk.Tk()
    root.geometry("800x600")
    MainUI(root)
    root.mainloop()
