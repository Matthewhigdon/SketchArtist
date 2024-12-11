import tkinter as tk
from PIL import Image, ImageTk
import time
import UI

class WitnessApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Witness Game with Timer")

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
        # Instruction Textbox with a black border
        self.instruction_frame = tk.Frame(self.root, bg="white", highlightbackground="black", highlightthickness=2)
        self.instruction_frame.place(relx=0.5, y=20, anchor=tk.N)

        # Main Title
        title = tk.Label(
            self.instruction_frame,
            text="You're the Witness!",
            font=("Helvetica", 24, "bold"),
            fg="orange",
            bg="white"
        )
        title.pack()

        # Subtitle (dynamic based on Listbox selection)
        self.subtitle = tk.Label(
            self.instruction_frame,
            text="the culprit is: None",
            font=("Helvetica", 16),
            fg="blue",
            bg="white"
        )
        self.subtitle.pack()

    def add_text_entry(self):
        # Frame for the text entry and submit button with a black border
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
        print(f"Submitted description: {guess}")  # Replace with desired action
        self.text_entry.delete(0, tk.END)  # Clear the entry field
    def update_culprit(self):
        selected_items = UI.Lb.curselection()
        if selected_items:
            culprit_name = UI.Lb.get(selected_items[0])
            self.subtitle.config(text=f"the culprit is: {culprit_name}")
        else:
            self.subtitle.config(text="the culprit is: None")


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
    app = WitnessApp(root)  # Correctly instantiate WitnessApp
    root.geometry("800x600")
    root.mainloop()
