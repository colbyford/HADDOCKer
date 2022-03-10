#!/bin/csh
#
echo "=========================================================="
echo "=========================================================="
echo " RUNNING NOW PROTEIN-LIGAND SHAPE-BASED DOCKING EXAMPLE"
echo "=========================================================="
echo "=========================================================="
source ../../haddock_configure.csh
haddock2.4 >&run.out
cd run1
\cp ../ligand-par/* toppar
\cp ../ligand-par/* toppar
patch -p0 -i ../run.cns.patch  >&/dev/null
haddock2.4 >>&haddock.out
grep Finishing haddock.out >>&../run.out
cd ..
./ana_scripts/run_all.csh run1 >&/dev/null
../results-stats-ligand.csh run1 
\rm run1/structures/it1/analysis/*out.gz run1/structures/it1/water/analysis/*out.gz >&/dev/null
echo "=========================================================="
echo "=========================================================="
echo " PROTEIN-LIGAND SHAPE-BASED DOCKING EXAMPLE COMPLETED"
echo "=========================================================="
echo "=========================================================="
