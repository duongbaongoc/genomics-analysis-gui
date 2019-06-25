#This file is a translation from perl to python of taswork.pl
#Translator: Ngoc Duong
#Date: 01/16/2019

import sys
import os
from subprocess import PIPE, Popen
import random #to test, should del
#argv[1]=xfile argv[2]=keyfile argv[3]=workingdirectory argv[4]=similarity minimum

#help function to find Levenshtein distaince
def levenshtein(s1, s2):
	if len(s1) < len(s2):
		return levenshtein(s2, s1)
	if len(s2) == 0:
		return len(s1)
	previous_row = range(len(s2) + 1)
	for i, c1 in enumerate(s1):
		current_row = [i + 1]
		for j, c2 in enumerate(s2):
			insertions = previous_row[j + 1] + 1
			deletions = current_row[j] + 1
			substitutions = previous_row[j] + (c1 != c2)
			current_row.append(min(insertions, deletions, substitutions))
		previous_row = current_row
	return previous_row[-1]


def getconsensus(testfile):#remove test file
        file = open(testfile, 'a')
	position = []
        consens = []
        consens1 = []
        consens2 = []
        consensline = ""

	in5 = open(wdir + "/" + newdir + ".d/" + holdtag + ".oneline", 'r')
        lin5 = in5.readline()
        while(lin5):
                lin5 = lin5.rstrip()
                consens1.append(lin5)
                lin5 = in5.readline()
        in5.close()
	
        c1lim = len(consens1)
        auth = consens1[0]
        authprts = auth.split('\t')
	
        authname = authprts[0].split("_")
        shortauthname = authname[0] + "_" + authname[2]
        authpush = shortauthname + "\n" + authprts[1] + "\n"
        consens2.append(authpush)
        authseq = authprts[1]
        austp = len(authseq)
        
        for cx in range(1, c1lim):
        	readin = consens1[cx]
        	subseq = readin.split("\t")
        	inseq = subseq[1]
        	pushreadline = subseq[0] + "\n" + subseq[1] + "\n"
        	consens2.append(pushreadline)
        	for s in range(austp):
			position.append([0,0,0,0,0,0])
        		if(authseq[s] != "-" and authseq[s].upper() != "A" and authseq[s].upper() != "C" and authseq[s].upper() != "G" and authseq[s].upper() != "T" and authseq[s].upper() != "Z"):
                		if(inseq[s].upper() == "A"):
					position[s][1] += 1
                		if(inseq[s].upper() == "C"):
					position[s][2] += 1
                		if(inseq[s].upper() == "G"):
					position[s][3] += 1
                		if(inseq[s].upper() == "T"):
					position[s][4] += 1
                		if(inseq[s].upper() == "-"):
					position[s][5] += 1
	
	align = holdtag + "_" + newdir + ".fas"
        for pl in range(austp):
		if (pl >= len(position)):#?
			consensline = consensline + "."
		if (pl < len(position)):
        		if(position[pl][0] == 0 and position[pl][1] == 0 and position[pl][2] == 0 and position[pl][3] == 0 and position[pl][4] == 0 and position[pl][5] == 0):
				consensline = consensline + "."
			else:
        			A = position[pl][1]
				C = position[pl][2]
				G = position[pl][3]
				T = position[pl][4]
				del_ = position[pl][5]
				mxallele = ""
        			mx = 0
        			if(A > mx):
					mx = A
					mxallele = "A"
        			if(C > mx):
					mx = C
					mxallele = "C"
        			if(G > mx):
					mx = G
					mxallele = "G"
        			if(T > mx):
					mx = T
					mxallele = "T"
        			if(del_ > mx):
					mx = del_
					mxallele = "d"

        			het = mxallele
        			allbases = [A, C, G, T, del_]
				allbases.sort(reverse = True)
				srtdall = allbases
        			second = srtdall[1]
        			allelecnt = 0
        			if(A > 0):
					allelecnt += 1
        			if(C > 0):
					allelecnt += 1
        			if(G > 0):
					allelecnt += 1
        			if(T > 0):
					allelecnt += 1
        			if(del_ > 0):
					allelecnt += 1
       		 		if(allelecnt > 2):
					het = "N"
        			elif(allelecnt >1):
        				if(A > 0 and C > 0):
						het = "M"
        				if(A > 0 and G > 0):
						het = "R"
        				if(A > 0 and T > 0):
						het = "W"
        				if(A > 0 and del_ > 0):
						het = "X"
        				if(C > 0 and G > 0):
						het = "S"
   		     			if(C > 0 and T > 0):
						het = "Y"
        				if(C > 0 and del_ > 0):
						het = "X"
        				if(G > 0 and T > 0):
						het = "K"
        				if(G > 0 and del_ > 0):
						het = "X"
        				if(T > 0 and del_ > 0):
						het = "X"
        
        			consenscall = het
        			consensline = consensline + consenscall
        consensline = consensline + "\n"
        consstring = authname[0] + "_" + rname + "\n" + consensline
        consens2 = [consstring] + consens2
        #bubble sort consens2 on similarity to key file and get hit count
        len_ = 0
	totalreadcnt = 0
        len_ = len(consens2)
	
        if(len_ >= 3):
	        out2 = open(wdir + "/" + newdir + ".d/" + align, 'w')
	        if(len_ == 3):
			prt1x = consens2[2].split("_")
			totalreadcnt = prt1x[1]
		else:
        		for c3x in range(2, len_ - 1):
				prt1x = consens2[c3x].split("_")
				totalreadcnt += int(prt1x[1])
        			for c3y in range((c3x+1), len_):
					prt1y = consens2[c3y].split("_")
					if(c3y == (len_-1) and (c3x == (len_-2))):
						totalreadcnt += int(prt1y[1])
						
		for l in consens2:
			out2.write(l)
        	if(rname != "" and holdtag != "" and totalreadcnt > 0):
			hits.write(rname + "\t" + holdtag + "\t" + str(totalreadcnt) + "\n")
        	out2.close()
        	
		conline = consensline.rstrip()
        	ecnt = len(conline)
        	contrk = 0
		postrk = -1
        	for conprt in conline:
        		postrk += 1
        		if(authseq[postrk] != "-"):
				contrk += 1
        		if(conprt != "." and postrk < ecnt-1):
        			tagpos = holdtag + "_" + str(contrk)
				rept.write(newdir + "\t" + tagpos + "\t" + holdtag + "\t" + str(contrk) + "\t" + conprt + "\n")
        	
        
        conline = []
        rilfirst = newdir + "_" + holdtag + ".fas"
        os.system("cp " + wdir + "/" + newdir + ".d/" + align + " " + wdir + "/Analysis/Markers/" + holdtag + ".d/" + rilfirst)
	file.close()
     



if __name__ == "__main__":
	#print out help message
	if (len(sys.argv) == 1 or sys.argv[1] == "-h" or sys.argv[1] == "--help"):
		print "How to run: python taswork.py [xfile] [cleankey file] [directory of raw data file] [mininal similarity]"
		print "Example   : python taswork.py   x1         cleankey             PRO366                   1.0" 
		sys.exit()
	
	#get some command arguments
	minsim = float(sys.argv[4])
	xfile = open(sys.argv[1], 'r')
	wdir = sys.argv[3]
	
	fid = xfile.readline()
	while(fid):
		fid = fid.rstrip()
		#find ril name and create directory for it.	
		rname = os.path.basename(fid)	
		newdir = rname
		#if not (os.path.isfile(wdir + "/" + newdir)):
		#	fid = xfile.readline()
		#	continue
		#this may cause an error	
		
		if not os.path.exists(wdir + "/" + newdir + ".d"):
			os.makedirs(wdir + "/" + newdir + ".d")
		
		#system("cp $fid $wdir/$newdir.d/");
		inraw = open(fid, 'r')
		firstline = inraw.readline()
		typchk = firstline[0]
		if (typchk == '>'):
			ftyp = 'a'
		elif (typchk == '@'):
			ftyp = 'q'
		else:
			print ("\n\n FILE MUST BE FASTA OR FASTQ, STARTING WITH > OR @. FIRST CHARACTER OF " + rname + " is " + str(typchk) + "\n\n")
			sys.exit()

		outraw = open(wdir + "/" + newdir + ".d/" + rname, 'w')
		rwcnt = 1
		newrname = str(rwcnt) + "_" + rname
		firstread = inraw.readline().rstrip()
		if (len(firstread) >=37):
			outraw.write(">" + newrname + "\n")
			outraw.write(firstread + "\n")
		if (ftyp == 'q'):
			inrd3 = inraw.readline()
			inrd4 = inraw.readline()
		inrd = inraw.readline()
		while(inrd):
			inrd = inrd.rstrip()
			rwcnt += 1
			newrname = str(rwcnt) + "_" + rname
			inrd2 = inraw.readline().rstrip()
			if (len(inrd2) >=37):
				outraw.write(">" + newrname + "\n")
				outraw.write(inrd2 + "\n")
			if (ftyp == 'q'):
				inrd3 = inraw.readline()
				inrd4 = inraw.readline()
			inrd = inraw.readline()
		inraw.close()
		outraw.close()
		
		# (marking this line for readability)
		os.system("cd-hit-est -M 4096 -c 1 -r 0 -d 0 -i " + wdir + "/" + newdir + ".d/\\" + rname + " -o " + wdir + "/" + newdir + ".d/\\" + rname + ".out && LC_ALL=C grep -B1 \"^>\" " + wdir + "/" + newdir + ".d/\\" + rname + ".out.clstr|grep -v \^--$ |sed \'s/  / /g\'|sed 's/Cluster /Cluster_/g'> " + wdir + "/" + newdir + ".d/\\" + rname + ".cseeds && tail -1 " + wdir + "/" + newdir + ".d/\\" + rname + ".out.clstr>>" + wdir + "/" + newdir + ".d/\\" + rname + ".cseeds && sed -i 's/Cluster /Cluster_/g' " + wdir + "/" + newdir + ".d/\\" + rname + ".out.clstr")
		
		os.system("LC_ALL=C grep -v \"%\" " + wdir + "/" + newdir + ".d/\\" + rname + ".out.clstr>" + wdir + "/" + newdir + ".d/\\" + rname + ".trimmed.out.clstr")
		rept = open(wdir + "/" + newdir + ".d/" + rname + ".snps.txt", 'w')
		hits = open(wdir + "/" + newdir + ".d/" + rname + ".hits.txt", 'w')
		
		
		os.system("grep -v \"^>\" " + wdir + "/" + newdir + ".d/" + rname + ".trimmed.out.clstr|tr \' \' \'\\t\' | cut -f1,3|cut -d\"_\" -f1|awk \'{print $2\" \"($1+1)}\'|sed \'s#^>##\'|sort --field-separator=\' \' -k1,1n >" + wdir + "/" + newdir + ".d/" + rname + ".trimmed.out.clstr.keeplist && sed \'N;s/\\n/\\t/\' " + wdir + "/" + newdir + ".d/" + rname + ".out|cut -d\"_\" -f1>" + wdir + "/" + newdir + ".d/" + rname + ".out.outnames && sed \'N;s/\\n/\\t/\' " + wdir + "/" + newdir + ".d/" + rname + ".out|cut -f2 > " + wdir + "/" + newdir + ".d/" + rname + ".out.outseqs && paste " + wdir + "/" + newdir + ".d/" + rname + ".out.outnames " + wdir + "/" + newdir + ".d/" + rname + ".out.outseqs|tr \' \' \'\\t\'|sed 's#>##'|sort -k1,1n >" + wdir + "/" + newdir + ".d/" + rname + ".outoneline && join " + wdir + "/" + newdir + ".d/" + rname + ".trimmed.out.clstr.keeplist " + wdir + "/" + newdir + ".d/" + rname + ".outoneline|sed \'s#^#>#'|sed \'s# #_#\'|tr \' \' \'\\n\' | sed \'s#^[ACGT]#q&#\' >" + wdir + "/" + newdir + ".d/" + rname + ".fou")
	
		
		#fou has been built
		#####grep out valid seqs######a
		inkeys = open(wdir + "/hpcjcl/cleankey", 'r')
		inkeyid = inkeys.readline()
		while(inkeyid):
			inkeyid = inkeyid.rstrip()
			inkeyseq = inkeys.readline().rstrip()
			inkeyprts = inkeyseq
			cnt5p = 0	#number of bases before the ambiguity code
			for in5 in inkeyprts:
				if(in5 != 'A' and in5 != 'C' and in5 != 'G' and in5 != 'T'):
					end5p = cnt5p	#end5p = index of the ambiguity code
					break
				else:
					cnt5p += 1
			lastbase = len(inkeyseq) - 1
			countdown = lastbase #countdown starts at the last index of the sequence
			
			if (end5p == countdown):
				errout = open(wdir + "/Analysis/Error.log", 'a')
				errout.write(inkeyid + " lacks ambiguity codes\n")
				errout.close()
				inkeyid = inkeys.readline()
				continue
			
	
			while True:
				if (inkeyprts[countdown] != 'A' and inkeyprts[countdown] != 'C' and inkeyprts[countdown] != 'G' and inkeyprts[countdown] != 'T'):
					end3p = countdown+1
					countdown = 0
				else:
					countdown -= 1
				if (countdown == 0):
					break
			
			tag5p = inkeyseq[0:end5p]
			tag3p = inkeyseq[end3p:]
			
			holdtag = inkeyid[1:]
			if not os.path.exists(wdir + "/Analysis/Markers/" + holdtag + ".d"):
				os.makedirs(wdir + "/Analysis/Markers/" + holdtag + ".d")
			
			putname = open(wdir + "/" + newdir + ".d/" + holdtag + ".hits.tmp", 'w')
			putname.write(inkeyid + "\n" + inkeyseq + "\n")
			putname.close()
			
			os.system("grep -B1 " + tag5p + " " + wdir + "/" + newdir + ".d/" + newdir + ".fou|grep -v ^--$ >" + wdir + "/" + newdir + ".d/" + holdtag + ".1 && grep -B1 " + tag3p + " " + wdir + "/" + newdir + ".d/" + holdtag + ".1 |grep -v ^--$ >" + wdir + "/" + newdir + ".d/" + holdtag + ".2 && sed 's#^.*" + tag5p + "#" + tag5p + "#' " + wdir + "/" + newdir + ".d/" + holdtag + ".2|sed 's#" + tag3p + ".*$#" + tag3p + "#'>>" + wdir + "/" + newdir + ".d/" + holdtag + ".hits.tmp")
			
			#############################
			#collapse the file to unique reads with new counts###########		
			holdids = []
			holdseqs = []
			intmp = open(wdir + "/" + newdir + ".d/" + holdtag + ".hits.tmp", 'r')
			tagid = intmp.readline().rstrip()
			tagrd = intmp.readline().rstrip()
			tagrdprts = tagrd
			ambcnt = 0	
			for t in tagrdprts:
				if (t != 'A' and t != 'C' and t != 'G' and t != 'T'):
					ambcnt += 1
			
			if (ambcnt == 0):
				inkeyid = inkeys.readline()
				continue

			
			inid = intmp.readline()
			while (inid):
				inid = inid.rstrip()
				inseq = intmp.readline().rstrip()
				comdis = levenshtein(tagrd,inseq)-ambcnt
				inid2 = inid + "_" + str(comdis)
				if (comdis == 0):
					holdids.append(inid2)
					holdseqs.append(inseq)
				inid = intmp.readline()
			
			seqcnt = len(holdseqs)
			totalcount = 0
			for scnt1 in range(seqcnt-1):
				for scnt2 in range((scnt1+1),(seqcnt)):
					if (holdseqs[scnt1] == holdseqs[scnt2]):
						id1prts = holdids[scnt1].split('_')
						id2prts = holdids[scnt2].split('_')
						id1prts[1] = int(id1prts[1]) + int(id2prts[1])
						holdids[scnt1] = id1prts[0] + "_" + str(id1prts[1]) + "_" + id1prts[2]
						holdids[scnt2] += "+"
						holdseqs[scnt2] += "+"
			#holdids (3): matching as long as do not include items of holdids that has "+"
			#recount and get total read count
			trkseqs = 0
			fnlseqscnt = len(holdseqs)
			
			while (trkseqs < fnlseqscnt):
				qseq = holdseqs[trkseqs].rstrip()
				if ('+' not in qseq):
					gpcnt = Popen(["grep", "-c", qseq, wdir + "/" + newdir + ".d/" + rname], stdout = PIPE)
					gpcnt = int(gpcnt.communicate()[0].split()[0])
					totalcount += gpcnt
					idbits = holdids[trkseqs].split('_')
					holdids[trkseqs] = idbits[0] + "_" + str(gpcnt) + "_" + idbits[2]
				trkseqs += 1
					
			trkids = -1
			for r1 in holdids:
				trkids += 1
				idbits = r1.split("_")
				if (len(idbits) > 1 and float(idbits[1]) <= totalcount*0.02 ):
					holdids[trkids] = ""
					holdseqs[trkids] = ""
			
			#replace items that have "+" by "" to be consistant with the perl code
			idx = 0
			while (idx < len(holdids)):
				if ('+' in holdids[idx]):
					holdids[idx] = ""
				idx += 1
			idx = 0
			while (idx < len(holdseqs)):
				if ('+' in holdseqs[idx]):
					holdseqs[idx] = ""
				idx += 1

			holdids.insert(0, tagid)
			holdseqs.insert(0, tagrd)

			#insert a "" item at the end of holdids to be consistant with the perl code
			holdids.append("")
			holdseqs.append("")

			howmanyaligns = len(holdids)
			if(howmanyaligns == 1):
				inkeyid = inkeys.readline()
				continue
			
			outseq = open(wdir + "/" + newdir + ".d/" + holdtag + ".hits2", 'w')
			for prntseq in range(seqcnt+2):
				if(prntseq < len(holdseqs) and holdseqs[prntseq] != ""):
					outseq.write(holdids[prntseq] + "\n" + holdseqs[prntseq] + "\n")
			intmp.close()
			outseq.close()
			
			#process one tag
			
			rawalignname = newdir + "_" + holdtag + ".RAW" + ".align" + ".fasta"
			os.system("muscle -in "+ wdir + "/" + newdir + ".d/" + holdtag + ".hits2 -out " + wdir + "/" + newdir + ".d/" + rawalignname)
					
			in4 = open(wdir + "/" + newdir + ".d/" + rawalignname, 'r')
			out1 = open(wdir + "/" + newdir + ".d/" + holdtag + ".onelineraw", 'w')
			
			line1 = in4.readline().rstrip()
			if(line1[1:] == holdtag):
				line1 = line1 + "_1000000_key"
				out1.write(line1 + "\t")
			else:
				out1.write(line1 + "\t")
			
			lin4 = in4.readline()
			while(lin4):
				lin4 = lin4.rstrip()
				chkstrt = lin4[0]
				if(chkstrt == ">"):
					if(lin4[1:] == holdtag):
						lin4 = lin4 + "_1000000_key"
						out1.write("\n" + lin4 + "\t")
					else:
						out1.write("\n" + lin4 + "\t")
				else:
					out1.write(lin4)
				lin4 = in4.readline()
			
			out1.close()
			in4.close()
			
			os.system("sort -t_ -k2,2rn " + wdir + "/" + newdir + ".d/" + holdtag + ".onelineraw>" + wdir + "/" + newdir + ".d/" + holdtag + ".oneline")
			getconsensus(wdir + "/" + newdir + ".d/test")
			
			inkeyid = inkeys.readline() #end of while(inkeyid)
		
		hits.close()
		rept.close()
			
		os.system("rm " + wdir + "/" + newdir + ".d/*.tmp " + wdir + "/" + newdir + ".d/*.onelin* " + wdir + "/" + newdir + ".d/*.1 " + wdir + "/" + newdir + ".d/*.2 " + wdir + "/" + newdir + ".d/*.hits2 " + wdir + "/" + newdir + ".d/*.fasta " + wdir + "/" + newdir + ".d/" + rname + ".cseeds " + wdir + "/" + newdir + ".d/" + rname + ".fou " + wdir + "/" + newdir + ".d/" + rname + ".out " + wdir + "/" + newdir + ".d/" + rname + ".out.clstr " + wdir + "/" + newdir + ".d/" + rname + ".outoneline " + wdir + "/" + newdir + ".d/" + rname + ".out.outnames " + wdir + "/" + newdir + ".d/" + rname + ".out.outseqs " + wdir + "/" + newdir + ".d/" + rname + ".trimmed.out.clstr " + wdir + "/" + newdir + ".d/" + rname + ".trimmed.out.clstr.keeplist")
		os.system("mv " + wdir + "/" + newdir + ".d " + wdir + "/Analysis/Genotypes/")
		
		fid = xfile.readline()
	print ("this should be printed n times where n is the number of files to analyze")	
#####getconsensus function/definition is moved to top because of python order of execution
