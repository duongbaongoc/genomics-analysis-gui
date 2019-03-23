#######libraries for the interface
from tkinter import *
from tkinter import messagebox
from tkinter.filedialog import askopenfilename, askdirectory
import os
import sys #exit()
#######libraries to connect to a remote server
import paramiko
import time

#global variables
width = 600
height = 600
wdir = "Click here to open directory dialog"
keyfile = "Click here to open file dialog"
n_process = 24
percentage = 1.0
root = None
labelfont = ('times', 12, 'bold')
cursor_img = "heart"

previous_wdir = "/"
previous_keyfile = "/"
ip = ""
username = ""
password = ""
ssh = None


########################################
######connect to a server###############
def connect_to_server():
        global ssh
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=ip,username=username,password=password)
            return True
        except paramiko.AuthenticationException:
            messagebox.showerror("Error", "Failed to connect to %s due to wrong username/password" %ip)
            return False
        except:
            messagebox.showerror("Error", "Failed to connect to %s" %ip)
            return False
            
        
#################################################
######run the analysis in the server#############
def retrieve_previous_configs(): #save to/retrieve from configs.txt
	global ip
	global username
	global password
	global previous_wdir
	global previous_keyfile
	
	if (os.path.exists("configs.txt") and os.path.isfile("configs.txt") and os.path.getsize("configs.txt")>0):
		infile = open("configs.txt", 'r')
		ip = infile.readline().rstrip().split(":")[1]
		username = infile.readline().rstrip().split(":")[1]
		password = infile.readline().rstrip().split(":")[1]
		previous_wdir = infile.readline().rstrip().split(":")[1]
		previous_keyfile = os.path.dirname(infile.readline().rstrip().split(":")[1])
		infile.close()
	else: #create the file
		file = open("configs.txt", 'w')
		file.close()

def save_previous_configs(): #save to/retrieve from configs.txt
	outfile = open("configs.txt", 'w')
	outfile.write("ip:" + ip + "\n")
	outfile.write("username:" + username + "\n")
	outfile.write("password:" + password + "\n")
	outfile.write("wdir:" + wdir + "\n")
	outfile.write("keyfile:" + keyfile + "\n")
	outfile.close()

def run_analysis(wdir, keyfile, n_process):
    #check if all parameters are chosen
    if (ip == ""):
        messagebox.showerror("Error", "Please enter the server IP")
        return
    if (username == ""):
        messagebox.showerror("Error", "Please enter the server username")
        return
    if (password == ""):
        messagebox.showerror("Error", "Please enter the server password")
        return
    if (wdir == "Click here to open directory dialog"):
        messagebox.showerror("Error", "Choose a folder to analyze")
        return
    if (keyfile == "Click here to open file dialog"):
        messagebox.showerror("Error", "Choose a key file")
        return
	
    #connect to server
    if (connect_to_server() == False):
            return
        
    save_previous_configs()
	
    #run analysis
    try:
        #create a folder A in TAScli to store the wdir and the keyfile
        folder_name = str(time.time())
        stdin, stdout, stderr = ssh.exec_command("mkdir -m 777 /home/seq_user/TAScli/" + folder_name)
        messagebox.showinfo("Info", "The analysis on " + wdir + " using the key file " + keyfile + " is abou to run.\nThe program will not be responding. DO NOT CLOSE THE PROGRAM until you are notified that the analysis is complete.\nClick OK to run.")
      
        #move the wdir and the keyfile from this machine to the server
        fail = os.system("pscp -pw " + password + " -r " + wdir + " " + username + "@" + ip + ":/home/seq_user/TAScli/" + folder_name)
        if fail:
                print("Error: Failed to copy " + wdir + " to the server.")
                return
        fail = os.system("pscp -pw " + password + " " + keyfile + " " + username + "@" + ip + ":/home/seq_user/TAScli/" + folder_name)
        if fail:
                print("Error: Failed to copy " + keyfile + " to the server.")
                return
        #run the anaylysis on the server
        if (percentage == 1.0):
                stdin, stdout, stderr = ssh.exec_command("cd TAScli; perl TAScli.pl " + folder_name + "/" + os.path.basename(wdir) + " " + folder_name + "/" + os.path.basename(keyfile) + " " + str(n_process) + " 1.0")
        else: #95%
                stdin, stdout, stderr = ssh.exec_command("cd TAScli; perl TASapprox.pl " + folder_name + "/" + os.path.basename(wdir) + " " + folder_name + "/" + os.path.basename(keyfile) + " " + str(n_process) + " 0.95")
        
        exit_status = stdout.channel.recv_exit_status()          # Blocking call
        if exit_status != 0:
            print("Error", exit_status)
        		
        #copy result  files from the server to this machine
        if os.path.exists(wdir + "/Analysis"):	
            os.rename(wdir + "/Analysis", wdir + "/Analysis_pre_modified_at_" + str(os.path.getmtime(wdir + "/Analysis")))
        os.mkdir(wdir + "/Analysis")
        os.system("pscp -pw " + password + " " + username + "@" + ip + ":/home/seq_user/TAScli/" + folder_name + "/" + os.path.basename(wdir) + "/Analysis/* " + wdir + "/Analysis")
        
        outfile = open(wdir + "/Analysis/how_to_open_files.txt", 'w')
        outfile.write("Open hitcount.txt, HitCounts.lst, snpreport.txt, or SNPreport.lst using Excel for best readability.")
        outfile.close()
		
        #clean up folders in the server
        stdin, stdout, stderr = ssh.exec_command("rm -r TAScli/" + folder_name) 
        exit_status = stdout.channel.recv_exit_status()          # Blocking call
        if exit_status == 0:
            messagebox.showinfo("Info", "The analysis on " + wdir + "using the key file " + keyfile + " is complete.\nThe result files are stored in " + wdir + "/Analysis.\nYou are safe to close the program.")
        else:
            print("Error", exit_status)
        

    except Exception as e:
        print ("Error: a command can not be executed from the server")
        print (e.message)
        err = ''.join(stderr.readlines())
        out = ''.join(stdout.readlines())
        final_output = str(out)+str(err)

	
#####################################
######user interface#################
    
def get_wdir():
    global wdir
    filename = askdirectory(initialdir = previous_wdir,title = "Select directory")
    if (filename != ""):
        wdir = filename
        
def get_keyfile():
    global keyfile
    filename = askopenfilename(initialdir = previous_keyfile,title = "Select file",filetypes =[("all files","*.*")])
    if (filename != ""):
        keyfile = filename
        
def create_label(text, n): #n = 0,1,2,3...
        label = Label(text = text)
        label.configure(font=labelfont)
        label.pack()
        label.place(x=30, y=70+50*n)
    
class Window(Frame):


    def __init__(self, master=None):
        Frame.__init__(self, master)                 
        self.master = master
        self.init_window()

    #Creation of init_window
    def init_window(self):

        # changing the title of our master widget      
        self.master.title("What title should go here?")

        # allowing the widget to take the full space of the root window
        self.pack(fill=BOTH, expand=1)

        # creating a input field to prompt server ip
        create_label("Server IP:", 1)

        def get_ip(v):
                global ip
                ip = v.get()
        
        ipVar = StringVar()
        ipVar.trace("w", lambda name, index, mode, sv=ipVar: get_ip(sv))
        ipPrompt = Entry(self, textvariable=ipVar, font=labelfont)
        ipPrompt.insert(END, ip)
        ipPrompt.pack()
        ipPrompt.place(x=300, y=70+50*1, width=200)
        
        # creating a input field to prompt username
        create_label("Server Username:",2)
        
        def get_username(v):
                global username
                username = v.get()
        
        usernameVar = StringVar()
        usernameVar.trace("w", lambda name, index, mode, sv=usernameVar: get_username(sv))
        usernamePrompt = Entry(self, textvariable=usernameVar, font=labelfont)
        usernamePrompt.insert(END, username)
        usernamePrompt.pack()
        usernamePrompt.place(x=300, y=70+50*2, width=200)

        # creating a input field to prompt password
        create_label("Server Password:", 3)
        
        def get_password(v):
                global password
                password = v.get()
        
        passwordVar = StringVar()
        passwordVar.trace("w", lambda name, index, mode, sv=passwordVar: get_password(sv))
        passwordPrompt = Entry(self, textvariable=passwordVar, font=labelfont, show="*")
        passwordPrompt.insert(END, password)
        passwordPrompt.pack()
        passwordPrompt.place(x=300, y=70+50*3, width=200)

        # creating a button to get wdir
        create_label("Choose the folder to analyze:",5)
        wdirButtonText = StringVar()

        def master_get_wdir():
            get_wdir()
            wdirButtonText.set(wdir)
        
        wdirButton = Button(self, textvariable=wdirButtonText, command=master_get_wdir, cursor = cursor_img, font=labelfont)
        wdirButton.place(x=300, y=70+50*5)
        wdirButtonText.set("Click here to open directory dialog")

        # creating a button to get keyfile
        create_label("Choose the key file:", 6)
        keyfileButtonText = StringVar()

        def master_get_keyfile():
            get_keyfile()
            keyfileButtonText.set(keyfile)
        
        keyfileButton = Button(self, textvariable=keyfileButtonText, command=master_get_keyfile, cursor = cursor_img, font=labelfont)
        keyfileButton.place(x=300, y=70+50*6)
        keyfileButtonText.set("Click here to open file dialog")

        # creating a dropdown to get number of processes (1-32)
        create_label("Choose the number of processes:",7)
        
        options = [i for i in range(1,33)]
        n_process_dropdown_var = StringVar()
        n_process_dropdown_var.set(24) #default
        n_process_dropdown = OptionMenu(root, n_process_dropdown_var, *options)
        n_process_dropdown.configure(cursor=cursor_img, font=labelfont)
        n_process_dropdown.pack()
        n_process_dropdown.place(x=300, y=70+50*7)

        def get_n_process(*args):
            global n_process
            n_process = n_process_dropdown_var.get()
    
        n_process_dropdown_var.trace('w', get_n_process)

        # creating a radiobutton to choose 100% or 95%
        create_label("Minumim percentage of similarity:",8)
        var = IntVar()
        var.set(1.0)
        def sel():
                global percentage
                percentage = var.get()
                
        R1 = Radiobutton(root, text="95%", variable=var, value=0.95, command=sel, font=labelfont)
        R1.pack()
        R1.place(x=300, y=70+50*8)
        R2 = Radiobutton(root, text="100%", variable=var, value=1.0, command=sel, font=labelfont)
        R2.pack()
        R2.place(x=400, y=70+50*8)
        
        # creating a button to run the analysis
        runButton = Button(self, text="Run", command=lambda: run_analysis(wdir, keyfile, n_process), cursor = cursor_img)
        runButton.place(x=width/2-5, y=70+50*8 + 80)
        runButton.config(bg="green2", font=labelfont)
		
		
if __name__ == "__main__":
        retrieve_previous_configs() 
        root = Tk()
        #position the window in the center
        root.geometry(str(width) + "x" + str(height))
        app = Window(root)
        root.mainloop()

