#ARGV0is working directory ARGV1 is a serial number Call this script with #bashlaunchsubsetscorer.sh
open $snp,'<',"$ARGV[0]/hpcjcl/tags.$ARGV[1]" || die "no snplist";
open $line,'<',"$ARGV[0]/hpcjcl/linelist" || die "no linelist";
@lines=<$line>;close $line;
open $out,'>',"$ARGV[0]/hpcjcl/tagreport.$ARGV[1]";
while ($eachtag=<$snp>)
{chomp $eachtag;
	@tagpos=split /_/,$eachtag;
        $clocation=`LC_ALL=C grep -w $tagpos[0] $ARGV[0]/hpcjcl/ChromoLocations`;
	if(length $clocation>0){$clshort=substr($clocation,0,((length $clocation)-2));print $out "$clshort";}else{print $out "$tagpos[0]\t-\t-\t-";}
        system("LC_ALL=C grep -w $eachtag $ARGV[0]/hpcjcl/hitcount.srt >$ARGV[0]/hpcjcl/tmplist.$ARGV[1]");
        foreach $a (@lines)
        {
                chomp $a;
                @call=`LC_ALL=C grep -w $a $ARGV[0]/hpcjcl/tmplist.$ARGV[1]`;
        $calls=scalar @call;
        if($calls == 0){print $out "\t-";}else{@calla=split /\t/,$call[0];chop $calla[2];print $out "\t$calla[2]";}
        }
print $out "\n";
}
unlink "$ARGV[0]/hpcjcl/tmplist.$ARGV[1]";
close $out;
