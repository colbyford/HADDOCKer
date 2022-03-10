#!/usr/bin/perl
# <!--
$this_cgi = 'cns_inp2form_0.3.cgi';
$modified = 'Last modified 1/30/98 J. Reklaw';
#
#
# this will need to be changed if installed at another site
#
$www_root = '/software/haddock/protocols';
#
$input_dir = $www_root . '/software/cns_1.1/cns_solve_1.1/inputs';
$tmp_dir = '/usr/tmp/cns/inputs';
$tmplog = $tmp_dir . '/access.log';
#
$icon_dir = '/software/cns_1.1/cns_solve_1.1/doc/html/icons';
#
$form2inp = 'cns_form2inp_0.3.cgi';

########## GLOBAL DEFINITIONS ##########

  $NUMBERED = 'numbered';	# user keyword for numbered rows and cols

# FORMATTING PREFERENCES:

  $COLOR='#FFDEAD';	# color of the heading blocks
  $ALIGN='RIGHT';	# align documentation right
  $DOCMAX=200;	# if documentation > DOCMAX then fill whole row
  $A_FEW=3;	# if choices < A_FEW then selection list else radio buttons
  $BIG_SIZE=30;	# default size for big string fields (filenames) -- was 50
  $STR_SIZE=15;		# default size for string fields
  $NUM_SIZE=8;		# default size for number fields
  $SIZE_INC=5;		# extra space for sizes larger than max
  $TEXTAREA_COLS= 60;     # was 72
  $EXTRA_TEXTAREA_LINES= 5;
  $COL1=''; $COL2='COLSPAN=2'; $COL3='COLSPAN=3';
  $SPACER1='<IMG SRC="' . "$icon_dir/whiteblock.gif" . '" HEIGHT=1 WIDTH=100>';
  $BORDER = 1;		# border for tables?

# CHECK TO SEE IF BROWSER CAN HANDLE NESTED TABLES. NOT SURE WHAT ALL OF 
# THESE STRINGS COULD BE, PARTICULARLY THE MSIE ONES.

  $browser = $ENV{'HTTP_USER_AGENT'};
  if ($browser=~m/Mozilla\/(\d+)\./i && $1 >= 3) { $ok_to_nest = 1; }
  elsif ($browser=~m/\(\s*compatible\s*\;\s*MSIE\s*(\d+)\./i) {	# KLUDGE
    if ($1 >= 2) { $ok_to_nest = 1; }
    else { $ok_to_nest = 0; }
  } else { $ok_to_nest = 0; }

# FLAGS: (THESE NEED TO BE THE SAME IN 'cns_form2inp.cgi' !!!)

  $QUOTEFLAG = '_quote';
  $OTHERFLAG = '_OTHERFLAG';
  $OTHERVAL = '_OTHERVAL';
  $OTHER= 'user_file';
  $NONE = '_NONE_';	

# FOR LOGGING PURPOSES:

  $remote_host = $ENV{'REMOTE_HOST'};
  if (!$remote_host) { $remote_host = $ENV{'REMOTE_ADDR'}; }
  $http_ref = $ENV{'HTTP_REFERER'};
  $req_method = $ENV{'REQUEST_METHOD'};

  @shortmonth = ('',jan,feb,mar,apr,may,jun,jul,aug,sep,'oct',nov,dec);
  @d = localtime(time);
  ($SEC, $MIN, $HR, $DY, $MO, $YR) = (0..5);
  $d[$MO] ++;		# CONVERT TO 1..12 INSTEAD OF 0..11
  foreach $i (0..4) { if ($d[$i] < 10) { $d[$i] = '0' . $d[$i]; }}
    #2000 conversion: if($d[$YR]>95){$c=19;}else{$c=20;};$d[$YR]=$c . $d[$YR]; 
  $full_date = "$d[$YR]$shortmonth[$d[$MO]]$d[$DY]:$d[$HR]:$d[$MIN]:$d[$SEC]";

##############################


##### PROGRAM FLOW OF CONTROL #####

$inp_file = &init_cgi();
&init_html;
#
# make temporary directory if not present - assumes /usr/tmp is open acccess
#
if ( ! opendir TMPDIR, "$tmp_dir" ) {
    if ( system ("mkdir -p $tmp_dir") != 0 ) {
	die "could not make temporary directory - see system administrator\n";
    }
}
#
# get rid of out of date temporary files - 3 days for files, 1 day for empty dirs
#
system ("find $tmp_dir -type f -atime +3 '!' -name access.log -exec rm -f '{}' ';'");
system ("find $tmp_dir -type d -atime +1 depth -exec rmdir '{}' ';' 2>/dev/null");
#
### If no input file is given in the query string, 
### then we need to parse the multipart data.
if (!$inp_file) {
  $inp_file = $tmp_dir . "/${full_date}_${remote_host}";
  while ($line = <STDIN>) {
    next if ($line =~ /^\s*$/);			# skip blank lines
    if ($line =~ /^\s*\-+(\d+)\s*$/) {		# if delimiter line...
      $file_id = $1;				# ... get file ID
    } elsif ($line =~ /name="cns_file"/) {	# then get entire file...
      $fname = &get_file( $file_id, $line, $inp_file );
      last;
    } elsif ($line =~ /cns_edit_file=/) {
      %input=parse_args($line);
      $line_out = $input{cns_edit_file};
      $line_out =~ s/\cM//g;
      $line_out =~ s/&__/&/g;
      open (OUT_FILE, "> $inp_file");
      print OUT_FILE "$line_out";
      close OUT_FILE;
    }
  }
  if ($fname !~ /^ERR:/) {
    &log( $tmplog, "$remote_host $fname R" );	# log the transaction
  } else { print "$fname"; exit; }	# or die if no file received
} 
# Else, the filename is the last one listed in the full pathname.
else {	
    if ( $inp_file !~ /^\/\w/ ) {
	$inp_file = "$input_dir/" . $inp_file;
    }
    @dirs_and_file = split('/',$inp_file);
    $fname = $dirs_and_file[$#dirs_and_file];
    undef(@dirs_and_file);
    if ($fname !~ /^\s*$/) {
	&log( $tmplog, "$remote_host $fname L" );	# log the transaction
    } else { print "$fname"; exit; }	# or die if no file received
}

print "
  <HTML><HEAD><TITLE>Edit $fname</TITLE>
  <SCRIPT LANGUAGE=\"JavaScript1.1\">
  <!--- hide script from old browsers
  function assert_real(input, def) {
    var val = parseFloat(input.value);
    if (val < 0 || val >= 0) { input.value = val; }
    else {
      alert(\"Value must be a real number.\"); 
      input.value = def;
    }
  }
  // end hiding from old browsers -->
  </SCRIPT></HEAD><BODY BGCOLOR=white> 
  <H1><CENTER>$fname</CENTER></H1>
  <FORM ACTION=\"$form2inp\" METHOD=POST>
  <INPUT TYPE=HIDDEN NAME=\"source_file\" VALUE=\"$inp_file\">\n";

open( INP, "< $inp_file" ) || print "cannot read $inp_file";
while ($line=<INP>) { process_line($line); }
&output_form();		# output the remainder 
close INP;
print '
  <INPUT TYPE=SUBMIT NAME="submit_view" VALUE="View updated file"> 
  <INPUT TYPE=SUBMIT NAME="submit_save" VALUE="Save updated file"> 
  <INPUT TYPE=RESET VALUE="Reset">
  </FORM></BODY></HTML>
  ';


#################### PARSING SUBROUTINES ###################
sub process_line { local($line) = @_;
  $_ = $line;
  if (/^\s*$/) {				# blank lines break doc's
    if ($form[$#form - 1] eq 'doc') { push(@form, 'break'); } 
  }
  elsif (/^remarks$/) { }			# skip remarks
  elsif (/^\s*\{\-\s*(\S.*)$/) {		# skip guidelines
    ($str,$remainder) = &append_text_until( '\-\}', $1 ); 
    &process_line($remainder);
  }

  ### pre-form information
  elsif (/^\s*\{\+\s*authors:\s*(\S.*)$/i) {
    ($auth_str,$remainder) = &append_text_until( '\+\}', $1 );
    print "<H2>Authors</H2>\n<UL><LI>$auth_str</LI></UL>\n";
    &process_line($remainder);

  }
  elsif (/^\s*\{\+\s*description:\s*(\S.*)$/i) {
    ($desc_str,$remainder) = &append_text_until( '\+\}', $1 );
    &process_line($remainder);
    print "<H2>Description</H2>\n<UL><LI>$desc_str</LI></UL>\n";
  }

  ### if we begin a reference...
  elsif (/^\s*\{\+\s*reference:\s*(\S.*)$/) {
    ($ref_str,$remainder) = &append_text_until( '\+\}', $1 );
    &process_line($remainder);
    if ($form[0] ne 'ref') { 
      &output_form(); 
      @form = ('ref'); 
    }
    push(@form, $ref_str);
  }

  ### if we start a new heading...
  # NOTE: ir_refine.inp contains a '-' in a heading
  #       generate.inp contains no space after '...===' before 'nucleic'
  #       (generate_seq.inp too!)
  elsif (/^\s*\{==+\s*(\S[^=]+\S)\s*==[=\-]+\}\s*$/) {	
    $head = $1;
    $head =~ tr/=//d;			# remove any spurious '=' chars
    &output_form(); 
    @form = ('form',$head); 
  }

  ### if we begin documentation...
  elsif (/^\s*\{\*\s*(\S.*)$/) {	
    ($doc_str,$remainder) = &append_text_until( '\*\}', $1 );
#    &process_line($remainder);
    $doc_str =~ s/\s+/ /g;
    if ($doc_str ne ' ' && $doc_str ne '') {
      $doc_str =~ s/\&/\&amp\;/g;
      $doc_str =~ s/</\&lt\;/g;
      $doc_str =~ s/>/\&gt\;/g;
      push(@form, 'doc', $doc_str);
    } else { push(@form, 'break' ); }
  }

  ### if we have pre-formatted documention...
  elsif (/^\s*\{\+\s*list:\s*(\S.*)$/) {		
    ($pre_str,$remainder) = &append_text_until( '\+\}', $1 ); 
#    &process_line($remainder);
    $pre_str =~ s/\&/\&amp\;/g;
    $pre_str =~ s/</\&lt\;/g;
    $pre_str =~ s/>/\&gt\;/g;
    push(@form, 'doc', "<PRE>$pre_str</PRE>");
  }

  ### if we have a predefined option list...
  elsif (/^\s*\{\+\s*choice:\s*(\S.*)$/) {
    ($choice_str,$remainder) = &append_text_until( '\+\}', $1 );
    $choice_str =~ s/choice://g;	# delete 'choice:' from list-string
    $choice_str =~ s/\n/ /g;
    push(@form, 'varchoice', $choice_str);
    &process_line($remainder);
  }

  ### if we have a table...
  elsif (/^\s*\{\+\s*table:\s*(\S.*)$/) {
    ($table_str,$remainder) = &append_text_until( '\+\}', $1 );
    $table_str =~ s/\n/ /g;
    if ($table_str =~ /\s*rows\s*=\s*(\d+)(.*)cols\s*=\s*(\d+)(.*)$/i) {
      ($numrows,$rownames,$numcols,$colnames) = ($1,$2,$3,$4);
    } elsif ($table_str =~ /\s*cols\s*=\s*(\d+)(.*)rows\s*=\s*(\d+)(.*)$/i) {
      ($numcols,$colnames,$numrows,$rownames) = ($1,$2,$3,$4);
    } else { $numrows=-1; $numcols=-1; }	# BAD TABLE PARSE
    push(@form, 'vartable', $numrows, $numcols, $rownames, $colnames);
    &process_line($remainder);
  }

  ### if we have any variable(s) just on one line...
  elsif (/^\s*\{===>\}\s*(\S.*)\;\s*$/) {
    @varpairs = split(';',$1);
    foreach $varpair (@varpairs) {
      ($lhs,$rhs) = split('=',$varpair,2);
      &process_var($lhs,$rhs);
    }
  }

  ### if we have a multi-line variable...
  elsif (/^\s*\{===>\}\s*([^\s=]+)\s*=\s*(\S.*)$/) {
    ($lhs,$rest) = ($1,$2);
    ($rhs,$remainder) = &append_text_until( '\;', $rest );
    &process_var($lhs,$rhs);
    &process_line($remainder);
  }

  ### if we have the other type of multi-line variable...
  elsif (/^\s*\{===>\}\s*$/) {
    ($textarea,$remainder) = &append_text_until( '\{<===\}', '' );
    $name = 'textarea' . $num_textarea++;
    push(@form, 'varlong', 0, $name, $textarea);
    &process_line($remainder);
  }

  ### if we end the standard definitions section...
  elsif (/things below this line do not normally need to be changed/) { 
    &output_form(); 
    @form = ('form', '');		# treat this as an empty form block
  }

  ### default
  else {}
}

sub output_form { 
#print join(' | ',@form); 	# UNCOMMENT TO DEBUG FORM PARSING
  local ($i,$item,$doc_str,$lhs,$rhs,$q,$size);
  local ($choice_str,$other,@choices,$choice,@lines,$lines,);
  if ($form[0] eq 'ref') {

  ## I. REFERENCES

    print "<H2>References</H2><UL>\n";
    while ($form[++$i]) { 
      if ($form[$i] ne 'break') { print "  <P><LI>$form[$i]\n"; }
    }
    print "</UL>\n";

  ## II. FORM

  } elsif ($form[0] eq 'form') {

  ## A. HEADING

    print "<TABLE BORDER=$BORDER WIDTH=\"100\%\">\n";
    if ($form[1]) {
      print "  <TR><TD $COL3 BGCOLOR=$COLOR><CENTER>\n";
      print "    <FONT FACE=helvetica COLOR="RED"><BIG><B>$form[1]\n";
      print "    </B></BIG></FONT></CENTER></TD></TR>\n";
    } else {
      print "  <TR><TD $COL3 BGCOLOR=$COLOR><CENTER>\n";
      print "    <FONT SIZE=4 FACE=helvetica COLOR="RED">&nbsp;\n";
      print "    </FONT></CENTER></TD></TR>\n";
    }
    print "<TR><TD>$SPACER1<TD>$SPACER1<TD>$SPACER1</TR>\n";

    $i = 2;
    while ($item=$form[$i++]) {


  ## B. DOCUMENTATION

      if ($item eq 'doc') {
        $doc_str = $form[$i++];
        if ($doc_str=~m/file\(?s?\)?\s*$/) { $bigstr=1; } else { $bigstr=0; }
        $doc_str = "    <B>$doc_str</B><BR>\n";
        while ($form[$i] eq 'doc') { 
          $doc_str .= "    <I>$form[$i+1]</I>\n"; 
          $i+=2;
        }
        if ($form[$i] eq 'var' || $form[$i] eq 'varchoice') { 
          if ($form[$i+1] < $BIG_SIZE && !$bigstr) {
            print "  <TR><TD $COL2 ALIGN=$ALIGN>\n$doc_str";
            print "    </TD><TD $COL1>\n";
          } else {
            if (length($doc_str) > $DOCMAX) {
              print "  <TR><TD $COL3>\n$doc_str\n<BR>$SPACER1\n";
            } else {
              print "  <TR><TD $COL1 ALIGN=$ALIGN>\n$doc_str";
              print "    </TD><TD $COL2>\n";
            }
          }
        } else {
          print "  <TR><TD $COL3>\n$doc_str\n";	# for vartables only ???
        }


  ## C. CHOICES AND TABLE FORMATTING

      } elsif ($item eq 'varchoice') {
        $choice_str = $form[$i++];
        while ($form[$i] eq 'break') { $i++; }
        if ($form[$i] !~ /^var/) { print "ERROR!</TD></TR>\n"; }

      } elsif ($item eq 'vartable') {
        if ($ok_to_nest) {
          print "<BLOCKQUOTE><TABLE BORDER=$BORDER WIDTH=\"85%\">\n";
        } else {
          print "</TD></TR></TABLE>\n";		# break for inner table
          print "<TABLE BORDER=$BORDER WIDTH=\"100%\">\n";
        }
        ($numrows, $numcols) = ($form[$i++], $form[$i++]);
        ($rownames, $colnames) = ($form[$i++], $form[$i++]);
        if ($rownames=~m/$NUMBERED/i) 
          { $rownames = '"' . join('" "',1..$numrows) . '"' ; }
        if ($colnames=~m/$NUMBERED/i) 
          { $colnames = '"' . join('" "',1..$numcols) . '"' ; }
        $nested_table=1;	# /set flag that we're in a nested table
        if ($colnames=~m/^\s+$/) { $colnames = ''; }
        if ($rownames=~m/^\s+$/) { $rownames = ''; }
        $colnames =~ s/\n/ /g;
        $rownames =~ s/\n/ /g;

        if ($colnames) {
          foreach $i (0..$numcols-1) {
            if ($colnames=~m/^\s*"([^"]*)"(.*)$/) {
              ($name,$colnames) = ($1, $2);
            } else { $name = ''; }
            $colnames[$i] = $name;
          }
          if ($rownames) { print "  <TR><TH>&nbsp;</TH>"; }
          else { print "  <TR>"; }
          foreach $name (@colnames) { print "<TH>$name</TH>"; }  
          print "    </TR>\n";
        }
        $colcount = 1; # colcount is 1-based

        if ($rownames) {
          foreach $i (0..$numrows-1) {
            if ($rownames=~m/^\s*"([^"]*)"(.*)$/) {
              ($name,$rownames) = ($1, $2);
            } else { $name = ''; }
            $rownames[$i] = $name;
          }
          print "  <TR ALIGN=CENTER><TH>$rownames[0]</TH><TD>\n"; 
          $rownames = 1;
        } else { print "  <TR ALIGN=CENTER><TD>\n"; }
	$rowcount = 0; # rowcount is 0-based


  ## D. VARIABLES

      } elsif ($item eq 'var' || $item eq 'varlong') {
        ($size,$lhs,$rhs) = ($form[$i++], $form[$i++], $form[$i++]);
        if ($bigstr) { $size=$BIG_SIZE; } # bigstr flag set B. (documentation)

  ## D. 1) ANY VARIABLE REQUIRING MORE THAN 1 LINE (E.G.: TEXTAREA)

        if ($item eq 'varlong') {
          @lines = split(/\n/,$rhs);
          $lines = $#lines + $EXTRA_TEXTAREA_LINES;
          print "    </TD></TR>\n";	# always break row for textarea
          print "  <TR><TD $COL3><TEXTAREA NAME=$lhs ROWS=$lines ";
          print "COLS=$TEXTAREA_COLS>\n$rhs</TEXTAREA>\n";
          undef(@lines);
          undef($lines);
          undef($rhs);
          undef($lhs);

  ## D. 2) SPECIAL

        } elsif (&is_special($lhs)) {		# if it's special...
          &output_var($NUM_SIZE,$lhs,$rhs);	# ... output all on one line
          while (&is_special($form[$i+2])) {
            ($size,$lhs,$rhs) = ($form[$i+1], $form[$i+2], $form[$i+3]);
            &output_var($NUM_SIZE,$lhs,$rhs);
            $i+=4;
          }

  ## D. 3) CHOICE VARIABLE

        } elsif ($choice_str) {

        ## Split up choices, grouping characters enclosed in double-quotes as
        ##   a single choice, or non-whitespace strings as single choices.
        ##   Example: {+ choice: "this" "that" "" user_file +} 
        ##   becomes a list with four elements: (this,that,,user_file),
        ##   where the third element is null and the fourth will translate to 
        ##   the 'other' selection.

          while ($choice_str !~ /^\s*$/) {
            if ($choice_str=~/^\s*"([^"]*)"(.*)$/) {
              ($choice, $choice_str) = ($1, $2);
            } elsif ($choice_str=~/^\s*(\S+)(.*)$/) {
              ($choice, $choice_str) = ($1, $2);
            } # should be no 'else'
            push( @choices, $choice );
          }

  ## D. 3a) RADIO BUTTONS

          if ($#choices < $A_FEW) {		# if we have few choices...
            foreach $choice (@choices) {	# print radio buttons
              print "    <INPUT TYPE=RADIO NAME=$lhs VALUE=\"$choice\"";
              if ( $choice eq $rhs ) { print ' CHECKED'; }
              print ">$choice &nbsp; &nbsp; &nbsp;\n";
            }

  ## D. 3b) SELECTION LIST

          } else {				# else print selection list
            print "    <SELECT NAME=$lhs>\n";
            $max_rhs_len = 0;
            foreach $choice (@choices) {
              if ( $choice eq $OTHER ) { $other = 1; }
              else {
                if ( $choice eq $rhs ) { print '    <OPTION SELECTED>'; }
                else { print '    <OPTION>'; }
                print "$choice</OPTION>\n";
                $cho_len = length($choice);
                if ($cho_len > $max_cho_len) { $max_cho_len = $cho_len; }
              }
            }
            print "    </SELECT>\n";
            if ($other) {

              # JUST PUT IT ALL ON ONE LINE REGARDLESS...
              $size = $STR_SIZE;
              if ($max_cho_len > $STR_SIZE ) { 
                 print "    <BR>\n"; 
                 $size = $max_cho_len + $SIZE_INC;
              }
              print "    <NOBR>Other: ";
              print "<INPUT TYPE=CHECKBOX NAME=$lhs$OTHERFLAG VALUE=1>\n";
              print "                 <INPUT NAME=$lhs$OTHERVAL ";
              print "VALUE=\"\" SIZE=$BIG_SIZE></NOBR>\n";
            }
          }
          $choice_str=''; $other=0; undef @choices;

  ## D. 4) NORMAL VARIABLE

        } else { &output_var($size,$lhs,$rhs); }
        while ($form[$i] eq 'break') { $i++; }
        if (!$nested_table) {
          if ($form[$i] eq 'doc') { print "    </TD></TR>\n"; }
          else { print "    <BR>\n"; }
        } else {
          print "    </TD>";
          if ($form[$i] eq 'doc') { 
            foreach (1..$numcols-$colcount) { print "<TD>&nbsp;</TD>"; }
            print "</TR>\n";
            &cleanup_nested_table();
          } else { 
            $colcount++;
            if ($colcount <= $numcols) {	# colcount is 1-based
              print "<TD>\n";
            } else {
              $rowcount++;
              $colcount=1;
              print "</TR>\n";
              if ($rowcount >= $numrows) {	# rowcount is 0-based
                &cleanup_nested_table();
              } else {
                if ($rownames) {
                  $r = $rownames[$rowcount];
                  if ($r=~m/^\s*$/) { $r = '&nbsp;'; }
                  print "  <TR ALIGN=CENTER><TH>$r</TH><TD>"; 
                } else { print "  <TR ALIGN=CENTER><TD>"; }
              }
            } 
          }
        }


  ## E. OTHER

      } else {}			# NO DEFAULT FOR TABLE BLOCK (may be 'break')
    }
    print "</TABLE>\n";
  } else {}				# NO FORM PROCESSED (e.g.: first form)
}

sub cleanup_nested_table {
  print "</TABLE>\n";		# end nested table
  if ($ok_to_nest) {
    print "</BLOCKQUOTE></TD></TR>\n";
  } else {
    print "<TABLE BORDER=$BORDER WIDTH=\"100\%\">\n"; # continue original table
    print "<TR><TD>$SPACER1<TD>$SPACER1<TD>$SPACER1</TR>\n";
  }
  $nested_table=0;		# nested_table flag set in C. (table formatting)
  undef ($numrows);
  undef ($rowcount);
  undef ($rownames);
  undef (@rownames);
  undef ($numcols);
  undef ($colcount);
  undef ($colnames);
  undef (@colnames);
}

sub output_var { local( $size, $lhs, $rhs ) = @_;
  if ($lhs=~m/$QUOTEFLAG$/) { $js_err = ''; $rhs = '"' . $rhs . '"'; } 
  else {$js_err="onChange=\"assert_real(document.forms[0].${lhs},$rhs)\"";}
# KLUDGE! kill javascript if the variable name contains other than alphanumerics
  if ($lhs =~ m/[^A-Za-z_1-9]/) { $js_err = ''; } 
  print "    <INPUT NAME=$lhs VALUE=$rhs SIZE=$size $js_err>\n"; 
}

# LEGACY -- REMOVE THIS (KLUDGE)
sub is_special{ local( $name ) = @_;
  return 0;
  return ($name eq 'a'       || $name eq 'b'        || $name eq 'c' || 
          $name eq 'alpha'   || $name eq 'beta'     || $name eq 'gamma' ||
          $name eq 'low_res' || $name eq 'high_res');
}

sub process_var { local($lhs,$rhs) = @_;
  # if value in parens or multi-line, then textarea
  if ($rhs=~/^\s*\(.*\)\s*$/ || $rhs=~/\n/) {	
    push(@form, 'varlong', 0, $lhs, $rhs); # modify the global variable "@form"
  } else { 
    if ($rhs=~/^"([^"]*)"\s*$/) {		# if the r.h.s. has quotes...
      $rhs = $1;
      $lhs .= $QUOTEFLAG;
      $size = $STR_SIZE;
    } else { $size = $NUM_SIZE; }
    if (length($rhs) > $STR_SIZE) { $size=length($rhs)+$SIZE_INC; } 
    push(@form, 'var', $size, $lhs, $rhs); 	# global "@form" again ... 
  }
}

##### SUBROUTINE
##### APPEND_TEXT_UNTIL
# Pre:  $delim is a non-null string
#       $tmp is a line of input, potentially containing $delim
# Post: $buffer, the first return value, is a concatenated string of
#         all chars in all lines (including $tmp) preceeding $delim
#       $line, the other return value is the remining line needing
#         processing (it may be empty).
#####
sub append_text_until{ local( $delim, $tmp ) = @_;
    local( $buffer='', $continue );
    $continue = 1;
    $tmp .= "\n"; 
    while ($continue) {			
      if ($tmp =~ /^(.*)$delim(.*)$/) {	# If $tmp contains $delim ...
        $buffer .= $1;			# ...append desired text to buffer
        $line = $2;
        $continue = 0;
      } else { 
        $buffer .= "$tmp ";		# ... Otherwise append all of $tmp
        $tmp = <INP>;			# ... and get a new line. 
      }
      if ( $continue && eof ) {
	  print "<CENTER><P><FONT SIZE=+3>\n";
	  print "EOF detected while trying to parse input<BR>\n";
	  print "Please check the input file - it may be corrupted\n";
	  print "</P></FONT></CENTER>\n";
	  exit;
      }
    }
    $buffer =~ s/[ \t]+/ /g;		# Squash multiple spaces
#    chop $buffer;			# Remove trailing space
    ($buffer,$line)			# Return buffer and line
}

##########  MULTIPART DATA PARSER  ##########

##### READS FILE FROM STDIN, STOPS AT 'FILE_ID'
##### WRITES FILE NAMED $new_fname.
##### RETURNS $old_fname -- the name the client gave the file.
##### IF $old_fname BEGINS WITH 'ERR: ' THEN THE TRANSMISSION FAILED.
#####   LOOK AT THE REST OF THE STRING FOR A DIAGNOSTIC.
sub get_file {
  local( $file_id, $head, $new_fname ) = @_;
  local( $fname, $line, @file, $empty, $content );

  $empty = 1;
  ($old_fname) = ($head =~ /filename="(.*)"/);
#  if ($fname =~ /([^A-Za-z0-9_\.\,\-])([A-Za-z0-9_\.\,\-]*)$/) { $fname = $2; }
  <STDIN>;			# SKIP FIRST BLANK LINE
  while (($line = <STDIN>) !~ /$file_id/) {
    if ($line !~ /^\s*$/) { $empty=0; }
    $line =~ s/\r\n$/\n/;	# DELETE EXTRA RETURNS PUT ON BY NETSCAPE???
    push( @file, $line );
  }
  if ($empty) { return 'ERR: no file received'; }
  open( OUT, "> $new_fname" ) || 
    (return "ERR: cannot write file $new_fname: $!");
  print OUT @file;
  close OUT;
  $old_fname;       # RETURN FNAME IF SUCCESSFUL
}


########## GENERAL CGI SUBROUTINES ##########

# PUBLIC SUBROUTINES
# $query 		= &init_cgi();
#			  &init_html( $title, $desc, $keyw );
# %nv			= &parse_post(); 
# $encode		= &escape { local($toencode) = @_;
#			  &switch_to( $url, $note, $time );
#			  &mail_usr( $usr, $subject, %nv );
#			  &log( $logfile, $note );

# PRIVATE SUBROUTINES
# %nv                      = &parse_args( $argstr );

# TO DO:
# need to add fork to mail subroutine
# subroutines should exit false, not die
# javascript soubroutines?

sub init_cgi {
  local( $query );
  $| = 1;
  if (!($query=$ENV{'QUERY_STRING'})) { $query = $ARGV[0]; }
  $query;  # RETURN VALUE
}

sub init_html { local( $title, $desc, $keyw ) = @_;
  print "Content-type: text/html\n\n<HTML>";
  if ($title || $desc || $keyw) { print '<HEAD>'; }
  if ($title) { print "<TITLE>$title</TITLE>\n"; }
  if ($desc) { print "<META NAME=description CONTENT=\"$desc\">\n"; }
  if ($keyw) { print "<META NAME=keywords CONTENT=\"$keyw\">\n"; }
  if ($title || $desc || $keyw) { print '</HEAD>'; }
}

sub switch_to { local( $url, $note, $time ) = @_;
  if ($time eq '' || $time < 0) { $time = 0; }
  if ($note eq 'direct') {
    print "Location: $url\n\n";
  } else {
    print "Content-type: text/html\n\n";
    if (!$note) { $note = "Switching to $url"; }
    print "<HTML><HEAD><TITLE>$note</TITLE>\n";
    print '<META HTTP-EQUIV="Refresh" CONTENT= "';
    print "${time};URL=${url}\"></META></HEAD>\n";
    print "<BODY><H1>$note</H1></BODY></HTML>\n";
    print "
      If this page does not automatically reload, you must be using an
      older WWW Browser that doesn't support 'page refresh.' Click
      <A HREF=\"$url\">here</A> to go on.
      And think about getting a new browser!</BODY></HTML>\n";
  }
}

sub parse_args { local( $argstr ) = @_;
  local( @pairs, $pair, $name, $value, %nv );
  @pairs = split(/&/, $argstr);
  foreach $pair (@pairs) {
    ($name, $value) = split(/=/, $pair);
    $value =~ tr/+/ /;
    $value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
    $value =~ s/^\s(.*)\s$/\1/; #trim off whitespace
    $nv{$name} .= $value;
  }
  %nv;	# RETURN NAME, VALUE PAIRS
}

sub parse_post {
  local( $buffer );
  read(STDIN, $buffer, $ENV{'CONTENT_LENGTH'});
  if (!$buffer) { $buffer = $ENV{'QUERY_STRING'}; }
  if (!$buffer) { $buffer = $ARGV[0]; }
  &parse_args( $buffer ); # RETURN NAME, VALUE PAIRS
}

# NOTE! MAKE SURE $SUBJECT & $USR DO NOT CONTAIN SPECIAL CHARS!
# TODO: USE FORK FOR MAIL PROCESS
sub mail_usr { local( $usr, $subject, %nv ) = @_;
  $mail = '/usr/ucb/mail';
  open( MAIL, "|$mail -s '$subject' $usr" ) ||
    die "cannot $mail -s '$subject' $usr: $!";
  print MAIL "Message from CGI...\n\n";
  foreach $input (keys %nv) {
    print MAIL "$input: $nv{$input}\n";
  }
  close MAIL;
}

sub log { local( $logfile, $note ) = @_;
  open( LOG, ">> $logfile" ) || die "cannot write to logfile $logfile";
  print LOG "$full_date $note\n";
  close LOG
}

# borrowed from Lincoln Stein (lstein@genome.wi.mit.edu)
# modified 5/1/96 J. Reklaw (Happy Mayday!)
# TRANSLATES ALL NON-ALPHANUMERIC CHARS TO CGI-FRIENDLY HEX
sub escape { local($toencode) = @_;
    $toencode=~s/([^a-zA-Z0-9_])/sprintf("%%%x",ord($1))/eg;
    return $toencode;
}

sub unescape { local($todecode) = @_;
  $todecode =~ tr/+/ /;
  $todecode =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
  $todecode =~ s/^\s(.*)\s$/\1/; #trim off whitespace
  return $todecode;
}


# EOF --> <H3>An error has occurred. Please email <!--
# -->&lt;<A HREF="mailto:reklaw@cs.yale.edu">reklaw@cs.yale.edu</A>&gt;</H3>
