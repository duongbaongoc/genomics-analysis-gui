import sys
import os

#about this program: filter out those sequences with low hit counts, output new_SNPreport.txt and new_HitCounts.txt
#This program only works after the analysis is done and there are SNPreport.txt and HitCounts.txt in Analysis folder



#this function returns the ambiguity code's positions
#pre-condition: file has just been opened, cursor is at the beginning of the file
def get_am_pos(file):
	firstline = file.readline()
	secondline = file.readline().rstrip()
	pos = 0
	am_pos = []

	for char in secondline:
		if char != '.':
			am_pos.append(pos)
		pos += 1
	return am_pos

#this function reads each sequence in the file and returns a dictionary of
#each sequence's code and its occurences
#pre-condition: file is opened to read and the cursor is at the tag of the first sequence
def get_occurences(file, am_pos):
	dict = {}
	line = file.readline()
	code = ""
	while(line):	#line == tag
		tokens = line.split('_')
		occ = int(tokens[1])
		seq = file.readline()
		code = ""
		for pos in am_pos:
			code += seq[pos]
		dict[code] = occ
		line = file.readline()
	return dict

#this function filters out the codes whose occurence < 20% of max occurences
def filter_codes(dict, percent, min_hits):
	remain = []
	total_hits = 0
	#get max_occ
	max_occ = 0
	for key,value in dict.items():
		if value > max_occ:
			max_occ = value
	accept = int(max_occ * (1- percent))
	
	#filter
	for key,value in dict.items():
		if value >= accept and value >= min_hits:
			remain.append(key)
			total_hits += value
	return remain, total_hits

#this function converts am codes
#exp:
# L = ["AGG", "CCG", "ACG"] => all codes for seq1, seq2, seq3
# "AGG" => 3 snips in seq 1
# output [amcode_of(A,C,A), amcode_of(G,C,C), amcode_of(G,G,G)]
def get_am(L):
	#conver L into a 2d list where each inner list has codes from all seqs at a snip position
	_2d_list = []
	for n_pos in range(len(L[0])):
		inner_list = []
		for seq in L:
			inner_list.append(seq[n_pos])
		_2d_list.append(inner_list)

	#call get_am_help to convert each inner list into an am code
	result = []
	for inner_list in _2d_list:
		am_code = get_am_help(inner_list)
		result.append(am_code)
	return result	


#this function converts a list of codes to an ambiguity code
def get_am_help(list):
	if 'A' in list and 'C' in list and 'G' in list and 'T' in list:
		return 'N'  
	if 'A' in list and 'C' in list and 'G' in list:
		return 'V'
	if 'A' in list and 'C' in list and 'T' in list:
		return 'H'
	if 'A' in list and 'G' in list and 'T' in list:
		return 'D'
	if 'C' in list and 'G' in list and 'T' in list:
		return 'B'
	if 'A' in list and 'G' in list:
		return 'R'
	if 'A' in list and 'C' in list:
		return 'M'
	if 'C' in list and 'T' in list:
		return 'Y'
	if 'G' in list and 'T' in list:
		return 'K'
	if 'C' in list and 'G' in list:
		return 'S'
	if 'A' in list and 'T' in list:
		return 'W'
	if 'A' in list and '-' in list:
		return 'X'
	if 'C' in list and '-' in list:
		return 'X'
	if 'G' in list and '-' in list:
		return 'X'
	if 'T' in list and '-' in list:
		return 'X'
	return list[0]

if __name__ == "__main__":
	if (len(sys.argv) <= 1 or sys.argv[1] == "--help"):
		print("To run: python filter_snips.py path/to/an/Analysis/folder <percent to filter> <min hit counts to keep>")
		print("Example: python filter_snips.py Analysis 0.255555 5")
		print("Output: path/to/Analysis/new_SNPreport.txt  => filter out all whose num hits < 25.5555% of maxnum hits and < 5 hits")
		exit()
	
	#Get the input: Analysis folder, percent to filter, min hit counts to keep
	Analysis = sys.argv[1]
	percent = float(sys.argv[2])
	min_hits = int(sys.argv[3])
	
	############################Get the ambiguity codes after filter###################################
	file_am = {}
	file_hits = {}
	
	for folder in os.listdir(Analysis + "/Markers"): 
		for file in os.listdir(Analysis + "/Markers/" + folder):

			
			infile = open(Analysis + "/Markers/" + folder + "/" + file, 'r')
			#get the ambiguity code's position
			am_pos = get_am_pos(infile)
			#skip the next 2 lines == the key tag and seq
			line = infile.readline()
			line = infile.readline()
			#for each sequence, get the number occurences and its codes
			dict = get_occurences(infile, am_pos)
			infile.close()
		

			#filter out codes whose occurences < 20% of max occurences in the file
			remain_codes, total_hits = filter_codes(dict, percent, min_hits)#remain_codes is a list whose each item is a string is codes of a seq
			#convert remain codes to an ambiguity code
			am_codes = get_am(remain_codes)
			file_am[file] = am_codes
			file_hits[file] = total_hits
	
	############################update SNPreport.txt###################################################
	#Make the Snip file from Analysis/SNPreport.txt (because it has info needed to keep) and file_am
	old_report = open(Analysis + "/SNPreport.txt", 'r')
	new_report = open(Analysis + "/after_filter_SNPreport.lst", 'w')

	#copy the header line (first line) over
	line = old_report.readline()
	new_report.write(line)
	
	#get list of samples from the header (we are interested in the order)
	tokens = line.rstrip().split("\t")
	list_samples = tokens[5:]
	
	#from the second line on, check if need to update the am code
	line = old_report.readline()
	previous_tag = "None" #these previous values and k values are to keep track of repetitions of tags in SNPreport
	previous_pos = "None"
	k = 0 #keep track of same tags in SNPreport.txt
	while(line): #for each line in the old SNP report
		tokens = line.rstrip().split("\t") #only care about tokens before the snips
		tag = tokens[0]
		pos = tokens[1]
		if (tag == previous_tag):
			k += 1
		else:
			k = 0
		if (pos == previous_pos):
			k -= 1
		
		new_line = tokens[0] + "\t" + tokens[1] + "\t" + tokens[2] + "\t" + tokens[3] + "\t" + tokens[4]
		for sample in list_samples:
			key = sample + "_" + tag + ".fas"
			if file_am.get(key) == None:
				new_line += "\t-"
			else:
				new_line += "\t" + file_am[key][k]
		new_line += "\n"
		
		new_report.write(new_line)

		#update statements
		line = old_report.readline()
		previous_tag = tag
		previous_pos = pos
	
	old_report.close()
	new_report.close()

	#############################update HitCounts.txt##################################################
	#Make the hitcount file from Analysis/HitCounts.txt (to get the same order of tags and samples) and file_hits
	old_hit_count = open(Analysis + "/HitCounts.txt", 'r')
	new_hit_count = open(Analysis + "/after_filter_HitCounts.lst", 'w')

	#copy the header line (first line) over
	line = old_hit_count.readline()
	new_hit_count.write(line)
	
	#get list of samples from the header (we are interested in the order)
	tokens = line.rstrip().split("\t")
	list_samples = tokens[1:]
	
	#write from file_hits to new_hit_count
	line = old_hit_count.readline()
	while(line): #for each line in the old HitCounts.txt
		tokens = line.rstrip().split("\t") #only care about tokens[0]==tag
		tag = tokens[0][1:-1]

		new_line = tag
		for sample in list_samples:
			key = sample[1:-1] + "_" + tag + ".fas"
			if file_hits.get(key) == None:
				new_line += "\t0"
			else:
				new_line += "\t" + str(file_hits[key])
		new_line += "\n"

		new_hit_count.write(new_line)
		
		#update statements
		line = old_hit_count.readline()

	old_hit_count.close()
	new_hit_count.close()
	
