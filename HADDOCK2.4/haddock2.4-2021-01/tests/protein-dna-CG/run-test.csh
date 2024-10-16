#!/bin/csh
#
set tname="PROTEIN-DNA CG"
echo "=========================================================="
echo "=========================================================="
echo " RUNNING NOW " $tname " TEST"
echo "=========================================================="
source ../../haddock_configure.csh
haddock2.4 >&test.out
\cp dna-rna_restraints.def run1/data/sequence/dna-rna_restraints.def
cd run1
bash ../patch-run.sh
haddock2.4 >>&../test.out
cd ..
\rm run1/structures/it1/analysis/*out.gz run1/structures/it1/water/analysis/*out.gz >&/dev/null
if ( -e refe/run1 ) then
  cat /dev/null >diff.out
  diff run1/structures/it0/file.list refe/run1/structures/it0/file.list >> diff.out
  diff run1/structures/it1/file.list refe/run1/structures/it1/file.list >> diff.out
  diff run1/structures/it1/water/file.list refe/run1/structures/it1/water/file.list >> diff.out
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
