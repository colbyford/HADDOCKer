#!/bin/tcsh -f

# This script is to be used with ANA_RMSD-Split.csh

# EzgiKaraca, 20092011, 6:19PM

#
# Define the location of profit
#
if ( `printenv |grep PROFIT | wc -l` == 0) then
  set found=`which profit |wc -l`
  if ($found == 0) then
     echo 'PROFIT environment variable not defined'
     echo '==> no rmsd calculations '
  else
     setenv PROFIT `which profit`
  endif
endif

set WDIR=$HADDOCK/tests/protein-tetramer-CG/ana_scripts
set refe = $WDIR/3GD8_tetramer.pdb
set izone_ABCD = $WDIR/3GD8_tetramer.izone_ABCD
set izone_ABDC = $WDIR/3GD8_tetramer.izone_ABDC
set izone_ACBD = $WDIR/3GD8_tetramer.izone_ACBD
set izone_ACDB = $WDIR/3GD8_tetramer.izone_ACDB
set izone_ADCB = $WDIR/3GD8_tetramer.izone_ADCB
set izone_ADBC = $WDIR/3GD8_tetramer.izone_ADBC
set atoms = 'CA'

cat /dev/null > i-RMSD.dat
cat /dev/null > rmsd_xray.disp

foreach i (`cat file.nam`)
  $HADDOCKTOOLS/pdb_segid-to-chain $i |sed -e 's/BB/CA/g' >$i:r.tmp
  echo $i >>rmsd_xray.disp 
  $PROFIT<<_Eod_ | grep RMS | sort -nk 2 | head -1 >> rmsd_xray.disp
      refe $refe
      mobi $i:r.tmp
      atom $atoms
      `cat $izone_ABCD`
      fit
      zone clear
      `cat $izone_ABDC`
      fit
      zone clear
      `cat $izone_ACBD`
      fit
      zone clear
      `cat $izone_ACDB`
      fit
      zone clear
      `cat $izone_ADBC`
      fit
      zone clear
      `cat $izone_ADCB`
      fit
      zone clear
      quit
_Eod_
\rm $i:r.tmp
end
awk '{if ($1 == "RMS:") {printf "%8.3f ",$2} else {printf "\n %s ",$1}}' rmsd_xray.disp |grep pdb |awk '{print $1,$2}' >> i-RMSD.dat
sort -nk 2 i-RMSD.dat > i-RMSD-sorted.dat
\rm rmsd_xray.disp
