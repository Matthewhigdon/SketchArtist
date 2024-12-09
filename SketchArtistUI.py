import tkinter as tk
from tkinter import Canvas, PhotoImage
from PIL import Image, ImageTk
import threading
import time

# Simulate the external method that provides timer value
def fetch_timer_value():
    # Example: Increment a counter every second
    timer_value = 0
    while True:
        yield timer_value
        timer_value += 1
        time.sleep(1)

# The Notepad Class (Drawable Canvas)
class Notepad(Canvas):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.bind("<B1-Motion>", self.draw)

    def draw(self, event):
        x, y = event.x, event.y
        radius = 2
        self.create_oval(x - radius, y - radius, x + radius, y + radius, fill="black")

# Main Application
class NotepadApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Drawable Notepad with Timer")

        # Backdrop Image
        self.set_backdrop("background.jpg")

        # Timer
        self.timer_label = tk.Label(self.root, font=("Helvetica", 20), bg="#d3d3d3", fg="black")
        self.timer_label.place(x=10, y=10)

        # Notepad
        self.notepad = Notepad(self.root, width=600, height=400, bg="white")
        self.notepad.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Starts timer
        self.timer_gen = fetch_timer_value()
        self.update_timer()

    def set_backdrop(self, image_path):
        # Load and set the background image
        image_path = "assets/UI Background.png"
        image = Image.open(image_path)
        self.bg_image = ImageTk.PhotoImage(image)
        bg_label = tk.Label(self.root, image=self.bg_image)
        bg_label.place(relwidth=1, relheight=1)




#the timer has 5 rounds, counts down 60 seconds in black then 10 seconds in blue
    #the blue timer is for people who are still guessing
    def update_timer(self):
        total_rounds = 5
        countdown_seconds = 60  #black
        pause_seconds = 10  #blue

        def run_timer(round_count):
            if round_count > total_rounds:
                self.timer_label.config(text="Done!", fg="green")  # End message
                return

            # Countdown phase
            def countdown(remaining):
                if remaining >= 0:
                    self.timer_label.config(
                        text=f"Timer: {remaining} seconds",
                        fg="black"
                    )
                    self.root.after(1000, lambda: countdown(remaining - 1))
                else:
                    # Transition to blue phase
                    pause(pause_seconds)

            #blue phase
            def pause(remaining):
                if remaining > 0:
                    self.timer_label.config(
                        text=f"Paused: {remaining} seconds",
                        fg="blue"
                    )
                    self.root.after(1000, lambda: pause(remaining - 1))
                else:
                    # Start next round
                    run_timer(round_count + 1)

            countdown(countdown_seconds)

        run_timer(1)  # Start the first round

# Run the Application
if __name__ == "__main__":
    root = tk.Tk()
    app = NotepadApp(root)
    root.geometry("800x600")
    root.mainloop()

