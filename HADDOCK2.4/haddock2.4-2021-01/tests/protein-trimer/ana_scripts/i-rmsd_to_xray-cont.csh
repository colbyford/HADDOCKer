#!/bin/csh
#
setenv WDIR $HADDOCK/tests/protein-trimer/ana_scripts
set refe=$WDIR/1qu9_ABC.pdb
set izone=$WDIR/1qu9.izone
set atoms='CA'
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

cat /dev/null >rmsd-interface_xray.disp

foreach i ($argv)
  if ($i:e == "gz") then
    gzip -dc $i > $i:t:r.tmp2
  else
    cp $i $i:t:r.tmp2
  endif
  $HADDOCKTOOLS/pdb_segid-to-chain $i:t:r.tmp2 |sed -e 's/BB/CA/g' >$i:t:r.tmp1
  echo $i >>rmsd-interface_xray.disp
  $PROFIT <<_Eod_ |grep RMS |sort -nk2 -r |tail -1 >>rmsd-interface_xray.disp
    refe $refe
    mobi $i:t:r.tmp1
    atom $atoms
    `cat $izone`
    fit
    quit
_Eod_
\rm $i:t:r.tmp1
\rm $i:t:r.tmp2
end
awk '{if ($1 == "RMS:") {printf "%8.3f ",$2} else {printf "\n %s ",$1}}' rmsd-interface_xray.disp |grep pdb |awk '{print $1,$2}' >> i-RMSD.dat
head -1 i-RMSD.dat >i-RMSD-sorted.dat
grep pdb i-RMSD.dat |sort -n -k2 >> i-RMSD-sorted.dat
\rm rmsd-interface_xray.disp
