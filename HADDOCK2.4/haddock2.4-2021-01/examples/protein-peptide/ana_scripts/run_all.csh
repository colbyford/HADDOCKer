#!/bin/csh
#
setenv target protein-peptide
setenv WDIR $HADDOCK/examples/protein-peptide/ana_scripts

cd $1/structures/it1/water/analysis
gunzip cluster.out.gz; \rm *out.gz
cd ..
$WDIR/i-rmsd_to_xray.csh 
$WDIR/l-rmsd_to_xray.csh 
$WDIR/ana_structures.csh
$WDIR/fraction-native.csh 
$WDIR/ana_clusters.csh -best 4 analysis/cluster.out
$WDIR/cluster-fnat.csh 4
cd ../analysis
gunzip cluster.out.gz; \rm *out.gz
cd ..
$WDIR/i-rmsd_to_xray.csh 
$WDIR/l-rmsd_to_xray.csh 
$WDIR/ana_structures.csh
$WDIR/fraction-native.csh 
$WDIR/ana_clusters.csh -best 4 analysis/cluster.out
$WDIR/cluster-fnat.csh 4
cd ../it0
$WDIR/i-rmsd_to_xray.csh 
$WDIR/l-rmsd_to_xray.csh 
$WDIR/ana_structures.csh
$WDIR/fraction-native.csh 
cd ../../../





