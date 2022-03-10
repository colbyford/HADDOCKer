#!/bin/csh
#
echo "=========================================================="
echo "=========================================================="
echo " RUNNING NOW PROTEIN-PROTEIN RDCS DOCKING EXAMPLE"
echo "=========================================================="
echo "=========================================================="
source ../../haddock_configure.csh
haddock2.4 >&run.out
cd run1
patch -p0 -i ../run.cns.patch  >&/dev/null
haddock2.4 >&haddock.out
grep Finishing haddock.out >>&../run.out
cd ..
./ana_scripts/run_all.csh run1 >&/dev/null
../results-stats.csh run1
echo "=========================================================="
echo "=========================================================="
echo " DI-UBIQUITIN RDCS DOCKING EXAMPLE COMPLETED"
echo "=========================================================="
echo "=========================================================="
