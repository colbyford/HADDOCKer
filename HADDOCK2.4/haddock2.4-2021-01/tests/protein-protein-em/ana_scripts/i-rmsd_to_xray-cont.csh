#!/bin/csh
#
setenv WDIR $HADDOCK/examples/protein-protein/ana_scripts
set refe=$WDIR/e2a-hpr_1GGR.pdb
set izone=$WDIR/e2a-hpr.izone
set atoms='CA'

cat /dev/null >rmsd-interface_xray.disp

foreach i ($argv)
  if ($i:e == "gz") then
    gzip -dc $i > $i:t:r.tmp2
  else
    cp $i $i:t:r.tmp2
  endif
  $HADDOCKTOOLS/pdb_segid-to-chain $i:t:r.tmp2  |sed -e 's/BB/CA/' >$i:t:r.tmp1
  echo $i >>rmsd-interface_xray.disp
  profit <<_Eod_ |grep RMS |tail -1 >>rmsd-interface_xray.disp
    refe $refe
    mobi $i:t:r.tmp1
    `cat $izone`
    atom $atoms
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
