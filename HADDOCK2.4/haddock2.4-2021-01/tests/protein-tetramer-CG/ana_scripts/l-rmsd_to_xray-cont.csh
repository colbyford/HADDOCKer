#!/bin/tcsh -f
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
set refe = $WDIR/3gd8_tetramer.pdb
set lzone_ABCD = $WDIR/3GD8_tetramer.lzone_ABCD
set lzone_ABDC = $WDIR/3GD8_tetramer.lzone_ABDC
set lzone_ACBD = $WDIR/3GD8_tetramer.lzone_ACBD
set lzone_ACDB = $WDIR/3GD8_tetramer.lzone_ACDB
set lzone_ADBC = $WDIR/3GD8_tetramer.lzone_ADBC
set lzone_ADCB = $WDIR/3GD8_tetramer.lzone_ADCB
set atoms = 'CA'

#cat /dev/null > l-RMSD.dat
cat /dev/null > l-rmsd_xray.disp

foreach i (`cat file.nam`)
  $HADDOCKTOOLS/pdb_segid-to-chain $i |sed -e 's/BB/CA/g' >$i:r.tmp
  echo $i >>l-rmsd_xray.disp 
  $PROFIT <<_Eod_ |grep RMS  | awk '{ if (NR % 4 == 0) print $0 }' | sort -nk2 |head -1 >> l-rmsd_xray.disp
      refe $refe
      mobi $i:r.tmp
      atom $atoms
      `cat $lzone_ABCD`
      zone clear
      `cat $lzone_ABDC`
      zone clear
      `cat $lzone_ACBD`
      zone clear
      `cat $lzone_ACDB`
      zone clear
      `cat $lzone_ADBC`
      zone clear
      `cat $lzone_ADCB`
      zone clear
      quit
_Eod_
\rm $i:r.tmp
end
awk '{if ($1 == "RMS:") {printf "%8.3f ",$2} else {printf "\n %s ",$1}}' l-rmsd_xray.disp |grep pdb |awk '{print $1,$2}' >> l-RMSD.dat
sort -nk 2 l-RMSD.dat > l-RMSD-sorted.dat
\rm l-rmsd_xray.disp
