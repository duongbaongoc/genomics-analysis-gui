#This file is a translation from perl to python of AGREPtaswork7..pl
#Translator: Ngoc Duong
#Date: 05/2019

import sys
import os
from subprocess import PIPE, Popen
#argv[1]=xfile argv[2]=keyfile argv[3]=workingdirectory argv[4]=similarity minimum
inseq = ""
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
        global inseq
	file = open(testfile, 'a')
	position = []
        consens = []
        consens1 = []
        consens2 = []
        consensline = ""
	
	in5 = open(wdir + "/" + newdir + ".d/" + holdtag + ".oneline", 'r')
	#####find true start and stop of auth line
	al1 = in5.readline()
	al2 = al1.split("\t")
	al2[1] = al2[1].rstrip()
	al3 = al2[1]
	alcount = 0
	for al3c in al3:
		if al3c != "-":
			trustrt = alcount
			break
		else:
			alcount +=1
	
	al2_1 = list(al2[1])
	al2_1.reverse()
	rauth = ''.join(al2_1)
	al3r = rauth
	allength = len(al2[1])
	arcount = 0
	for al3rc in al3r:
		if al3rc != "-":
			truend = arcount
			break
		else:
			arcount += 1
	endstart = allength - truend
	in5.close()
	##################################file.write(str(endstart)+" "+str(truend)+"\n")
	in5 = open(wdir + "/" + newdir + ".d/" + holdtag + ".oneline", 'r')
	lin5 = in5.readline()
        while(lin5):
                lin5 = lin5.rstrip()
                consens1.append(lin5)
                lin5 = in5.readline()
        in5.close()
        ###################################for item in consens1:
	###################################	file.write(item + "\n")
	c1lim = len(consens1)
        auth = consens1[0]
        authprts = auth.split('\t')
        authname = authprts[0].split("_")
        shortauthname = authname[0] + "_" + authname[2]
	###################################file.write(str(c1lim) + " " + auth + " " + shortauthname + "\n")
	subpart = authprts[1][trustrt:endstart]
	authpush = shortauthname + "\n" + subpart + "\n"
        consens2.append(authpush)
        authseq = subpart
        austp = len(authseq)
	#####################################file.write(subpart + " " + authpush + " " + str(austp) + "\n")
	#####################################file.write(inseq + "\n")
	inseq1 = ""
	for cx in range(1, c1lim):
        	readin = consens1[cx]
        	subseq = readin.split("\t")
		subpart = subseq[1][trustrt:endstart]
		inseq1 = subpart
        	pushreadline = subseq[0] + "\n" + subpart + "\n"
		###############################file.write(readin + " " + subpart + " " + pushreadline+ "\n")
        	consens2.append(pushreadline)
	
	#if inseq1 == "" then it has value of the latest non "" inseq1 => consistent with perl
	if (not os.path.exists(wdir + "/save")):
		save = open(wdir + "/save", 'w')
		save.close()
	if (inseq1 != ""):
		save = open(wdir + "/save", 'w')
		save.write(inseq1)
		save.close()
	else:
		save = open(wdir + "/save", 'r')
		inseq1 = save.readline()
		save.close()
		
	####################################file.write(authseq + "\n")
	for s in range(austp):
		position.append([0,0,0,0,0,0])
        	if(authseq[s] != "-" and authseq[s].upper() != "A" and authseq[s].upper() != "C" and authseq[s].upper() != "G" and authseq[s].upper() != "T" and authseq[s].upper() != "Z"):
			##########################file.write(inseq1 + "\n")
			if (len(inseq1) > s):
				if(inseq1[s].upper() == "A"):
					position[s][1] += 1
        	       		if(inseq1[s].upper() == "C"):
					position[s][2] += 1
               			if(inseq1[s].upper() == "G"):
					position[s][3] += 1
               			if(inseq1[s].upper() == "T"):
					position[s][4] += 1
               			if(inseq1[s].upper() == "-"):
					position[s][5] += 1
	####################for item in position:
	####################	if 1 in item:
	####################		file.write(str(item.index(1))+ "\n")		

	#######################file.write(str(len(position)) + "\n")
	align = holdtag + "_" + newdir + ".fas"
        for pl in range(austp):
		if (1 not in position[pl]):
			consensline = consensline + "."
			#################file.write(consensline + "\n")
		else:
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
				het = ""
        			consensline = consensline + consenscall
	######################################file.write(consensline + "\n")
	##################################for item in consens2:
	##################################	file.write(item + "\n")
	consensline = consensline + "\n"
        consstring = authname[0] + "_" + rname + "\n" + consensline
        consens2 = [consstring] + consens2
        #bubble sort consens2 on similarity to key file and get hit count
        len_ = 0
	totalreadcnt = 0
        len_ = len(consens2)
	#############################for item in consens2:
	#############################	file.write(item + "\n")
	if(len_ < 3):
		return	
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
					##########################file.write(prt1x[2] + "  " + prt1y[2] + "\n")
					prt1x2 = float(prt1x[2].split("\n")[0])
					prt1y2 = float(prt1y[2].split("\n")[0])
					if(prt1x2 < prt1y2):
							t = consens2[c3x]
							consens2[c3x] = consens2[c3y]
							consens2[c3y] = t				
		for l in consens2:
			out2.write(l)
        	out2.close()
        	
		conline = consensline.rstrip()
        	ecnt = len(conline)
        	contrk = 0
		postrk = -1
        	for conprt in conline:
        		postrk += 1
        		if(authseq[postrk] != "-"):
				contrk += 1
        	
        
        conline = []
        rilfirst = newdir + "_" + holdtag + ".fas"
        ###################new chunk##############
	##unique reads and grep count
	infas = open(wdir + "/" + newdir + ".d/" + align, 'r')
	outseqz = open(wdir + "/" + newdir + ".d/" + align + ".4uniq", 'w')
	holdlines = []
	conid1 = infas.readline()
	conline1 = infas.readline()
	keyid1 = infas.readline()
	keyseq1 = infas.readline()
	inidline = infas.readline()
	while (inidline):
		inseqline = infas.readline()
		outseqz.write(inseqline)
		inidline = infas.readline()
	infas.close()
	outseqz.close()
	##############################################diff file.d
	os.system("sort -u " + wdir + "/" + newdir  + ".d/" + align + ".4uniq >" + wdir + "/" + newdir + ".d/" + align + ".realigned")
	inreal = open(wdir + "/" + newdir + ".d/" + align + ".realigned", 'r')
	realout = open(wdir + "/" + newdir + ".d/" + align + ".realigned2", 'w')
	x = 1
	totalrecount = 0
	keyseq1 = keyseq1.rstrip()
	inrealseq = inreal.readline()
	while (inrealseq):
		holdlines.append(inrealseq)
		inrealseq = inrealseq.rstrip()
		realprts = inrealseq
		inrealseqnodash = ""
		for rps in realprts:
			if (rps != "-"):
				inrealseqnodash = inrealseqnodash + rps
		realcnt = Popen(['grep', '-c', inrealseqnodash, wdir + "/" + newdir + ".d/" + rname], stdout=PIPE)
		realcnt = int(realcnt.communicate()[0].rstrip())
		inrealseqnodash = ""
		totalrecount += realcnt
		uselen = len(inrealseq)
		comdis = levenshtein(keyseq1,inrealseq)-ambcnt
		disfract = (int((1-(comdis*1.0/uselen))*1000.0))/1000.0
		if disfract == 1.0:
			disfract = 1
		printline = ">" + str(x) + "_" + str(realcnt) + "_" + str(disfract)
		x += 1
		realout.write(printline + "\t" + inrealseq + "\n")
		inrealseq = inreal.readline()
	realout.close()
	#############################################diff file.d
	os.system("sort -t_ -k3,3rn -k2,2rn " + wdir + "/" + newdir + ".d/" + align + ".realigned2>" + wdir + "/" + newdir + ".d/" + align + ".realignedt && sed \'s#\\t#\\n#\' " + wdir + "/" + newdir + ".d/" + align + ".realignedt >" + wdir + "/" + newdir + ".d/" + align + ".realigned2")
	holdlinescnt = len(holdlines)
	conline1 = conline1.rstrip()
	conlineprts = conline1
	clpos = -1
	keyseqprts = keyseq1
	keygapcnt = 0
	##############################for item in conlineprts:
	#############################	file.write(item + "\n")
	for clprt in conlineprts:
		clpos += 1
		if (keyseqprts[clpos] == "-"):
			keygapcnt += 1
		if (clprt != "."):
			allelecnt = 0
			Ac = 0
			Cc = 0
			Gc = 0
			Tc = 0
			delc = 0
			het = ""
			for hlline in range(holdlinescnt):
				linesplit = holdlines[hlline]
				if (linesplit[clpos] == "A"):
					Ac += 1
				if (linesplit[clpos] == "C"):
					Cc += 1
				if (linesplit[clpos] == "G"):
					Gc += 1
				if (linesplit[clpos] == "T"):
					Tc += 1
				if (linesplit[clpos] == "-"):
					delc += 1
			if (Ac > 0):
				allelecnt += 1
			if (Cc > 0):
				allelecnt += 1
			if (Gc > 0):
				allelecnt += 1
			if (Tc > 0):
				allelecnt += 1
			if (delc > 0):
				allelecnt += 1
			if (allelecnt > 2):
				het = "N"
			elif (allelecnt > 1):
				if (Ac > 0 and Cc > 0):
					het = "M"
				if (Ac > 0 and Gc > 0):
					het = "R"
				if (Ac > 0 and Tc > 0):
					het = "W"
				if (Ac > 0 and delc > 0):
					het = "X"
				if (Cc > 0 and Gc > 0):
					het = "S"
				if (Cc > 0 and Tc > 0):
					het = "Y"
				if (Cc > 0 and delc > 0):
					het = "X"
				if (Gc > 0 and Tc > 0):
					het = "K"
				if (Gc > 0 and delc > 0):
					het = "X"
				if (Tc > 0 and delc > 0):
					het = "X"
			elif (allelecnt == 1):
				if (Ac > 0):
					het = "A"
				if (Cc > 0):
					het = "C"
				if (Gc > 0):
					het = "G"
				if (Tc > 0):
					het = "T"
				if (delc > 0):
					het = "X"
			conlineprts = conlineprts[0:clpos] + het + conlineprts[(clpos + 1):]
			ungappedpos = clpos + 1 - keygapcnt
			tagpos = holdtag + "_" + str(ungappedpos)
			rept.write(newdir + "\t" + tagpos + "\t" + holdtag + "\t" + str(ungappedpos) + "\t" + het + "\n")
	######################################diff file.d		
	realout1 = open(wdir + "/" + newdir + ".d/" + align + ".realigned3", 'w')
	realout1.write(conid1)
	for cpo in conlineprts:
		realout1.write(cpo)
	realout1.write("\n" + keyid1 + keyseq1 + "\n")
	inreal.close()
	realout1.close()
	os.system("cat " + wdir + "/" + newdir + ".d/" + align + ".realigned3 " + wdir + "/" + newdir + ".d/" + align + ".realigned2>" + wdir + "/" + newdir + ".d/" + align)
	hits.write(rname + "\t" + holdtag + "\t" + str(totalrecount) + "\n")
	os.system("cp " + wdir + "/" + newdir + ".d/" + align + " " + wdir + "/Analysis/Markers/" + holdtag + ".d/" + rilfirst)
	######################################diff file.d
	file.close()
     



if __name__ == "__main__":
	global inseq
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
		if not os.path.exists(wdir + "/" + newdir + ".d"):
			os.makedirs(wdir + "/" + newdir + ".d")
		
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
		#####grep out valid seqs######
		inkeys = open(wdir + "/hpcjcl/cleankey", 'r')
		inkeyid = inkeys.readline()
		while(inkeyid):
			inkeyid = inkeyid.rstrip()
			inkeyseq = inkeys.readline().rstrip()
			holdtag = inkeyid[1:]
			if not os.path.exists(wdir + "/Analysis/Markers/" + holdtag + ".d"):
				os.makedirs(wdir + "/Analysis/Markers/" + holdtag + ".d")
			
			putname = open(wdir + "/" + newdir + ".d/" + holdtag + ".hits.tmp", 'w')
			putname.write(inkeyid + "\n" + inkeyseq + "\n")
			
			seqstrt = inkeyseq[:15]
			keylen = len(inkeyseq)
			if ((keylen*minsim) - int(keylen*minsim) >= 0.5):
				allowedfract = keylen - (int(keylen*minsim)+1)
			else:
				allowedfract = keylen - (int(keylen*minsim))
			if (allowedfract > 8):
				allowedfract = 8
			agout1 = Popen(['agrep', '-'+str(allowedfract), inkeyseq, wdir + '/' + newdir + '.d/' + newdir + '.fou'], stdout = PIPE)
			agout2 = Popen(['grep', '-v', 'Grand'], stdin=agout1.stdout, stdout=PIPE)
			agout3 = Popen(['sed', 's#^.*'+ seqstrt + '#' + seqstrt + '#'], stdin=agout2.stdout, stdout=PIPE)
			agout4 = Popen(['sed', 's#^q##'], stdin=agout3.stdout, stdout=PIPE)
			agout5 = agout4.communicate()[0]
			
			#reformat agout because Popen does not work properly on output of sed
			agout = []
			if len(agout5) > 0:
				temp_seq = ""
				for item in agout5:
					item = item.rstrip()
					if item == "" or item == " ": #signilize the end of a seq
						agout.append(temp_seq)
						temp_seq = ""
					else:
						temp_seq += item
			#done reformating agout
			
			filelen = len(agout)
			#if (filelen==0):
			#	putname.close()
			#	os.unlink(wdir + "/" + newdir + ".d/" + holdtag + ".hits.tmp")
			#	continue
			

			linecnt = 0
			for lnout in agout:
				lnout = lnout.rstrip()
				linecnt += 1
				putname.write(">" + str(linecnt) + "\n" + lnout + "\n")


			putname.close()			
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
				
				if len(tagrd) < len(inseq):
					uselen = len(tagrd)
					lendiff = abs(len(tagrd) - len(inseq))	
				else:
					uselen = len(inseq)

				if len(inseq) > len(tagrd):
					comdis = levenshtein(tagrd,inseq)-ambcnt-lendiff
				else:
					comdis = levenshtein(tagrd, inseq) -ambcnt
				
				disfract = (int((1-(comdis*1.0/uselen))*1000.0))/1000.0
				inid2 = inid + "_" + str(disfract)
				if (disfract >= minsim):
					holdids.append(inid2)
					holdseqs.append(inseq)
				inid = intmp.readline()
			
			seqcnt = len(holdseqs)
			totalcount = 0
			for scnt1 in range(seqcnt-1):
				for scnt2 in range((scnt1+1),(seqcnt)):
					if (holdseqs[scnt1] == holdseqs[scnt2]):
						holdids[scnt2] += "+"
						holdseqs[scnt2] += "+"

			#holdids (3): matching as long as do not include items of holdids that has "+"
			#recount and get total read count
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

			
			#insert a "" item at the end of holdids to be consistant with the perl code
			holdids.append("")
			holdseqs.append("")
			
			trkseqs = 0
			fnlseqscnt = len(holdseqs)
			
			while (trkseqs < fnlseqscnt):
				qseq = holdseqs[trkseqs].rstrip()
				if (len(qseq) > 0):
					gpcnt = Popen(["grep", "-c", qseq, wdir + "/" + newdir + ".d/" + rname], stdout = PIPE)
					gpcnt = int(gpcnt.communicate()[0].split()[0])
					totalcount += gpcnt
					idbits = holdids[trkseqs].split('_')
					if idbits[1] == "1.0":
						idbits[1] = "1"
					holdids[trkseqs] = idbits[0] + "_" + str(gpcnt) + "_" + idbits[1]
				trkseqs += 1
					
			trkids = -1
			for r1 in holdids:
				trkids += 1
				idbits = r1.split("_")
				if (len(idbits) > 1 and float(idbits[1]) <= totalcount*0.02 ):
					holdids[trkids] = ""
					holdseqs[trkids] = ""
			
			holdids.insert(0, tagid)
			holdseqs.insert(0, tagrd)
			
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
		os.system("rm " + wdir + "/save " + wdir + "/" + newdir + ".d/*.tmp " + wdir + "/" + newdir + ".d/*.onelin* " + wdir + "/" + newdir + ".d/*.realigned* " + wdir + "/" + newdir + ".d/*.4uniq " + wdir + "/" + newdir + ".d/*.hits2 " + wdir + "/" + newdir + ".d/*.fasta " + wdir + "/" + newdir + ".d/" + rname + ".cseeds " + wdir + "/" + newdir + ".d/" + rname + ".fou " + wdir + "/" + newdir + ".d/" + rname + ".out " + wdir + "/" + newdir + ".d/" + rname + ".out.clstr " + wdir + "/" + newdir + ".d/" + rname + ".outoneline " + wdir + "/" + newdir + ".d/" + rname + ".out.outnames " + wdir + "/" + newdir + ".d/" + rname + ".out.outseqs " + wdir + "/" + newdir + ".d/" + rname + ".trimmed.out.clstr " + wdir + "/" + newdir + ".d/" + rname + ".trimmed.out.clstr.keeplist")
		os.system("mv " + wdir + "/" + newdir + ".d " + wdir + "/Analysis/Genotypes/")
			
		fid = xfile.readline()
	print ("this should be printed n times where n is the number of files to analyze")	
#####getconsensus function/definition is moved to top because of python order of execution
