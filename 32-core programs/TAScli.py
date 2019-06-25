#This file is a Perl-to-Python translation of TAScli.pl and TASapprox.pl
#Translator: Ngoc Duong
#Crop and Soil department, Washington State University, Pullman, WA
#Date: 01/11/2019

import sys
import os 
from subprocess import PIPE, Popen

#Check valid number of command arguments
if (len(sys.argv) == 1):
        print "\nError: Invalid number of arguments.\nRun: python TAScli.py -h or python TAScli.py --help for more info\n"
        sys.exit()


#Print help for command -h or --help
if (sys.argv[1] == "-h" or sys.argv[1] == "--help"):
	print "\nEnter the command as follows:\npython TAScli.py [directory of reads] [directory and name of key file] [number of cores] [minimum similarity to qualify as a match] <opt for filter: het percentage> <opt for filter: min hitcounts>\nExample:\npython TAScli.py /home/user/Documents/TASreads /home/user/Documents/keyfiles/Keyfile 28 0.95\nThe number of cores and minimum similarity are optional, defaults are 30 and 0.98, respectively. However, these arguments MUST be entered in order, so if you wish to enter a minimum similarity you must also enter a number of cores such that number of cores is the third argument and minimum similarity is the fourth argument.\n\n"
	sys.exit()


#Check valid number of command arguments
if (not (len(sys.argv) == 3 or len(sys.argv) == 5 or len(sys.argv) == 7)):
        print "\nError: Invalid number of arguments.\nRun: python TAScli.py -h or python TAScli.py --help for more info\n"
        sys.exit()


#Check for duplicates in Keyfile
keyFile = open(sys.argv[2], 'r')
temp = []
for line in keyFile:
	if (line[0] == '>'):
		if (line in temp):
			print ("\nError: Key file entries must be unique!! " + sys.argv[2] + " has duplicate name: " + line + ".\n\n")
			sys.exit()
		temp.append(line)

#get args
wdir = sys.argv[1]
scriptdir = os.getcwd()
if (len(sys.argv) == 3):
	cores = 30
	minsim = 0.98
else:
	cores = int(sys.argv[3])
	minsim = float(sys.argv[4])

#get the correct taswork file
if (minsim > 1.0 or minsim < 0):
	print "Error: similarity must be in [0,1.0]\n"
	sys.exit()
elif (minsim == 1.0):
	taswork = "taswork100.py"
else:
	taswork = "taswork95.py"

#create needed dirs if they do not already exist
if  not os.path.exists(wdir + "/hpcjcl"):
	os.makedirs(wdir + "/hpcjcl")
if  not os.path.exists(wdir + "/Analysis"):
        os.makedirs(wdir + "/Analysis")
if  not os.path.exists(wdir + "/Analysis/Genotypes"):
        os.makedirs(wdir + "/Analysis/Genotypes")
if  not os.path.exists(wdir + "/Analysis/Markers"):
        os.makedirs(wdir + "/Analysis/Markers")
os.system("cp " + scriptdir + "/ChromoLocations " + wdir + "/hpcjcl/ChromoLocations");

#create rhits.R
rhits = open(wdir + "/hpcjcl/rhits.R", 'w')
rhits.write("a<-read.table(file=\"" + wdir + "/Analysis/hitcount.lst\", header=T)\n\
b<-as.data.frame(a)\n\
library(reshape)\n\
b<-a[c(1,2,3)]\n\
mb<-melt(b,id=c(\"Tag\",\"Ril\"))\n\
rs<-cast(mb,Tag~Ril, fun.aggregate=sum)\n\
write.table(rs,file=\"" + wdir + "/Analysis/HitCounts.txt\", sep=\"\\t\", row.names=F)")
rhits.close()

#create rsnps.R
rsnps = open(wdir + "/hpcjcl/rsnps.R", 'w')
rsnps.write("a<-read.table(file=\"" + wdir + "/Analysis/snpreport.lst\", header=T)\n\
b<-as.data.frame(a)\n\
library(reshape)\n\
b<-a[c(1,2,5)]\n\
mb<-melt(b,id=c(\"TagPos\",\"Ril\"))\n\
rs<-cast(mb,TagPos~Ril)\n\
write.table(rs,file=\"" + wdir + "/hpcjcl/SNPreport.txt\", sep=\"\\t\", row.names=F)")
rsnps.close()

p1 = Popen(['ls', wdir, "-p"], stdout=PIPE)
p2 = Popen(["grep", "-v", "/"], stdin=p1.stdout, stdout=PIPE)
filelist = p2.communicate()[0].split()

for i in range(len(filelist)):
	filelist[i] = wdir + "/" + filelist[i]
filecnt = len(filelist)
intstart = int(filecnt/cores)
leftover = filecnt-(intstart*cores)

#make the xfiles, write launch script, launch it
shellout = open(wdir + "/hpcjcl/launchtas.sh", 'w')
xtrack=0
for xl in range(1, cores + 1):
	added = 0
	if (xtrack < filecnt):
		xout = open(wdir + "/hpcjcl/x" + str(xl), 'w')
		if (leftover > 0):
			xlines = intstart+1
		else:
			xlines = intstart

		while (True):
			xout.write(filelist[xtrack] + "\n")
			xtrack += 1
			added += 1
			if (added == xlines or xtrack > filecnt):
				break
		shellout.write("python " + scriptdir + "/" + taswork + " " + wdir + "/hpcjcl/x" + str(xl) + " " + wdir + "/hpcjcl/cleankey " + wdir + " " + str(minsim) + " & grpwait" + str(xl) + "=$!\n")
		added = 0
		xout.close()
	leftover -= 1


for gcnt in range(1, cores + 1):
	shellout.write("wait $grpwait" + str(gcnt) + "\n")
shellout.write("echo \"Ril\tTag\tHits\">" + wdir + "/hpcjcl/hithead && echo \"Ril\tTagPos\tTag\tPos\tCall\">" + wdir + "/hpcjcl/snphead && cat " + wdir + "/Analysis/Genotypes/*/*.hits.txt|sort -u >" + wdir + "/hpcjcl/hitcount.srt &&  cat " + wdir + "/hpcjcl/hithead " + wdir + "/hpcjcl/hitcount.srt>" + wdir + "/Analysis/hitcount.lst && R --slave --vanilla <" + wdir + "/hpcjcl/rhits.R & cat " + wdir + "/Analysis/Genotypes/*/*.snps.txt |sort -u >" + wdir + "/hpcjcl/snpreport.srt &&  cat " + wdir + "/hpcjcl/snphead " + wdir + "/hpcjcl/snpreport.srt>" + wdir + "/Analysis/snpreport.lst && R --slave --vanilla <" + wdir + "/hpcjcl/rsnps.R && sed 's#NA#\"-\"#g' -i " + wdir + "/hpcjcl/SNPreport.txt && head -1 " + wdir + "/hpcjcl/SNPreport.txt>" + wdir + "/hpcjcl/snpheader && sed '1d' -i " + wdir + "/hpcjcl/SNPreport.txt && echo \"Chromosome\tChromo_arm\tcM\">" + wdir + "/hpcjcl/chromohead && echo \"Tag\" >" + wdir + "/hpcjcl/taghd && paste " + wdir + "/hpcjcl/taghd " + wdir + "/hpcjcl/snpheader> " + wdir + "/hpcjcl/snpheader1 && paste " + wdir + "/hpcjcl/snpheader1 " + wdir + "/hpcjcl/chromohead>" + wdir + "/hpcjcl/finalheader && cut -d\\\" -f2 " + wdir + "/hpcjcl/SNPreport.txt|cut -d_ -f1|sort >" + wdir + "/hpcjcl/foundsnps && cut -f1 " + wdir + "/hpcjcl/ChromoLocations|sort>" + wdir + "/hpcjcl/chromosnps && comm -1 -2 " + wdir + "/hpcjcl/chromosnps " + wdir + "/hpcjcl/foundsnps >" + wdir + "/hpcjcl/greplist && LC_ALL=C grep -w -f " + wdir + "/hpcjcl/greplist " + wdir + "/hpcjcl/ChromoLocations|sort -k1,1 >" + wdir + "/hpcjcl/commonlocations && cut -d\\\" -f2 " + wdir + "/hpcjcl/SNPreport.txt|cut -d_ -f1>" + wdir + "/hpcjcl/snptagnames && paste " + wdir + "/hpcjcl/snptagnames " + wdir + "/hpcjcl/SNPreport.txt|sort -k1,1 >" + wdir + "/hpcjcl/tmpreport1 && join -a1 " + wdir + "/hpcjcl/tmpreport1 " + wdir + "/hpcjcl/commonlocations|tr ' ' '\\t' > " + wdir + "/hpcjcl/FinalSNPs && cat " + wdir + "/hpcjcl/finalheader " + wdir + "/hpcjcl/FinalSNPs>" + wdir + "/hpcjcl/SNPreport.txt && sed 's#\"##g' -i " + wdir + "/hpcjcl/SNPreport.txt && perl " + wdir + "/hpcjcl/shufflecols.pl && sed 's#\\r##' -i " + wdir + "/Analysis/SNPreport.txt") #&& rm -rf wdir/hpcjcl/"

shellout.close()

#creating shufflecols.pl
shuf = open(wdir + "/hpcjcl/shufflecols.pl", 'w')
shuf.write("open $in,'<',\"" + wdir + "/hpcjcl/SNPreport.txt\";\n\
open $out ,'>',\"" + wdir + "/Analysis/SNPreport.txt\";\n\
$hdr=<$in>;\n\
chomp $hdr;\n\
@hdprts=split /\\t/,$hdr;\n\
$cols=@hdprts;\n\
print $out \"Tag\\tSNP_position\\tChromo\\tarm\\tcM\";\n\
for $cc (2..($cols-4)){print $out \"\\t$hdprts[$cc]\";}\n\
while ($lin = <$in>)\n\
{\n\
chomp $lin;\n\
@linprts=split /\\t/,$lin;\n\
@tagpos=split /_/,$linprts[1];\n\
print $out \"\\n$tagpos[0]\\t$tagpos[1]\";\n\
print $out \"\\t$linprts[$cols-3]\\t$linprts[$cols-2]\\t$linprts[$cols-1]\";\n\
for $cc (2..($cols-4)){print $out \"\\t$linprts[$cc]\";}\n\
}\n\
close $in;close $out;")
shuf.close()

if not os.path.exists(wdir + "/hpcjcl/cleankey"):
	#simplify key names
	keyin = open(sys.argv[2], 'r')
	keyout = open(wdir + "/hpcjcl/cleankey", 'w')
	
	kin = keyin.readline()
	while (kin):
		kin = kin.rstrip()
		for kp in kin:
			if ((kp == '_') or (kp == '-')):
				keyout.write('.')
			else:
				keyout.write(kp)
		keyout.write('\n')
		kseqin = keyin.readline()
		keyout.write(kseqin)
		kin = keyin.readline()
	
	keyin.close()
	keyout.close()

#end key names
os.system("sh " + wdir + "/hpcjcl/launchtas.sh")
#remove medium files
os.system("rm -rf " + wdir + "/hpcjcl/ " + "save")


#######################Start filtering out the 4 resulting files#############################################
if (len(sys.argv) == 7): #user already specified filter args
	percentage = sys.argv[5]
	min = sys.argv[6]
	os.system("python filter_snips.py " + wdir + "/Analysis " + str(percentage) + " " + str(min))

else:
	print "\n"
	i = 0
	while (i == 0):	#want to filter?
		filter = raw_input("Filter the result (exp: remove seqs that  < 20% and < 5 hits)? (y/n)")
		if (filter == "y" or filter == "Y" or filter == "yes"):
			i = 1
		elif (filter == "n" or filter == "N" or filter == "no"):
			i = -1
	
		else:
			print "Invalid answer. Please answer y, Y, yes, n, N, or no"

	if i == 1: # yes to filter
		#get percentage to filter
		percentage = 1.1
		while (percentage > 1.0 or percentage < 0.0):
			percentage = raw_input("HET percentage to filter? (exp: 0.20) ")
			percentage = float(percentage)
			if (percentage > 1.0 or percentage < 0.0):
				print "Percentage must be in [0.0,1.0]"
		print "\n"
		#get min hit count to filter
		min = input("Minimum allowed hit count to filter? (exp: 5) ")

		os.system("python filter_snips.py " + wdir + "/Analysis " + str(percentage) + " " + str(min))
	
	
print "THE ANALYSIS IS COMPLETE\n"
#########################End filtering out the 4 resulting files#############################################
