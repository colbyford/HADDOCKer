#!/bin/csh
#
setenv target refine-expand-complex
setenv WDIR $HADDOCK/tests/refine-expand-complex/ana_scripts

cd $1/structures/it1/water/analysis
gunzip cluster.out.gz; \rm *out.gz
cd ..
$WDIR/i-rmsd_to_xray.csh `cat file.nam`
$WDIR/l-rmsd_to_xray.csh `cat file.nam`
$WDIR/ana_structures.csh
$WDIR/fraction-native.csh `cat file.nam`
$WDIR/ana_clusters.csh -best 4 analysis/cluster.out
$WDIR/cluster-fnat.csh 4
cd ../analysis
gunzip cluster.out.gz; \rm *out.gz
cd ..
$WDIR/i-rmsd_to_xray.csh `cat file.nam`
$WDIR/l-rmsd_to_xray.csh `cat file.nam`
$WDIR/ana_structures.csh
$WDIR/fraction-native.csh `cat file.nam`
$WDIR/ana_clusters.csh -best 4 analysis/cluster.out
$WDIR/cluster-fnat.csh 4
cd ../it0
$WDIR/i-rmsd_to_xray.csh `head -5000 file.nam`
$WDIR/l-rmsd_to_xray.csh `head -5000 file.nam`
$WDIR/ana_structures.csh
$WDIR/fraction-native.csh `head -5000 file.nam`
set i1=`wc -l file.nam`
@ i1-=5000
if ($i1 > 0) then
  $WDIR/i-rmsd_to_xray-cont.csh `tail -$i1 file.nam`
  $WDIR/l-rmsd_to_xray-cont.csh `tail -$i1 file.nam`
  $WDIR/fraction-native-cont.csh `tail -$i1 file.nam`
endif
cd ../../../





