from tkinter import *
from tkinter import messagebox
from tkinter.filedialog import askopenfilename, askdirectory
import os

'''
This program cleans up data in the snip report
'''


#global variables
width = 500
height = 330
labelfont = ('times', 12, 'bold')
cursor_img = "heart"
wdir = "Open file dialog"
previous_wdir = ""
p_missing_data = 60 #% to throw away
p_het = 100 #% to throw away

######################################################################################
######transfer data to pgm server and make a data folder in this computer#############
def retrieve_previous_dirs(): #save to/retrieve from dirs.txt
	global previous_wdir
	
	if (os.path.exists("dir2.txt") and os.path.isfile("dir2.txt") and os.path.getsize("dir2.txt")>0):
		infile = open("dir2.txt", 'r')
		previous_wdir = infile.readline().rstrip().split(":")[1]
		infile.close()
	else: #create the file
		file = open("dir2.txt", 'w')
		file.close()

def save_previous_dirs(): #save to/retrieve from configs.txt
	outfile = open("dir2.txt", 'w')
	outfile.write("wdir:" + wdir + "\n")
	outfile.close()
	
def run():
        #check if all parameters are chosen
        if (wdir == "Open file dialog"):
                messagebox.showerror("Error", "Choose a SNP report file")
                return
        save_previous_dirs()
        
        #open the file
        infile =  open(wdir, 'r')
        extension = wdir.split(".")[-1]
        new_file_name = wdir[:(-1 - (len(extension)))] + "_result.txt"
        outfile =  open(new_file_name, 'w')

        #copy the headings over
        line = infile.readline()
        outfile.write(line)

        #for each row in infile
        row = infile.readline().rstrip()
        while (row):
                data = row.split("\t")[5:]
                
                #compute stats
                n_missing_data = data.count('-')
                n_have_data = len(data) - n_missing_data
                n_R = data.count('R')
                n_M = data.count('M')
                n_Y = data.count('Y')
                n_K = data.count('K')
                n_S = data.count('S')
                n_W = data.count('W')
                n_H = data.count('H')
                n_V = data.count('V')
                n_D = data.count('D')
                n_B = data.count('B')
                
                #compute percentages
                p_row_missing_data = float(n_missing_data) / len(data)
                try:
                        p_R = float(n_R) / n_have_data
                        p_M = float(n_M) / n_have_data
                        p_Y = float(n_Y) / n_have_data
                        p_K = float(n_K) / n_have_data
                        p_S = float(n_S) / n_have_data
                        p_W = float(n_W) / n_have_data
                        p_H = float(n_H) / n_have_data
                        p_V = float(n_V) / n_have_data
                        p_D = float(n_D) / n_have_data
                        p_B = float(n_B) / n_have_data
                except:
                        p_R = p_M = p_Y = p_K = p_S = p_W =  p_H = p_V = p_D = p_B = 1.0

                p_am_code_list = [p_R, p_M, p_Y, p_K, p_S, p_W, p_H, p_V, p_D, p_B]
                p_am_code_list_filtered = []
                for item in p_am_code_list:
                        if (item >= p_het/100.0):
                                p_am_code_list_filtered.append(item)
                

                #check if the row pass the conditions and write to outfile
                if (p_row_missing_data < p_missing_data/100.0 and len(p_am_code_list_filtered) == 0):
                        outfile.write(row + "\n")
                
                #update
                row = infile.readline().rstrip()
        
        infile.close()
        outfile.close()

        #ending message
        messagebox.showinfo("Info", "The analysis is complete.\nThe result file is " + new_file_name)
        
        
#####################################
######user interface#################

def get_wdir():
    global wdir
    filename = askopenfilename(initialdir = previous_wdir,title = "Select file")
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
        self.master.title("GMS: Clean up Data in Snip Report")

        # allowing the widget to take the full space of the root window
        self.pack(fill=BOTH, expand=1)

        #frame
        top_frame = Frame(self, bg='thistle2', width = width, height = 100).grid(row = 0, columnspan = 1)

        # creating a button to get job folder
        create_label(top_frame, "Snip report file:",1,0, 'thistle2')
        
        wdirButtonText = StringVar()
        def master_get_wdir():
            get_wdir()
            wdirButtonText.set(wdir)
        
        wdirButton = Button(self, textvariable=wdirButtonText, command=master_get_wdir, cursor = cursor_img, font=labelfont)
        wdirButton.place(x=260, y=50*1, width=200)
        wdirButtonText.set("Open file dialog")

        #frame
        middle_frame = Frame(self, bg='wheat', width = width, height = 140).grid(row = 1, columnspan = 1)

        # creating a slide to get percentage of missing data
        create_label(middle_frame, "% of missing data to throw away:",3,0, 'wheat')
        var0 = IntVar()
        var0.set(60)
        def get_percentage_missing_data(val):
                global p_missing_data
                p_missing_data = int(val)
                
        S0 = Scale(root, from_=0, to=100, resolution=1, variable=var0, showvalue=60, command=get_percentage_missing_data, font=labelfont, orient=HORIZONTAL, length = 200)
        S0.configure(bg = 'wheat', highlightbackground = 'wheat')
        S0.pack()
        S0.place(x=260, y=50*3-20)

        # creating a slide to get percentage of het:i.e. get rid of rows whose percentage of ambiguity codes is >= 95%
        create_label(middle_frame, "% of HET. to throw away:",4,0, 'wheat')

        def display_help():
                messagebox.showinfo("Info", "I.e. %HET = 90% means:\nStep1: for each row, calculate % of each am code = number of each am code / number of all non-dash values.\nStep 2: get rid of rows whose any of the computed percentage >= 90%.")
                
        helpButton = Button(top_frame, text="?", font=labelfont, command = display_help)
        helpButton["bg"] = "yellow"
        helpButton.pack()
        helpButton.place(x=470, y=50*4-5)

        var1 = IntVar()
        var1.set(100)
        def get_percentage_het(val):
                global p_het
                p_het = int(val)
                
        S1 = Scale(root, from_=0, to=100, resolution=1, variable=var1, showvalue=100, command=get_percentage_het, font=labelfont, orient=HORIZONTAL, length = 200)
        S1.configure(bg = 'wheat', highlightbackground = 'wheat')
        S1.pack()
        S1.place(x=260, y=50*4-20)
        
        #frame
        bottom_frame = Frame(self, bg='light blue', width = width, height = 200).grid(row = 2, columnspan = 1)
        
        # creating a button to run
        runButton = Button(self, command = run, text="Run", cursor = cursor_img)
        runButton.place(x=width/2-25, y=70+50*3 + 50)
        runButton.config(bg="ghost white", font=labelfont)
        
		
if __name__ == "__main__":
        retrieve_previous_dirs()
        root = Tk()
        #position the window in the center
        root.geometry(str(width) + "x" + str(height))
        app = Window1(root)
        root.mainloop()

