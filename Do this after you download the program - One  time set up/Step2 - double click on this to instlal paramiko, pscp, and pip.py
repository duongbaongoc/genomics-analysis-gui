import os
from tkinter import *
from tkinter import messagebox


root = Tk()
root.withdraw()


#pip
failure = os.system("python get-pip.py")
if (failure):
	messagebox.showerror("Error", "Failed to install pip")
	exit()


#paramiko
failure = os.system("pip install paramiko")
if (failure):
	messagebox.showerror("Error", "Failed to install paramiko")
	exit()


#pscp
failure = os.system("python -m pip install pscp")
if (failure):
	messagebox.showerror("Error", "Failed to install pscp")
	exit()

#pandas
failure = os.system("python -m pip install pandas")
if (failure):
	messagebox.showerror("Error", "Failed to install pandas")
	exit()
	
	
messagebox.showinfo("Congrats!", "Successfully installed all dependencies (Python, paramiko, pscp)")
