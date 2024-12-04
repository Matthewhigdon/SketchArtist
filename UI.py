import tkinter as tk
from tkinter import PhotoImage
import subprocess

def run_login_script():
    try:
        # Run the Login.py script directly
        result = subprocess.run(['python', 'Login.py'], capture_output=True, text=True)
        output_text.delete(1.0, tk.END)  # Clear previous output
        output_text.insert(tk.END, result.stdout)  # Show output in the text box
        if result.stderr:
            output_text.insert(tk.END, "\nError: " + result.stderr)  # Show errors
    except Exception as e:
        output_text.insert(tk.END, f"Error: {e}")

# Create the main window
root = tk.Tk()
root.title("Python File Runner")

# Set a custom background image
bg_image = PhotoImage(file="assets/UI Background.png")  # Replace with your background image path
bg_label = tk.Label(root, image=bg_image)
bg_label.place(relwidth=1, relheight=1)  # Make background cover the whole window

# Add a logo at the top of the window
logo_image = PhotoImage(file="assets/MainLogo.png")  # Replace with your logo image path
logo_label = tk.Label(root, image=logo_image, bg="white")  # Add logo with a white background
logo_label.pack(pady=10)

# Add the Start button with custom styling
start_button = tk.Button(root, text="Start", command=run_login_script,
                         font=("Helvetica", 20, "bold"),  # Font style and size
                         bg="green",  # Button background color
                         fg="white",  # Button text color
                         padx=50, pady=20,  # Padding inside the button
                         relief="raised")  # Button border style
start_button.pack(pady=20)

# Add a text box to display the output of the script
output_text = tk.Text(root, height=10, width=50)
output_text.pack(padx=20, pady=10)

# Start the UI loop
root.mainloop()
