#######libraries for the interface
from tkinter import *
from tkinter import messagebox
from tkinter.ttk import Combobox
from tkinter.filedialog import askopenfilename, askdirectory
import os
import sys #exit()
import time
import shutil
import paramiko #server
import pandas as pd #manipulate csv files
from shlex import quote #escape shell quotes

'''
This program prepares data for analysis by transfer data from the proton server to the pgm server and create a final data folder on desktop of this computer.
'''

#global variables
width = 500
height = 430
labelfont = ('times', 12, 'bold')
cursor_img = "heart"
password_proton = ""
password_pgm = ""
is_saved = 1 #0==no, 1==yes <= want to save the server info in this computer?
ssh = None
wdir = "Open directory dialog" #the job folder
previous_wdir = ""

########################################
######connect to a server###############
def connect_to_server(ip, username, password):
        global ssh
        try:
            ssh = paramiko.SSHClient() 
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=ip,username=username,password=password)
        except paramiko.AuthenticationException:
            messagebox.showerror("Error", "Failed to connect to %s due to wrong username/password" %ip)
            return False
        except:
            messagebox.showerror("Error", "Failed to connect to %s" %ip)
            return False
        return True

######################################################################################
######transfer data to pgm server and make a data folder in this computer#############
def retrieve_previous_dirs(): #save to/retrieve from dirs.txt
	global previous_wdir
	
	if (os.path.exists("dir.txt") and os.path.isfile("dir.txt") and os.path.getsize("dir.txt")>0):
		infile = open("dir.txt", 'r')
		previous_wdir = infile.readline().rstrip().split(":")[1]
		infile.close()
	else: #create the file
		file = open("dir.txt", 'w')
		file.close()

def save_previous_dirs(): #save to/retrieve from configs.txt
	outfile = open("dir.txt", 'w')
	outfile.write("wdir:" + wdir + "\n")
	outfile.close()
	
def retrieve_previous_configs(): #save to/retrieve from configs.txt
	global password_proton
	global password_pgm
	
	if (os.path.exists("configs1.txt") and os.path.isfile("configs1.txt") and os.path.getsize("configs1.txt")>0):
		infile = open("configs1.txt", 'r')
		password_proton = infile.readline().rstrip().split(":")[1]
		password_pgm = infile.readline().rstrip().split(":")[1]
		infile.close()
	else: #create the file
		file = open("configs1.txt", 'w')
		file.close()

def save_previous_configs(): #save to/retrieve from configs.txt
	outfile = open("configs1.txt", 'w')
	outfile.write("password_proton:" + password_proton + "\n")
	outfile.write("password_pgm:" + password_pgm + "\n")
	outfile.close()
       
def run():
        global wdir
        #check if all parameters are chosen
        if (password_proton == ""):
                messagebox.showerror("Error", "Input proton server password")
                return
        if (password_pgm == ""):
                messagebox.showerror("Error", "Input pgm server password")
                return
        if (wdir == "Open directory dialog"):
                messagebox.showerror("Error", "Choose a job folder\nClick on the ? button for more info.")
                return
        save_previous_dirs()
        
        #get a list of PRO numbers
        pro_list = [entry.split('-')[0][3:] for entry in os.listdir(wdir) if entry[:3] == "PRO"]
        pro_list = list(set(pro_list)) #remove duplicats if any
     
        #verify inputs
        connected_proton = connect_to_server("134.121.95.28", "ionadmin", password_proton)
        if (connected_proton == False):
                return

        for pro in pro_list:
                command = "cd /results/analysis/output/Home; ls Auto_user_Proton-" + pro + "*"
                stdin, stdout, stderr = ssh.exec_command(command)
                exit_status = stdout.channel.recv_exit_status()          # Blocking call
                if exit_status != 0:
                        print("Error", exit_status, "faied to run", command)
                        messagebox.showerror("Error", "PRO '" + pro + "' does not exist in the proton server")
                        return
        connected_pgm = connect_to_server("134.121.92.88", "ionadmin", password_pgm)
        if (connected_pgm == False):
                return

        #at this point, the servers are connectable, and the pro numbers are valid
        save_previous_configs()
        messagebox.showinfo("Info", "The program is about to transfer data.\nIt will freeze for awhile. DO NOT CLOSE THE PROGRAM until it says the process is complete.")

        #replace space in basename of wdir for later
        basename = os.path.basename(wdir)
        dirname = os.path.dirname(wdir)
        wdir = dirname + "/" + basename.replace(" ", "-")
        os.rename(dirname + "/" + basename, wdir)
        
        #create a folder in wdir to save the data
        data_path = ""
        if (os.path.exists(wdir + "/data-proton-server")):
                data_path = wdir + "/data-proton-server" + "-" +str(time.time())
        else:
                data_path = wdir + "/data-proton-server"
        os.mkdir(data_path)
        
        #IN THE PROTON SERVER
        connect_to_server("134.121.95.28", "ionadmin", password_proton)
        for pro in pro_list:
                command = "cd /results/analysis/output/Home; ls Auto_user_Proton-" + pro + "*"
                stdin, stdout, stderr = ssh.exec_command(command)
                exit_status = stdout.channel.recv_exit_status()          # Blocking call
                dir_no_tn = str(stdout.read()).split('\n')[0][2:].split(":")[0]
                print(dir_no_tn)
                command = "cd /results/analysis/output/Home/" + dir_no_tn + "/basecaller_results;mkdir PRO" + pro + "bam"
                stdin, stdout, stderr = ssh.exec_command(command)
                exit_status = stdout.channel.recv_exit_status()          # Blocking call
                command = "cd /results/analysis/output/Home/" + dir_no_tn + "/basecaller_results; mv *.bam PRO" + pro + "bam"
                stdin, stdout, stderr = ssh.exec_command(command)
                exit_status = stdout.channel.recv_exit_status()          # Blocking call
                print (stderr)#print ("ok") if exit_status == 0 else print ("failed")
                command = "cd /results/analysis/output/Home/" + dir_no_tn + "/basecaller_results; /results/sshpass -p " + password_pgm + " scp -r PRO" + pro + "bam ionadmin@134.121.92.88:/results/BAMbackup" 
                stdin, stdout, stderr = ssh.exec_command(command)
                exit_status = stdout.channel.recv_exit_status()          # Blocking call
                
                        
        #IN THE PGM SERVER
        connect_to_server("134.121.92.88", "ionadmin", password_pgm)
        for pro in pro_list:
                command = "cd /results/BAMbackup/PRO" + pro + "bam; perl /results/bam2fasta.pl MAS*"
                stdin, stdout, stderr = ssh.exec_command(command)
                exit_status = stdout.channel.recv_exit_status()          # Blocking call
        
        #DOWNLOAD TO THIS COMPUTER
        for pro in pro_list:
                if (os.path.exists(data_path + "/" + pro)):
                        shutil.rmtree(data_path + "/" + pro)
                os.mkdir(data_path + "/" + pro)
                command = "pscp -pw " + password_pgm + " ionadmin@134.121.92.88:/results/BAMbackup/PRO" + pro + "bam/PRO" + pro + "bam/MAS* " + data_path + "/" + pro
                os.system(command)
        
        #IN THIS COMPUTER
        #change file names
        for entry in os.listdir(wdir):
                pro = entry.split("-")[0][3:]
                if pro in pro_list: #entry is one of the PRO file to change name
                        #prepare a dictionary to change name
                        frame= None
                        try:
                                frame = pd.read_csv(wdir + "/" + entry, delimiter = ',')
                        except:
                                messagebox.showerror("Error", "Cannot read " + wdir + "/" + entry + ".\nMake sure the file is in csv format (delimiter is , ).")
                                return
                        index_ = frame['Barcode']
                        frame.index = index_
                        frame = frame[['Sample ID']]
                        #change file names
                        for file in os.listdir(wdir + "/data-proton-server/" + pro):
                                ind = file[:-21]
                                cur_path = wdir + "/data-proton-server/" + pro + "/" + file
                                new_path = wdir + "/data-proton-server/" + pro + "/" + frame.loc[ind, 'Sample ID']
                                os.rename(cur_path, new_path)

        #move files up to direct parent folder, if duplicates, add a time at the end of file name
        for pro in os.listdir(wdir + "/data-proton-server"):
                for file in os.listdir(wdir + "/data-proton-server/" + pro):
                        if (not os.path.exists(wdir + "/data-proton-server/" +  file)):
                                os.rename(wdir + "/data-proton-server/" + pro + "/" + file, wdir + "/data-proton-server/" + file)
                        else:
                                i = 1
                                while (True):
                                        if (not os.path.exists(wdir + "/data-proton-server/" +  file + "_" + str(i))):
                                                os.rename(wdir + "/data-proton-server/" + pro + "/" + file, wdir + "/data-proton-server/" + file + "_" + str(i))
                                                break
                                        i += 1
        #remove the now empty folders
        for pro in pro_list:
                os.rmdir(wdir + "/data-proton-server/" + pro)
        messagebox.showinfo("Done!", "The data is ready for analyze.\nIt is stored in " + wdir + "/data-proton-server.")
        
#####################################
######user interface#################

def get_wdir():
    global wdir
    filename = askdirectory(initialdir = previous_wdir,title = "Select directory")
    if (filename != ""):
        wdir = filename
        
def create_label(frame, text, n, indent, color): #n = 0,1,2,3...
        label = Label(frame, text = text)
        label.configure(font=labelfont, bg = color)
        label.pack()
        label.place(x=30 + indent*10, y=50*n)


class Window1(Frame): #to run the analysis

    def __init__(self, master=None):
        Frame.__init__(self, master)                 
        self.master = master
        self.init_window()

    #Creation of init_window
    def init_window(self):
        # changing the title of our master widget      
        self.master.title("GMS: Prepare Data to Analyze")

        # allowing the widget to take the full space of the root window
        self.pack(fill=BOTH, expand=1)

        #frame
        top_frame = Frame(self, bg='thistle2', width = width, height = 240).grid(row = 0, columnspan = 1)

        create_label(top_frame, "Provide password of", 1,0, 'thistle2')

        # creating a input field to prompt password (proton server)
        create_label(top_frame, "proton server:", 2,5, 'thistle2')
        
        def get_password_proton(v):
                global password_proton
                password_proton = v.get()
        
        passwordVar2 = StringVar()
        passwordVar2.trace("w", lambda name, index, mode, sv=passwordVar2: get_password_proton(sv))
        passwordPrompt2 = Entry(top_frame, textvariable=passwordVar2, font=labelfont, show="*")
        passwordPrompt2.insert(END, password_proton)
        passwordPrompt2.pack()
        passwordPrompt2.place(x=200, y=50*2, width=200)

        # creating a input field to prompt password (pgm server)
        create_label(top_frame, "pgm server:", 3,5, 'thistle2')
        
        def get_password_pgm(v):
                global password_pgm
                password_pgm = v.get()
        
        passwordVar3 = StringVar()
        passwordVar3.trace("w", lambda name, index, mode, sv=passwordVar3: get_password_pgm(sv))
        passwordPrompt3 = Entry(top_frame, textvariable=passwordVar3, font=labelfont, show="*")
        passwordPrompt3.insert(END, password_pgm)
        passwordPrompt3.pack()
        passwordPrompt3.place(x=200, y=50*3, width=200)

        # creating a radiobutton to choose save credentials or not
        create_label(top_frame, "Save the server info?",4,0, 'thistle2')
        def display_help1():
                messagebox.showinfo("Info", "If choose 'yes' and the passwords are correct, the program will save the passwords for next time use.\n If choose 'no' and the passwords are incorrect, the 2 passwords ever saved by this program in this computer will be deleted.")
                
        helpButton = Button(top_frame, text="?", font=labelfont, command = display_help1)
        helpButton["bg"] = "yellow"
        helpButton.pack()
        helpButton.place(x=430, y=50*4)
        
        var = IntVar()
        var.set(1)
        def sel():
                global is_saved
                is_saved = var.get()
                
        R1 = Radiobutton(root, text="Yes", variable=var, value=1, command=sel, font=labelfont)
        R1.configure(bg = 'thistle2')
        R1.pack()
        R1.place(x=200, y=50*4)
        R2 = Radiobutton(root, text="No", variable=var, value=0, command=sel, font=labelfont)
        R2.configure(bg = 'thistle2')
        R2.pack()
        R2.place(x=300, y=50*4)

        #frame
        middle_frame = Frame(self, bg='wheat', width = width, height = 100).grid(row = 1, columnspan = 1)
        
        # creating a button to get job folder
        create_label(top_frame, "Job folder:",5.5,0, 'wheat')
        def display_help2():
                messagebox.showinfo("Info", "Select a job folder from this computer.\nThe folder must contain excel sheets whose names start with \"PRO<plate_number>-\"\ni.e. folder Z:\JOBS\Jobs_2019\19009 (E. Stockinger U of O) contains PRO424-ISC-CS-TAS-19009-p1, PRO426-ISC-CS-TAS-19009-p2, PRO427-ISC-CS-TAS-19009-p3")
                
        helpButton2 = Button(top_frame, text="?", font=labelfont, command = display_help2)
        helpButton2["bg"] = "yellow"
        helpButton2.pack()
        helpButton2.place(x=430, y=50*5.5)
        
        wdirButtonText = StringVar()
        def master_get_wdir():
            get_wdir()
            wdirButtonText.set(wdir)
        
        wdirButton = Button(self, textvariable=wdirButtonText, command=master_get_wdir, cursor = cursor_img, font=labelfont)
        wdirButton.place(x=200, y=50*5.5, width=200)
        wdirButtonText.set("Open directory dialog")
        
        #frame
        bottom_frame = Frame(self, bg='light blue', width = width, height = 200).grid(row = 2, columnspan = 1)
        
        # creating a button to run
        runButton = Button(self, command = run, text="Run", cursor = cursor_img)
        runButton.place(x=width/2-25, y=70+50*5 + 50)
        runButton.config(bg="ghost white", font=labelfont)
        
		
if __name__ == "__main__":
        retrieve_previous_configs()
        retrieve_previous_dirs()
        root = Tk()
        #position the window in the center
        root.geometry(str(width) + "x" + str(height))
        app = Window1(root)
        root.mainloop()

