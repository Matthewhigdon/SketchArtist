import tkinter as tk
from PIL import Image, ImageTk
import time

class DetectiveApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Detective Game with Timer")

        # Backdrop Image
        self.set_backdrop("assets/UI Background.png")

        # Instruction Textbox
        self.add_instruction_textbox()

        # Timer
        self.timer_label = tk.Label(self.root, font=("Helvetica", 20), bg="#d3d3d3", fg="black")
        self.timer_label.place(x=10, y=100)

        # Text Entry Box
        self.add_text_entry()

        # Starts timer
        self.update_timer()

    def set_backdrop(self, image_path):
        # Load and set the background image
        image = Image.open(image_path)
        self.bg_image = ImageTk.PhotoImage(image)
        bg_label = tk.Label(self.root, image=self.bg_image)
        bg_label.place(relwidth=1, relheight=1)

    def add_instruction_textbox(self):
        # Instruction Textbox
        frame = tk.Frame(self.root, bg="white")
        frame.place(relx=0.5, y=20, anchor=tk.N)

        # Main Title
        title = tk.Label(
            frame,
            text="You're a Detective!",
            font=("Helvetica", 24, "bold"),
            fg="orange",
            bg="white"
        )
        title.pack()

        # Subtitle
        subtitle = tk.Label(
            frame,
            text="guess who the culprit is",
            font=("Helvetica", 16),
            fg="blue",
            bg="white"
        )
        subtitle.pack()

    def add_text_entry(self):
        # Frame for the text entry and submit button
        entry_frame = tk.Frame(self.root, bg="white", highlightbackground="black", highlightthickness=2)
        entry_frame.place(relx=0.5, rely=0.4, anchor=tk.CENTER)

        # Entry field
        self.text_entry = tk.Entry(entry_frame, font=("Helvetica", 16), width=30, relief=tk.FLAT)
        self.text_entry.pack(pady=10)

        # Submit button
        submit_button = tk.Button(
            entry_frame,
            text="Submit",
            font=("Helvetica", 14),
            command=self.handle_submit
        )
        submit_button.pack(pady=5)

    def handle_submit(self):
        # Get the text from the entry field
        guess = self.text_entry.get()



        

        self.text_entry.delete(0, tk.END) # Clear the entry field

    def update_timer(self):
        total_rounds = 5
        countdown_seconds = 60
        pause_seconds = 10

        def run_timer(round_count):
            if round_count > total_rounds:
                self.timer_label.config(text="Done!", fg="green")  # End message
                return

            def countdown(remaining):
                if remaining >= 0:
                    self.timer_label.config(
                        text=f"Timer: {remaining} seconds",
                        fg="black"
                    )
                    self.root.after(1000, lambda: countdown(remaining - 1))
                else:
                    pause(pause_seconds)

            def pause(remaining):
                if remaining > 0:
                    self.timer_label.config(
                        text=f"Paused: {remaining} seconds",
                        fg="blue"
                    )
                    self.root.after(1000, lambda: pause(remaining - 1))
                else:
                    run_timer(round_count + 1)

            countdown(countdown_seconds)

        run_timer(1)  # Start the first round






# Run the Application
if __name__ == "__main__":
    root = tk.Tk()
    app = DetectiveApp(root)
    root.geometry("800x600")
    root.mainloop()