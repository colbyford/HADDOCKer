#!/bin/csh
#
set WDIR=$HADDOCK/examples/protein-protein/ana_scripts
set refe=$WDIR/e2a-hpr_1GGR.pdb
set izone=$WDIR/e2a-hpr.izone
set atoms='CA,C,N,O'

cat /dev/null >rmsd_xray.disp

foreach i ($argv)
  $HADDOCKTOOLS/pdb_segid-to-chain $i >$i:r.tmp1
#  cat $i >$i:r.tmp1
  echo $i >>rmsd_xray.disp
  profit <<_Eod_ |grep RMS |tail -1 >>rmsd_xray.disp
    refe $refe
    mobi $i:r.tmp1
    atom $atoms
    `cat $lzone`
    quit
_Eod_
\rm $i:r.tmp1
end
awk '{if ($1 == "RMS:") {printf "%8.3f ",$2} else {printf "\n %s ",$1}}' rmsd_xray.disp |grep pdb |awk '{print $1,$2}' >> l-RMSD.dat
head -1 l-RMSD.dat >l-RMSD-sorted.dat
grep pdb l-RMSD.dat |sort -n -k2 >> l-RMSD-sorted.dat
\rm rmsd_xray.disp
