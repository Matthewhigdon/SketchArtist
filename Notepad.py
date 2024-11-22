import tkinter as tk
from tkinter import ttk

def draw(event):
    x1, y1 = (event.x - 1), (event.y - 1)
    x2, y2 = (event.x + 1), (event.y + 1)
    canvas.create_oval(x1, y1, x2, y2, fill=color.get())

def clear_canvas():
    canvas.delete("all")

root = tk.Tk()
root.title("Drawing Pad")

canvas = tk.Canvas(root, width=500, height=400, bg="white")
canvas.pack(fill=tk.BOTH, expand=True)

color = tk.StringVar(value="black")

color_frame = tk.Frame(root)
color_frame.pack(side=tk.BOTTOM)

colors = ["black", "red", "green", "blue"]
for c in colors:
    tk.Button(color_frame, bg=c, width=2, command=lambda col=c: color.set(col)).pack(side=tk.LEFT)

clear_button = tk.Button(root, text="Clear", command=clear_canvas)
clear_button.pack(side=tk.BOTTOM)

canvas.bind("<B1-Motion>", draw)

root.mainloop()
