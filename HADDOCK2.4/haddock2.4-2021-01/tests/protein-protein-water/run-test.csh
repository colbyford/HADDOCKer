#!/bin/csh
#
set tname="PROTEIN-PROTEIN AIRs DOCKING WITH WATER REFINEMENT"
echo "=========================================================="
echo "=========================================================="
echo " RUNNING NOW " $tname " TEST"
echo "=========================================================="
source ../../haddock_configure.csh
haddock2.4 >&test.out
cd run1
patch -p0 -i ../run.cns.patch  >&/dev/null
haddock2.4 >>&../test.out
cd ..
./ana_scripts/run_all.csh run1 >&/dev/null
\rm run1/structures/it1/analysis/*out.gz run1/structures/it1/water/analysis/*out.gz >&/dev/null
if ( -e refe/run1 ) then
  cat /dev/null >diff.out
  diff run1/structures/it0/file.list refe/run1/structures/it0/file.list >> diff.out
  diff run1/structures/it1/file.list refe/run1/structures/it1/file.list >> diff.out
  diff run1/structures/it1/water/file.list refe/run1/structures/it1/water/file.list >> diff.out
  diff run1/structures/it0/i-RMSD.dat refe/run1/structures/it0/i-RMSD.dat >> diff.out
  diff run1/structures/it1/i-RMSD.dat refe/run1/structures/it1/i-RMSD.dat >> diff.out
  diff run1/structures/it1/water/i-RMSD.dat refe/run1/structures/it1/water/i-RMSD.dat >> diff.out
  if ( `wc -l diff.out | awk '{print $1}'` == 0 ) then
    echo "  >>>> No difference - test OK"
  else
    cat diff.out
  endif
else
  echo "No reference run present"
endif
echo "=========================================================="
echo " " $tname " TEST COMPLETED"
echo "=========================================================="
echo "=========================================================="
