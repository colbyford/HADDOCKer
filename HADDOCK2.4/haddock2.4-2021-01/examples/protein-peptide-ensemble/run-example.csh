#!/bin/csh
#
source ../../haddock_configure.csh
echo "=========================================================="
echo "=========================================================="
echo " RUNNING NOW PROTEIN-PEPTIDE ENSEMBLE DOCKING EXAMPLE"
date
echo "=========================================================="
echo "=========================================================="
haddock2.4 >&/dev/null
cd run1
patch -p0 -i ../run.cns.patch  >&/dev/null
haddock2.4 >>&haddock.out
cd ..
\rm run1/structures/it1/analysis/*out.gz run1/structures/it1/water/analysis/*out.gz >&/dev/null
echo "=========================================================="
echo "=========================================================="
echo " PROTEIN-PEPTIDE ENSEMBLE DOCKING EXAMPLE COMPLETED"
date
echo "=========================================================="
echo "=========================================================="
