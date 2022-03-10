#!/usr/bin/perl
#
if ( ! &ReadParse(*input)) {
    print "Content-type: text/plain\n\n";
    print "Problem with reading input\n"
}
#
foreach $key (sort keys(%input)) {
    if ( $key =~ /(\w*)_quote/ ) {
	$input{$key} = "\"".$input{$key}."\"";
    }
    elsif ( $key eq submit_view ) {
	print "Content-type: text/plain\n\n";
    }
    elsif ( $key eq submit_save ) {
	print "Content-type: text/cns\n\n";
    }
}
#
open(CNS_FILE,$input{source_file});
#
$textcount=0;
while ( $line=<CNS_FILE> ) {
    if ($line =~ /^\s*\{===>\}\s*$/) {
	$textarea="textarea".$textcount;
	print "{===>}";
	if ( $input{$textarea} =~ /^\w+(.|\n)*$/ ) {
	    print "\n";
	}
	print "$input{$textarea}";
	if ( $input{$textarea} !~ /^(.|\n)*\n+(\t| )*$/ ) {
	    print "\n";
	}
	until_delimit($line,'\{<===\}');
	print "{<===}\n";
	++$textcount;
    }
    elsif ($line =~ /^\s*\{===>\}\s*(\w+.*)\s*$/) {
	$done=0;
	$subline = $1;
	$outline = "{===>} ";
	while ( ! $done ){
	    if ( $subline =~ 
                /^\s*([\w.\d\-+]*)\s*=\s*([ "()\w\d.:\-+\/=\^><*,]*)(;|$)(.*)$/ ) {
		$variable = $1;
		$value = $2;
		$subline = $4;
		$varout = $variable;
		if ( $value =~ /^\".*\";*\s*$/ ) {
		    $variable = $variable . "_quote";
		}
		$valout = $input{$variable};
		$valout =~ s/^\"\s*\"$/\"\"/gs;
		$valout =~ s/^\"\s*(\w+.*\w+)\s*\"$/\"$1\"/gs;
		$valout =~ s/^\s*(\(.*\))\s*$/$1/gs;
		$prelen = " " x (8 + length($varout));
		$valout =~ s/\n/\n$prelen/g;
		$outline = $outline . "$varout=$valout; ";
	    }
	    else {
		$done=1;
	    }
	}
	print "$outline\n";
	if ($line =~ /^(.*);\s*$/) {
	}
	else {
	    until_delimit($line,';');
	}
    }
    else {
	print "$line";;
    }
}
#
close (CNS_FILE);
#
sub until_delimit {
    local($current,$delimit) = @_;
    $string = '';
    if ( $current =~ /^\s*(.*)$delimit\s*$/ ) {
	$end_char=1;
    }
    elsif ( $current =~ /^\s*(.*)$/ ) {
	$end_char=0;
    }
    if ( ! $end_char ) {
	while ( ! $end_char ) {
	    $_ = <CNS_FILE>;
	    if (/^\s*(.*)$delimit\s*$/) {
		$end_char=1;
	    }
	    elsif (/^\s*(.*)$/) {
		$end_char=0;
	    }
	    if ( ( ! $end_char ) && eof ) {
		print "<CENTER><P><FONT SIZE=+3>\n";
		print "EOF detected while trying to parse input<BR>\n";
		print "Please check the input file - it may be corrupted\n";
		print "</P></FONT></CENTER>\n";
		exit;
	    }
	}
    }
}

# Perl Routines to Manipulate CGI input
# S.E.Brenner@bioc.cam.ac.uk
#
# Copyright 1994 Steven E. Brenner  
# Unpublished work.
# Permission granted to use and modify this library so long as the
# copyright above is maintained, modifications are documented, and
# credit is given for any use of the library.
#
# For more information, see:
#     http://www.bio.cam.ac.uk/web/form.html       
#     http://www.seas.upenn.edu/~mengwong/forms/   

# ReadParse
# Reads in GET or POST data, converts it to unescaped text, and puts
# one key=value in each member of the list "@in"
# Also creates key/value pairs in %in, using '\0' to separate multiple
# selections

# Returns TRUE if there was input, FALSE if there was no input 
# UNDEF may be used in the future to indicate some failure.

# Now that cgi scripts can be put in the normal file space, it is useful
# to combine both the form and the script in one place.  If no parameters
# are given (i.e., ReadParse returns FALSE), then a form could be output.

# If a variable-glob parameter (e.g., *cgi_input) is passed to ReadParse,
# information is stored there, rather than in $in, @in, and %in.

sub ReadParse {
  local (*in) = @_ if @_;
  local ($i, $key, $val);

  # Read in text
  if (&MethGet) {
    $in = $ENV{'QUERY_STRING'};
  } elsif ($ENV{'REQUEST_METHOD'} eq "POST") {
    read(STDIN,$in,$ENV{'CONTENT_LENGTH'});
  }

  @in = split(/&/,$in);

  foreach $i (0 .. $#in) {
    # Convert plus's to spaces
    $in[$i] =~ s/\+/ /g;

    # Split into key and value.  
    ($key, $val) = split(/=/,$in[$i],2); # splits on the first =.

    # Convert %XX from hex numbers to alphanumeric
    $key =~ s/%(..)/pack("c",hex($1))/ge;
    $val =~ s/%(..)/pack("c",hex($1))/ge;

    # Associate key and value
    $in{$key} .= "\0" if (defined($in{$key})); # \0 is the multiple separator
    $in{$key} .= $val;

  }

  return length($in); 
}

# MethGet
# Return true if this cgi call was using the GET request, false otherwise

sub MethGet {
  return ($ENV{'REQUEST_METHOD'} eq "GET");
}
