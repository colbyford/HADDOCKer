#!/bin/csh
#
setenv WDIR $HADDOCK/tests/protein-dna/ana_scripts

cd $1/structures/it1/water/
$WDIR/fraction-native.csh `cat file.nam`
$WDIR/cluster-fnat.csh 4
cd ..
$WDIR/fraction-native.csh `cat file.nam`
$WDIR/cluster-fnat.csh 4
cd ../it0
set i1=`wc -l file.nam`
@ i1-=5000
$WDIR/fraction-native.csh `head -5000 file.nam`
$WDIR/fraction-native-cont.csh `tail -$i1 file.nam`
cd ../../../
