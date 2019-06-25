#######libraries for the interface
from tkinter import *
from tkinter import messagebox
from tkinter.ttk import Combobox
from tkinter.filedialog import askopenfilename, askdirectory
import os
import sys #exit()
#######libraries to connect to a remote server
import paramiko
import time
import warnings
warnings.filterwarnings("ignore")

#global variables
width = 500
height = 350
wdir = "Open directory dialog"
keyfile = "Open file dialog"
n_process = 24 #chosen number of cores to run
n_avail_cores = 0
n_nodes = 2 #96-core
percentage = 1.0
het_percentage = 0.20
hit_count = 5
is_saved = 1 #0==no, 1==yes <= want to save the server info in this computer?
root = None
app = None
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
        global n_avail_cores
        global app
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
        #connecting
        try:
            ssh = paramiko.SSHClient() 
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=ip,username=username,password=password)
        except paramiko.AuthenticationException:
            messagebox.showerror("Error", "Failed to connect to %s due to wrong username/password" %ip)
            return
        except:
            messagebox.showerror("Error", "Failed to connect to %s" %ip)
            return
        #when connected:
        if (is_saved): #if users choose to save, we save the last connected server
            save_previous_configs()
        else: #if users choose not to save, we delete all saved server
            if os.path.exists("configs.txt"):
                    os.remove("configs.txt")
            
        get_number_of_avail_cores()
        app.destroy()
        root.geometry(str(width - 30) + "x" + str(height + 130))
        app = Window2(root)
        

#################################################
######run the analysis in the server#############
def retrieve_previous_configs(): #save to/retrieve from configs.txt
	global ip
	global username
	global password
	
	if (os.path.exists("configs.txt") and os.path.isfile("configs.txt") and os.path.getsize("configs.txt")>0):
		infile = open("configs.txt", 'r')
		ip = infile.readline().rstrip().split(":")[1]
		username = infile.readline().rstrip().split(":")[1]
		password = infile.readline().rstrip().split(":")[1]
		infile.close()
	else: #create the file
		file = open("configs.txt", 'w')
		file.close()

def save_previous_configs(): #save to/retrieve from configs.txt
	outfile = open("configs.txt", 'w')
	outfile.write("ip:" + ip + "\n")
	outfile.write("username:" + username + "\n")
	outfile.write("password:" + password + "\n")
	outfile.close()

def retrieve_previous_dirs(): #save to/retrieve from dirs.txt
	global previous_wdir
	global previous_keyfile
	
	if (os.path.exists("dirs.txt") and os.path.isfile("dirs.txt") and os.path.getsize("dirs.txt")>0):
		infile = open("dirs.txt", 'r')
		previous_wdir = infile.readline().rstrip().split(":")[1]
		previous_keyfile = os.path.dirname(infile.readline().rstrip().split(":")[1])
		infile.close()
	else: #create the file
		file = open("dirs.txt", 'w')
		file.close()

def save_previous_dirs(): #save to/retrieve from configs.txt
	outfile = open("dirs.txt", 'w')
	outfile.write("wdir:" + wdir + "\n")
	outfile.write("keyfile:" + keyfile + "\n")
	outfile.close()
	
def reset(): #reset the program
        global width
        global height
        global wdir
        global keyfile
        global n_process
        global n_avail_cores
        global n_nodes
        global percentage
        global het_percentage
        global hit_count
        global is_saved
        global root
        global app
        global ssh
        #reset global variables
        width = 500
        height = 350
        wdir = "Open directory dialog"
        keyfile = "Open file dialog"
        n_process = 24 #chosen number of cores to run
        n_avail_cores = 0
        n_nodes = 2 #96-core
        percentage = 1.0
        het_percentage = 0.20
        hit_count = 5
        is_saved = 1 #0==no, 1==yes <= want to save the server info in this computer?
        ssh = None
        #reset window        
        app.destroy()
        root.geometry(str(width) + "x" + str(height))
        app = Window1(root)
        
        
def run_32(wdir, keyfile, n_process):
    #check if all parameters are chosen
    if (wdir == "Open directory dialog"):
        messagebox.showerror("Error", "Choose a folder to analyze")
        return
    if (keyfile == "Open file dialog"):
        messagebox.showerror("Error", "Choose a key file")
        return

    save_previous_dirs()
    
    #run analysis
    try:
        #create a folder A in TAScli to store the wdir and the keyfile
        folder_name = str(time.time())
        stdin, stdout, stderr = ssh.exec_command("mkdir -m 777 /home/seq_user/TAScli/" + folder_name)
        messagebox.showinfo("Info", "The analysis is about to run.\nThe program will freeze. DO NOT CLOSE THE PROGRAM until it says the analysis is complete.")
      
        #move the wdir and the keyfile from this machine to the server
        fail = os.system("pscp -pw " + password + " -r " + wdir + " " + username + "@" + ip + ":/home/seq_user/TAScli/" + folder_name)
        if fail:
                print("Error: Failed to copy " + wdir + " to the server.")
                return
        fail = os.system("pscp -pw " + password + " " + keyfile + " " + username + "@" + ip + ":/home/seq_user/TAScli/" + folder_name)
        if fail:
                print("Error: Failed to copy " + keyfile + " to the server.")
                return

        #run the analysis on the server
        command ="cd TAScli; python TAScli.py " + folder_name + "/" + os.path.basename(wdir) + " " + folder_name + "/" + os.path.basename(keyfile) + " " + str(n_process) + " " + str(percentage) + " " + str(het_percentage) + " " + str(hit_count)
        print (command)
        stdin, stdout, stderr = ssh.exec_command(command)
        ###Start checking the progress
        time.sleep(30)
        stdin, stdout0, stderr = ssh.exec_command("cd TAScli/" + folder_name + "/" + os.path.basename(wdir) + "/" + "Analysis/Markers; ls | wc -l")
        stdout0 = int(str(stdout0.read())[2:-3])
        time.sleep(20)
        stdin, stdout1, stderr = ssh.exec_command("cd TAScli/" + folder_name + "/" + os.path.basename(wdir) + "/" + "Analysis/Markers; ls | wc -l")
        stdout1 = int(str(stdout1.read())[2:-3])
        while (stdout1 != stdout0):
                stdout0 = stdout1
                time.sleep(20)
                stdin, stdout1, stderr = ssh.exec_command("cd TAScli/" + folder_name + "/" + os.path.basename(wdir) + "/" + "Analysis/Markers; ls | wc -l")
                stdout1 = int(str(stdout1.read())[2:-3])
        stdin, stdout, stderr = ssh.exec_command("cd TAScli; cat " + folder_name + "/" + os.path.basename(keyfile) + "| wc -l")
        expected_num_files_Markers = int(str(stdout.read())[2:-3]) / 2
        if (stdout0 != expected_num_files_Markers):
                messagebox.showinfo("IMPORTANT", "The GUI is encountering a problem. It will close after you click OK. The analyzis is still running just fine. The result files will not be downloaded to this computer but will locate in the 32-core server in folder " + folder_name + "/" + os.path.basename(wdir))
                sys.exit()
        ##End checing the progess
        exit_status = stdout.channel.recv_exit_status()          # Blocking call
        if exit_status != 0:
            print("Error", exit_status, "faied to run", command)       

        #copy result files from the server to this machine
        if os.path.exists(wdir + "/Analysis"):	
            os.rename(wdir + "/Analysis", wdir + "/Analysis_pre_modified_at_" + str(os.path.getmtime(wdir + "/Analysis")))
        os.mkdir(wdir + "/Analysis")
        os.system("pscp -pw " + password + " " + username + "@" + ip + ":/home/seq_user/TAScli/" + folder_name + "/" + os.path.basename(wdir) + "/Analysis/* " + wdir + "/Analysis")
		
        #clean up folders in the server
        stdin, stdout, stderr = ssh.exec_command("rm -r TAScli/" + folder_name) 
        exit_status = stdout.channel.recv_exit_status()          # Blocking call
        if exit_status == 0:
            reset() #reset the program
            messagebox.showinfo("Info", "The analysis is complete.\nThe results are saved in " + wdir + "/Analysis.")
        else:
            print("Error", exit_status)
    except Exception as e:
        print ("Error: a command can not be executed from the server")
        print (e.message)
        err = ''.join(stderr.readlines())
        out = ''.join(stdout.readlines())
        final_output = str(out)+str(err)

        
def run_96(wdir, keyfile, n_nodes):
    #check if all parameters are chosen
    if (wdir == "Open directory dialog"):
        messagebox.showerror("Error", "Choose a folder to analyze")
        return
    if (keyfile == "Open file dialog"):
        messagebox.showerror("Error", "Choose a key file")
        return

    save_previous_dirs()
    
    #run analysis
    try:
        #create a folder A in TAS to store the wdir and the keyfile
        folder_name = str(time.time())
        stdin, stdout, stderr = ssh.exec_command("mkdir -m 777 /home/wrsggl/TAS/" + folder_name)
        messagebox.showinfo("Info", "The analysis is about to run.\nThe program will freeze. DO NOT CLOSE THE PROGRAM until it says the analysis is complete.")
        
        #move the wdir and the keyfile from this machine to the server
        fail = os.system("pscp -pw " + password + " -r " + wdir + " " + username + "@" + ip + ":/home/wrsggl/TAS/" + folder_name)
        if fail:
                print("Error: Failed to copy " + wdir + " to the server.")
                return
        fail = os.system("pscp -pw " + password + " " + keyfile + " " + username + "@" + ip + ":/home/wrsggl/TAS/" + folder_name)
        if fail:
                print("Error: Failed to copy " + keyfile + " to the server.")
                return
        
        #run the analysis on the server
        command = "cd TAS; python TAScli.py " + folder_name + "/" + os.path.basename(wdir) + " " + folder_name + "/" + os.path.basename(keyfile) + " " + str(n_nodes) + " " + str(percentage)
        print (command)
        stdin, stdout, stderr = ssh.exec_command(command)
        exit_status = stdout.channel.recv_exit_status()          # Blocking call
        if exit_status != 0:
            print("Error", exit_status, "faied to run", command)
            
        #wait until the slurm job finishes
        stdin, stdout, stderr = ssh.exec_command("squeue")
        while ("pro366" in str(stdout.read())):
                stdin, stdout, stderr = ssh.exec_command("squeue")
        
        #copy result files from the server to this machine
        if os.path.exists(wdir + "/Analysis"):	
            os.rename(wdir + "/Analysis", wdir + "/Analysis_pre_modified_at_" + str(os.path.getmtime(wdir + "/Analysis")))
        os.mkdir(wdir + "/Analysis")
        os.system("pscp -pw " + password + " " + username + "@" + ip + ":/home/wrsggl/TAS/" + folder_name + "/" + os.path.basename(wdir) + "/Analysis/* " + wdir + "/Analysis")
		
        #clean up folders in the server
        stdin, stdout, stderr = ssh.exec_command("rm -r TAS/" + folder_name) 
        exit_status = stdout.channel.recv_exit_status()          # Blocking call
        if exit_status == 0:
            reset() #reset the program
            messagebox.showinfo("Info", "The analysis is complete.\nThe results are saved in " + wdir + "/Analysis.")
        else:
            print("Error", exit_status)
        
    except Exception as e:
        print ("Error: a command can not be executed from the server")
        print (e.message)
        err = ''.join(stderr.readlines())
        out = ''.join(stdout.readlines())
        final_output = str(out)+str(err)
        

#####################################
######get number of available cores##
#Note: this is method may not result in the exact number of available cores
# because what cores are running or idling can change within a split of second
def get_number_of_avail_cores():
        global n_avail_cores
        #get the total number of cores
        stdin, stdout, stderr = ssh.exec_command("lscpu")
        exit_status = stdout.channel.recv_exit_status()          # Blocking call
        total_cpus = int(str(stdout.read()).split("\\n")[3].split(" ")[-1])
        #get number of avail cores
        set_running_cores = set()
        stdin, stdout, stderr = ssh.exec_command("top -i -b -n1")
        exit_status = stdout.channel.recv_exit_status()          # Blocking call
        lines = str(stdout.read()).split("\\n")
        pids = [line.lstrip().split(" ")[0] for line in lines[7:-2]]
        command = "ps -o pid,psr,comm -p"
        for pid in pids:
                command += " " + pid
        stdin, stdout, stderr = ssh.exec_command(command)
        exit_status = stdout.channel.recv_exit_status()          # Blocking call
        pid_cpu_task_s = str(stdout.read()).split("\\n")
        if (len(pid_cpu_task_s) > 2):
                for line in pid_cpu_task_s[1:-1]:
                    cpu = int(line.split(" ")[-2])
                    set_running_cores.add(cpu)
        n_running = len(set_running_cores)
        n_avail_cores = total_cpus - n_running

        
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
        
def create_label(frame, text, n, indent, color): #n = 0,1,2,3...
        label = Label(frame, text = text)
        label.configure(font=labelfont, bg = color)
        label.pack()
        label.place(x=30 + indent*10, y=50*n)


class Window1(Frame): #to connect to server


    def __init__(self, master=None):
        Frame.__init__(self, master)                 
        self.master = master
        self.init_window()

    #Creation of init_window
    def init_window(self):
        # changing the title of our master widget      
        self.master.title("GMS: Analyze Data")

        # allowing the widget to take the full space of the root window
        self.pack(fill=BOTH, expand=1)

        #frame
        top_frame = Frame(self, bg='LavenderBlush2', width = width, height = 250).grid(row = 0, columnspan = 1)
        
        # creating a input field to prompt server ip
        create_label(top_frame, "Server IP:", 1,0, 'LavenderBlush2')

        def get_ip(v):
                global ip
                ip = v.get()
        
        ipVar = StringVar()
        ipVar.trace("w", lambda name, index, mode, sv=ipVar: get_ip(sv))
        ipPrompt = Entry(top_frame, textvariable=ipVar, font=labelfont)
        ipPrompt.insert(END, ip)
        ipPrompt.pack()
        ipPrompt.place(x=200, y=50*1, width=200)
        
        # creating a input field to prompt username
        create_label(top_frame, "Server Username:",2,0, 'LavenderBlush2')
        
        def get_username(v):
                global username
                username = v.get()
        
        usernameVar = StringVar()
        usernameVar.trace("w", lambda name, index, mode, sv=usernameVar: get_username(sv))
        usernamePrompt = Entry(top_frame, textvariable=usernameVar, font=labelfont)
        usernamePrompt.insert(END, username)
        usernamePrompt.pack()
        usernamePrompt.place(x=200, y=50*2, width=200)

        # creating a input field to prompt password
        create_label(top_frame, "Server Password:", 3,0, 'LavenderBlush2')
        
        def get_password(v):
                global password
                password = v.get()
        
        passwordVar = StringVar()
        passwordVar.trace("w", lambda name, index, mode, sv=passwordVar: get_password(sv))
        passwordPrompt = Entry(top_frame, textvariable=passwordVar, font=labelfont, show="*")
        passwordPrompt.insert(END, password)
        passwordPrompt.pack()
        passwordPrompt.place(x=200, y=50*3, width=200)

        # creating a radiobutton to choose save credentials or not
        create_label(top_frame, "Save the server info?",4,0, 'LavenderBlush2')
        def display_help():
                messagebox.showinfo("Info", "If choose 'yes' and the server is connected, the program will remember this server info for next time use.\n If choose 'no' and the server is connected, all server info ever saved by this program in this computer will be deleted.")
                
        helpButton = Button(top_frame, text="?", font=labelfont, command = display_help)
        helpButton["bg"] = "yellow"
        helpButton.pack()
        helpButton.place(x=400, y=50*4)
        
        var = IntVar()
        var.set(1)
        def sel():
                global is_saved
                is_saved = var.get()
                
        R1 = Radiobutton(root, text="Yes", variable=var, value=1, command=sel, font=labelfont)
        R1.configure(bg = 'LavenderBlush2')
        R1.pack()
        R1.place(x=200, y=50*4)
        R2 = Radiobutton(root, text="No", variable=var, value=0, command=sel, font=labelfont)
        R2.configure(bg = 'LavenderBlush2')
        R2.pack()
        R2.place(x=300, y=50*4)

        #frame
        bottom_frame = Frame(self, bg='light blue', width = width, height = 200).grid(row = 1, columnspan = 1)
        
        # creating a button to connect to the server
        connectButton = Button(bottom_frame, text="Connect", command = connect_to_server)
        connectButton.place(x=200, y=50*4 + 80)
        connectButton.config(bg="ghost white", font=labelfont)


class Window2(Frame): #to run the analysis

    def __init__(self, master=None):
        Frame.__init__(self, master)                 
        self.master = master
        self.init_window()

    #Creation of init_window
    def init_window(self):
        # changing the title of our master widget      
        self.master.title("GMS: Analyze Data")

        # allowing the widget to take the full space of the root window
        self.pack(fill=BOTH, expand=1)

        #frame
        top_frame = Frame(self, bg='thistle2', width = width, height = 240).grid(row = 0, columnspan = 1)
        
        # creating a button to get wdir
        create_label(top_frame, "Folder of data:",1,0, 'thistle2')
        wdirButtonText = StringVar()

        def master_get_wdir():
            get_wdir()
            wdirButtonText.set(wdir)
        
        wdirButton = Button(self, textvariable=wdirButtonText, command=master_get_wdir, cursor = cursor_img, font=labelfont)
        wdirButton.place(x=200, y=50*1)
        wdirButtonText.set("Open directory dialog")

        # creating a button to get keyfile
        create_label(top_frame, "Key file:", 2,0, 'thistle2')
        keyfileButtonText = StringVar()

        def master_get_keyfile():
            get_keyfile()
            keyfileButtonText.set(keyfile)
        
        keyfileButton = Button(self, textvariable=keyfileButtonText, command=master_get_keyfile, cursor = cursor_img, font=labelfont)
        keyfileButton.place(x=200, y=50*2)
        keyfileButtonText.set("Open file dialog")

        if (username == "seq_user"): #32-core server
                # creating a slide to get number of processes
                create_label(top_frame, "Number of processes:",3,0, 'thistle2')
                var0 = IntVar()
                var0.set(24)
                def get_n_process(val):
                        global n_process
                        n_process = val
                        
                S0 = Scale(root, from_=1, to=n_avail_cores, resolution=1, variable=var0, showvalue=24, command=get_n_process, font=labelfont, orient=HORIZONTAL, length = 200)
                S0.configure(bg = 'thistle2', highlightbackground = 'thistle2')
                S0.pack()
                S0.place(x=200, y=50*3-10)
        else: #96-core server
                # creating a slide to get number of nodes
                create_label(top_frame, "Number of nodes:",3,0, 'thistle2')
                var0 = IntVar()
                var0.set(2)
                def get_n_nodes(val):
                        global n_nodes
                        n_nodes = val
                        
                S0 = Scale(root, from_=2, to=4, resolution=1, variable=var0, showvalue=2, command=get_n_nodes, font=labelfont, orient=HORIZONTAL, length = 200)
                S0.configure(bg = 'thistle2', highlightbackground = 'thistle2')
                S0.pack()
                S0.place(x=200, y=50*3-10)
        # creating a slider (scale) for min sim
        create_label(top_frame, "Similarity (%):",4,0, 'thistle2')
        var1 = DoubleVar()
        var1.set(100)
        def sel(val):
                global percentage
                percentage = int(val)/100.0
                
        S1 = Scale(root, from_=0, to=100, resolution=1, variable=var1, showvalue=100, command=sel, font=labelfont, orient=HORIZONTAL, length = 200)
        S1.configure(bg = 'thistle2', highlightbackground = 'thistle2')
        S1.pack()
        S1.place(x=200, y=50*4-10)
        
        #frame
        middle_frame = Frame(self, bg='wheat', width = width, height = 150).grid(row = 1, columnspan = 1)
        if (username == "seq_user"): #32-core server; this is temporary because 96-core programs do not have filter
                #text: heterozygotes
                create_label(middle_frame, "HETEROZYGOTES filter:",5,0, 'wheat')
                
                #creating a scale to choose het percentage to filter
                create_label(middle_frame, "Percentage (%):",6,3, 'wheat')
                var2 = DoubleVar()
                var2.set(20)
                def het(val):
                        global het_percentage
                        het_percentage = int(val)/100.0
                        
                S2 = Scale(root, from_=0, to=100, resolution=1, variable=var2, showvalue=20, command=het, font=labelfont, orient=HORIZONTAL, length = 200)
                S2.configure(bg = 'wheat', highlightbackground = 'wheat')
                S2.pack()
                S2.place(x=200, y=50*6-10)
                
                #creating a scale to choose min hit-count to filter
                create_label(middle_frame, "Min. hit counts:",7,3, 'wheat')
                var3 = DoubleVar()
                var3.set(5)
                def hitcount(val):
                        global hit_count
                        hit_count = int(val)
                        
                S3 = Scale(root, from_=0, to=100, resolution=1, variable=var3, showvalue=5, command=hitcount, font=labelfont, orient=HORIZONTAL, length = 200)
                S3.configure(bg = 'wheat', highlightbackground = 'wheat')
                S3.pack()
                S3.place(x=200, y=50*7-10)      
        else: #96-core server; this is temporary because 96-core programs do not have filter
                create_label(middle_frame, "**This server does not support to filter snip report**",5,1, 'wheat')
        #frame
        bottom_frame = Frame(self, bg='light blue', width = width, height = 200).grid(row = 2, columnspan = 1)
        
        # creating a button to run the analysis
        if (username == "seq_user"): #32-core server
                runButton = Button(self, text="Run", command=lambda: run_32(wdir, keyfile, n_process), cursor = cursor_img)
        else: #96-core server
                runButton = Button(self, text="Run", command=lambda: run_96(wdir, keyfile, n_nodes), cursor = cursor_img)
        runButton.place(x=width/2-25, y=70+50*6 + 50)
        runButton.config(bg="ghost white", font=labelfont)
        
		
if __name__ == "__main__":
        retrieve_previous_configs()
        retrieve_previous_dirs() 
        root = Tk()
        #position the window in the center
        root.geometry(str(width) + "x" + str(height))
        app = Window1(root)
        root.mainloop()

