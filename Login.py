import tkinter
from tkinter import messagebox

def validate_login():
    userid = username_entry.get()
    password = password_entry.get()

    if userid == "admin" and password == "password":
        messagebox.showinfo("Login Successful", "Welcome, Admin!")

    else:
        messagebox.showerror("Login Failed", "Invalid username or password")

parent = tkinter.Tk()
parent.title("Login Form")

username_label = tkinter.Label(parent, text="Userid:")
username_label.pack()

username_entry = tkinter.Entry(parent)
username_entry.pack()

password_label = tkinter.Label(parent, text="Password:")
password_label.pack()

password_entry = tkinter.Entry(parent, show="*")
password_entry.pack()

login_button = tkinter.Button(parent, text="Login", command=validate_login)
login_button.pack()

parent.mainloop()