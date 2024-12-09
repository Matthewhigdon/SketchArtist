import tkinter as tk
from tkinter import PhotoImage
import subprocess

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
    players = []
    num_players = Lb.curselection()[0]

    while num_players > 0:
        new_player = "player" + str(num_players)
        players.append(new_player)
        num_players -= 1

 """   if len(players) == 2:
        player1 = artist
        player2 = suspect
    else:
        player1 = artist
        player2 = witness
        for x in players:
            x = suspect

def run_artist(){

}

def run_witness(){

}

def run_suspect(){

}
"""
# Create the main window
root = tk.Tk()
root.title("Python File Runner")

# Set a custom background image
bg_image = PhotoImage(file="assets/UI Background.png")
bg_label = tk.Label(root, image=bg_image)
bg_label.place(relwidth=1, relheight=1)


logo_image = PhotoImage(file="assets/MainLogo.png")
logo_label = tk.Label(root, image=logo_image, bg="white")
logo_label.pack(pady=10)


start_button = tk.Button(root, text="Start", command=set_player_role,
                         font=("Helvetica", 20, "bold"),
                         bg="green",
                         fg="white",
                         padx=50, pady=20,
                         relief="raised")
start_button.pack(pady=20)

Lb = tk.Listbox(root)
Lb.insert(1, '1 player')
Lb.insert(2, '2 players')
Lb.insert(3, '3 players')
Lb.insert(4, '4 players')
Lb.insert(5, '5 players')
Lb.insert(6, '6 players')
Lb.pack()

output_text = tk.Text(root, height=10, width=50)
output_text.pack(padx=20, pady=10)


root.mainloop()