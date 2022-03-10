#!/bin/csh -f
#
setenv target protein-ligand 
setenv WDIR $HADDOCK/examples/protein-ligand/ana_scripts

cd $1/structures/it1/water/analysis
gunzip cluster.out.gz; \rm *out.gz
cd ..
$WDIR/i-rmsd_to_xray.csh 
$WDIR/l-rmsd_to_xray.csh 
$HADDOCKTOOLS/ana_structures-ligand.csh
$WDIR/fraction-native.csh 
$HADDOCKTOOLS/ana_clusters-ligand.csh -best 4 analysis/cluster.out
$WDIR/cluster-fnat.csh 4
cd ../analysis
gunzip cluster.out.gz; \rm *out.gz
cd ..
$WDIR/i-rmsd_to_xray.csh 
$WDIR/l-rmsd_to_xray.csh 
$HADDOCKTOOLS/ana_structures-ligand.csh
$WDIR/fraction-native.csh 
$HADDOCKTOOLS/ana_clusters-ligand.csh -best 4 analysis/cluster.out
$WDIR/cluster-fnat.csh 4
cd ../it0
$WDIR/i-rmsd_to_xray.csh 
$WDIR/l-rmsd_to_xray.csh
$HADDOCKTOOLS/ana_structures-ligand.csh
$WDIR/fraction-native.csh 
cd ../../../





