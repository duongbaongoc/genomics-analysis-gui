#This is a perl-to-python translation of TASapprox....pl and TASexact....pl
#Translator: Ngoc Duong
#Crop and Soil department, Washington State University, Pullman, WA
#Date: 06/11/2019

import sys
import os
from subprocess import PIPE, Popen

minsim = float(sys.argv[4])
p1 = Popen(['nodeattr','-c','\"~(login||mgmt)\"'], stdout=PIPE)
p2 = Popen(['tr', '\',\'', '\'\n\''], stdin=p1.stdout, stdout=PIPE)
p3 = Popen(['wc', '-l'], stdin=p2.stdout, stdout=PIPE)
nodecountnom = int(p3.communicate()[0])
nodecountc = nodecountnom - 2
if (minsim < 1.0):
	nodecountc = nodecountnom - 1
p1 = Popen(['scontrol', 'show', 'node'], stdout=PIPE)
p2 = Popen(['grep', 'CPUTot'], stdin=p1.stdout, stdout=PIPE)
p3 = Popen(['cut', '-d=', '-f4'], stdin=p2.stdout, stdout=PIPE)
p4 = Popen(['tr', ' ', '\t'], stdin=p3.stdout, stdout=PIPE)
p5 = Popen(['cut', '-f1'], stdin=p4.stdout, stdout=PIPE)
p6 = Popen(['awk', '{s+=$1} END {print s}'], stdin=p5.stdout, stdout=PIPE)
corecnt = int(p6.communicate()[0])
ntaskrequest = int(corecnt/2)

if (sys.argv[1] == '-h' or sys.argv[1] == '--help'):
	print ("\nEnter the command as follows:\npython TAScli.py [directory of reads] [directory and name of key file] [number of nodes available] [min sim]\nExample:\npython TAScli.py /home/user/Documents/TASreads /home/user/Documents/keyfiles/Keyfile " + str(nodecountc) + "1.0 \nThe number of nodes available is currently estimated as " + str(nodecountc) + ", provide a different number if needed. These arguments MUST be entered in order.\n\n")
	sys.exit()

#check for duplicates in Keyfile
keycounts = []
p1 = Popen(['grep', '>', sys.argv[2]], stdout=PIPE)
p2 = Popen(['wc', '-l'], stdin=p1.stdout, stdout=PIPE)
keycounts.append(int(p2.communicate()[0]))
p1 = Popen(['grep', '>', sys.argv[2]], stdout=PIPE)
p2 = Popen(['sort', '-u'], stdin=p1.stdout, stdout=PIPE)
p3 = Popen(['wc', '-l'], stdin=p2.stdout, stdout=PIPE)
keycounts.append(int(p3.communicate()[0]))
keycntall = keycounts[0]
keycntuniq = keycounts[1]
dupkeys = keycntall-keycntuniq
if (dupkeys > 0):
	print ("\nKey file entries must be unique!! " + sys.argv[2] + " has " + str(dupkeys) + " duplicate name(s).\n\n")
	sys.exit()
ft = ""
try:
	nodecntp = int(sys.argv[3])
	noderq = nodecntp
except:
	noderq = nodecountc
wdir = sys.argv[1]
scriptdir = os.getcwd()
p1 = Popen(['ls', wdir], stdout=PIPE)
filelist0 = p1.communicate()[0].split()
filelist = []
for item in filelist0:
	filelist.append(wdir + "/" + item + "\n") 
 
if not os.path.exists(wdir + "/hpcjcl"):
	os.makedirs(wdir + "/hpcjcl")
if not os.path.exists(wdir + "/Analysis"):
	os.makedirs(wdir + "/Analysis")
if not os.path.exists(wdir + "/Analysis/Genotypes"):
	os.makedirs(wdir + "/Analysis/Genotypes")
if not os.path.exists(wdir + "/Analysis/Markers"):
	os.makedirs(wdir + "/Analysis/Markers")
os.system("cp " + scriptdir + "/ChromoLocations " + wdir + "/hpcjcl/ChromoLocations")
if not os.path.exists(wdir + "/hpcjcl/cleankey"):
	#simplify key names
	keyin = open(sys.argv[2], 'r')
	keyout = open(wdir + "/hpcjcl/cleankey", 'w')
	kin = keyin.readline()
	while(kin):
		kin = kin.rstrip()
		kinprts = kin
		for kp in kinprts:
			if((kp == '_') or (kp == '-')):
				keyout.write(".")
			else:
				keyout.write(kp)
		keyout.write("\n")
		kseqin = keyin.readline()
		keyout.write(kseqin)
		kin = keyin.readline()
	keyin.close()
	keyout.close()
#make the xfiles, write launch script, launch it
filecnt = len(filelist)
hdout = open(wdir + "/hpcjcl/genolist", 'w')
for xl in range(1, filecnt + 1):
	xout = open(wdir + "/hpcjcl/x" + str(xl), 'w')
	xout.write(filelist[(xl-1)])
	xout.close()
	hdout.write(filelist[(xl-1)])

hdout.close()
os.system("sed \'s#^.*/##\' " + wdir + "/hpcjcl/genolist|tr \'\\n\' \'\\t\'|sed \'s#\\t\$#\\n#\' | sed \'s#^#Tag\tChromosome\tChromoArm\tLocation\tSNPposition\t#\'>" + wdir + "/hpcjcl/Aheader")
os.system("sed \'s#^.*/##\' " + wdir + "/hpcjcl/genolist|tr \'\\n\' \'\\t\'|sed \'s#\\t\$#\\n#\' | sed \'s#^#Tag\tChromosome\tChromoArm\tLocation\t#\'>" + wdir + "/hpcjcl/Hheader")

awkout = open(wdir + "/hpcjcl/awksplit", 'w')
awkout.write("BEGIN{fn = \"" + wdir + """/hpcjcl/tags.1\"; n = 1 ;m=1}
{ 
   if (n<=o) {print > fn;n++}
   if (n>(o-1)) {close (fn)
       m++
       fn = \"""" + wdir + """/hpcjcl/tags.\" m
        n=0
   }
}""")
awkout.close()
awklaunch = open(wdir + "/hpcjcl/launchawk.sh", 'w')
awklaunch.write("l=$((`wc -l < " + wdir + """/hpcjcl/snplist`/192))
awk -v o=$l -f """ + wdir + "/hpcjcl/awksplit " + wdir + """/hpcjcl/snplist
""")
awklaunch.close()

shellout = open(wdir + "/hpcjcl/launchtas.sh", 'w')
shellout.write("""#!/bin/bash
#SBATCH --job-name=pro366
#SBATCH --nodes=""" + str(noderq) + """
#SBATCH --distribution=cyclic
#SBATCH --ntasks=""" + str(ntaskrequest) + """
module add muscle
module add cd-hit-est
module add perl5.29.5
module add soap
module add python2.6.9
""")
if (minsim == 1.0):
	shellout.write("""
for i in {1..""" + str(filecnt) + """}; do
srun --exclusive --nodes=1 --ntasks=1 python """ + scriptdir + "/taswork100.py " + wdir + "/hpcjcl/x$i " + wdir + "/hpcjcl/cleankey " + wdir + """ 1.0 &""")
else:
	shellout.write("""module add agrep
for i in {1..""" + str(filecnt) + """}; do
srun --exclusive --nodes=1 --ntasks=1 python """ + scriptdir + "/taswork95.py " + wdir + "/hpcjcl/x$i " + wdir + "/hpcjcl/cleankey " + wdir + " " + str(minsim) + " &")


shellout.write("""
done

wait

echo \"Ril\tTag\tHits\">""" + wdir + """/hpcjcl/hithead &&
echo \"Ril\tTagPos\tTag\tPos\tCall\">""" + wdir + """/hpcjcl/snphead &&

cat """ + wdir + "/Analysis/Genotypes/*/*.hits.txt|sort -u >" + wdir + """/hpcjcl/hitcount.srt &&  
cat """ + wdir + "/hpcjcl/hithead " + wdir + "/hpcjcl/hitcount.srt>" + wdir + """/Analysis/hitcount.lst && 

cat """ + wdir + "/Analysis/Genotypes/*/*.snps.txt |sort -u >" + wdir + """/hpcjcl/snpreport.srt &&  
cat """ + wdir + "/hpcjcl/snphead " + wdir + "/hpcjcl/snpreport.srt>" + wdir + """/Analysis/snpreport.lst && 

cut -f1 """ + wdir + "/hpcjcl/snpreport.srt|sort -u >" + wdir + """/hpcjcl/linelist &&
cut -f2 """ + wdir + "/hpcjcl/snpreport.srt|sort -u >" + wdir + """/hpcjcl/snplist &&

srun --exclusive --nodes=1 --ntasks=1 sh """ + wdir + """/hpcjcl/launchawk.sh &
wait 

t=$(ls """ + wdir + """/hpcjcl/tags.[123456789]*|wc -l)
for i in $( seq 1 $t ); do
srun --exclusive --ntasks=1 --nodes=1 perl subsetscorer.pl """ + wdir + """  $i &
done
wait

echo \"\" >>""" + wdir + """/hpcjcl/Aheader && cat """ + wdir + "/hpcjcl/Aheader " + wdir + "/hpcjcl/tagreport.* > " + wdir + """/Analysis/SNPreport.txt &&
rm """ + wdir + "/hpcjcl/tags.[123456789]* && rm " + wdir + "/hpcjcl/tagreport.* && rm "  + wdir + "/hpcjcl/linelist && rm " + wdir + """/hpcjcl/snplist &&
cut -f1 """ + wdir + "/hpcjcl/hitcount.srt|sort -u >" + wdir + """/hpcjcl/linelist &&
cut -f2 """ + wdir + "/hpcjcl/hitcount.srt|sort -u >" + wdir + """/hpcjcl/snplist &&
srun --exclusive --nodes=1 --ntasks=1 sh """ + wdir + """/hpcjcl/launchawk.sh &
wait

t=$(ls """ + wdir + """/hpcjcl/tags.[123456789]*|wc -l)
for i in $( seq 1 $t ); do
srun --exclusive --ntasks=1 --nodes=1 perl subsetscorerhits.pl """ + wdir + """  $i &
done
wait

echo \"\" >>""" + wdir + """/hpcjcl/Hheader && cat """ + wdir + "/hpcjcl/Hheader " + wdir + "/hpcjcl/tagreport.* > " + wdir + """/Analysis/HITreport.txt

""")

shellout.close()

os.system("sbatch " + wdir + "/hpcjcl/launchtas.sh")
#system("rm -rf $wdir/hpcjcl/");

'''
print ("Please wait...")

#wait until the job is done before moving on
p1 = Popen(['squeue'], stdout=PIPE)
result = p1.communicate()[0]
while ("pro366" in str(result)):
	p1 = Popen(['squeue'], stdout=PIPE)
	result = p1.communicate()[0]

###############################Start filtering out the 4 resulting files#############################################
if (len(sys.argv) == 7): #user already specified filter args
        percentage = sys.argv[5]
        min = sys.argv[6]
        os.system("python filter_snips.py " + wdir + "/Analysis " + str(percentage) + " " + str(min))

else:
        print "\n"
        i = 0
        while (i == 0): #want to filter?
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
'''
