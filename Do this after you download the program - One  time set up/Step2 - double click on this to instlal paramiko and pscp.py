import os
from tkinter import *
from tkinter import messagebox


root = Tk()
root.withdraw()


failure = os.system("pip install paramiko")
if (failure):
	messagebox.showerror("Error", "Failed to install paramiko")


failure = os.system("python -m pip install pscp")
if (failure):
	messagebox.showerror("Error", "Failed to install pscp")
	
	
messagebox.showinfo("Congrats!", "Successfully installed all dependencies (Python, paramiko, pscp)")
