#!/bin/csh
#
set WDIR=$HADDOCK/examples/refine-complex/ana_scripts
set refe=$WDIR/e2a-hpr_1GGR.pdb
set lzone=$WDIR/e2a-hpr.lzone
set atoms='CA,C,N,O'

cat /dev/null >rmsd_xray.disp

foreach i ($argv)
  $HADDOCKTOOLS/pdb_segid-to-chain $i >$i:r.tmp1
#  cat $i >$i:r.tmp1
  echo $i >>rmsd_xray.disp
  $PROFIT <<_Eod_ |grep RMS |tail -1 >>rmsd_xray.disp
    refe $refe
    mobi $i:r.tmp1
    ignore missing
    atom $atoms
    `cat $lzone`
    quit
_Eod_
\rm $i:r.tmp1
end
echo "#struc l-RMSD" >l-RMSD.dat
awk '{if ($1 == "RMS:") {printf "%8.3f ",$2} else if  ($2 == "RMS:") {printf "%8.3f ",$3} else {printf "\n %s ",$1}}' rmsd_xray.disp |grep pdb |awk '{print $1,$2}' >> l-RMSD.dat
head -1 l-RMSD.dat >l-RMSD-sorted.dat
grep pdb l-RMSD.dat |sort -n -k2 >> l-RMSD-sorted.dat
\rm rmsd_xray.disp
