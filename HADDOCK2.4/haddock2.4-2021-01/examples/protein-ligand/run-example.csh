#!/bin/csh
#
source ../../haddock_configure.csh
echo "=========================================================="
echo "=========================================================="
echo " RUNNING NOW THE NEURAMINIDASE PROTEIN-LIGAND DOCKING EXAMPLE"
echo "=========================================================="
echo "=========================================================="
haddock2.4 >&/dev/null
cd run1
\cp ../ligand-prodrg.param  toppar/ligand.param
\cp ../ligand-prodrg.top toppar/ligand.top
patch -p0 -i ../run.cns.patch  >&/dev/null
haddock2.4 >&haddock.out
cd ..
./ana_scripts/run_all.csh run1 >&/dev/null
../results-stats-ligand.csh run1 
echo "=========================================================="
echo "=========================================================="
echo " NEURAMINIDASE PROTEIN-LIGAND DOCKING EXAMPLE COMPLETED"
echo "=========================================================="
echo "=========================================================="
