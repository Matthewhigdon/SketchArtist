import tkinter as tk
from tkinter import PhotoImage
import subprocess
import SketchArtistUI


class player:
    def __init__(self, player_number, role):
        self.player_number = player_number
        self.role = role

    def get_role(self):
        return self.role

    def set_role(self, role):
        self.role = role

    def get_player_number(self):
        return self.player_number

    def set_player_number(self, player_number):
        self.player_number = player_number


def run_login_script():
    try:
        # Run the Login.py script directly
        result = subprocess.run(['python', 'Login.py'], capture_output=True, text=True)
        output_text.delete(1.0, tk.END)
        output_text.insert(tk.END, result.stdout)
        if result.stderr:
            output_text.insert(tk.END, "\nError: " + result.stderr)
    except Exception as e:
        output_text.insert(tk.END, f"Error: {e}")


def set_player_role():
    print("hit")
    players = []

    # Get the selected number of players from Listbox (adjusted for 1-based index)
    num_players = Lb.curselection()[0] + 1  # Listbox selections are 0-based, so add 1 to get correct player count

    while num_players > 1:
        new_player = player(num_players, "suspect")
        players.append(new_player)
        num_players -= 1
    if num_players == 1:
        new_player = player(num_players, "witness")
        players.append(new_player)
        num_players -= 1
    if num_players == 0:
        new_player = player(num_players, "artist")
        players.append(new_player)

    for x in players:
        if x.role == "artist":
            run_artist()
        if x.role == "suspect":
            run_suspect()
        if x.role == "witness":
            run_witness()


def run_artist():
    root_a = tk.Toplevel()
    app = SketchArtistUI.NotepadApp(root_a)
    root_a.geometry("800x600")
    root_a.mainloop()


def run_witness():
    root_w = tk.Toplevel()
    app = SketchArtistUI.NotepadApp(root_w)
    root_w.geometry("800x600")
    root_w.mainloop()


def run_suspect():
    root_s = tk.Toplevel()
    app = SketchArtistUI.NotepadApp(root_s)
    root_s.geometry("800x600")
    root_s.mainloop()


# Create the main window
root = tk.Tk()
root.title("Python File Runner")
root.geometry("800x600")

# Set a custom background image
bg_image = PhotoImage(file="assets/UI Background.png")
bg_label = tk.Label(root, image=bg_image)
bg_label.place(relwidth=1, relheight=1)

# Frame to hold the logo and the dropdown (Listbox)
top_frame = tk.Frame(root, bg="white")
top_frame.pack(pady=10)

# Logo Image
logo_image = PhotoImage(file="assets/MainLogo.png")
logo_label = tk.Label(top_frame, image=logo_image, bg="white")
logo_label.pack(side=tk.LEFT, padx=10)  # Place logo on the left side

# Listbox (Dropdown) next to the logo
Lb = tk.Listbox(top_frame, height=6, width=20, font=("Helvetica", 14))
Lb.insert(1, '1 player')
Lb.insert(2, '2 players')
Lb.insert(3, '3 players')
Lb.insert(4, '4 players')
Lb.insert(5, '5 players')
Lb.insert(6, '6 players')
Lb.pack(side=tk.LEFT, padx=10)  # Place the Listbox next to the logo

# Start Button
start_button = tk.Button(root, text="Start", command=set_player_role,
                         font=("Helvetica", 20, "bold"),
                         bg="green",
                         fg="white",
                         padx=50, pady=20,
                         relief="raised")
start_button.pack(pady=20)

# Output text box
output_text = tk.Text(root, height=10, width=50)
output_text.pack(padx=20, pady=10)

root.mainloop()
