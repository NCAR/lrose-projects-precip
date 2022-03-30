#!/usr/bin/perl

use Getopt::Std;
use Time::Local;

#  quick-and-dirty routine to re-format output from ncdump
#  reformatting is done to provide reports with all variables from
#  a given time on a single line.
# 
#		RAR 01-Jun-2015
#
#  Change the variable list in the ncdump call, as necessary.
#  This routine will accept multiple files as input.  Output is
#  to stdout.
#
#  Written for S-Pol weather station.
#

# for $params, always include base_time and time_offset as the first two params!


$tzone_offset = 0;
$tz = "UTC";
#$tzone_offset = -6;
#$tz = "MDT";
$params = "base_time,time,tdry,rh,wspd,wu,wv";
#$params = "batt,base_time,time,tdry,rh,pres,wspd,wdir,wmax,raina";

$tzone_offset *= 3600;

for (@ARGV) {
    push @fnames, $_;
}

for(@fnames) {
    chomp;
    $ready=0;
    open INP, "ncdump -v $params $_ | ";
	ITER: while (<INP>) {
	    chomp;
	    $line = $_;
	    $line =~ s/\s+//g;		# remove blanks in line
	    $line =~ s/,$|\;$|\}$//;	# remove any typical trailing chars
#	    $line =~ s/;|\s+$//;
	    next ITER if ($line =~ m/^$/); 
	    if (m/base_time =/) { 	# search forward until base_time
		($junk,$temp) = split('=',$line,2);
		$tbase = $temp;
		$ready=1;
#		printf("base time is %s-\n\n",$tbase);
		next ITER;
	    }
	    next ITER if ($ready == 0);

	    if ( $line =~ m/=/) {	# find all variables
		($temp,$line) = split('=',$line,2);
		push @vnames, $temp;
		push @voffs, $#vars;
	    }
	    $lastind = $#vars;
#	    print $line, "\n";

	    @stuff = split( /,/,$line);
	    push @vars, @stuff;
	}

#    print $#vnames, "\n";
#    printf("first var offset = %s; second = %s\n", @voffs[0], @voffs[1]);
#    print $#vars, "\n";

    for ($j=0;$j<=@voffs[1];$j++) {
	($sec,$min,$hr,$day,$mon,$yr)=gmtime($tbase + $tzone_offset + @vars[$j]);
#	($sec,$min,$hr,$day,$mon,$yr)=localtime($tbase + @vars[$j]);
	@vars[$j] = sprintf("%04d%02d%02d  %02d%02d",1900+$yr,1+$mon,$day,$hr,$min);
    }
    @vnames[$0] = " $tz Date/Time";

    printf("\n");
    for ($i=0; $i<=$#vnames; $i++) {
	printf("%11s",@vnames[$i]);
    }
    printf("\n\n");
    for ($j=0;$j<=@voffs[1];$j++) {
	for ($i=0; $i<=$#vnames; $i++) {
	    printf(" %10s",@vars[1+@voffs[$i]+$j]);
	}
	printf("\n");
    }
	    
    splice @vars, 0;		# null-out the arrays
    splice @voffs, 0;
    splice @vnames, 0;
    close INP;
}
exit;
