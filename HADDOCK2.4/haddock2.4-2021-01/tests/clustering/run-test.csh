#!/bin/csh
#
set tname="CLUSTERING"
echo "=========================================================="
echo "=========================================================="
echo " RUNNING NOW " $tname " TEST"
echo "=========================================================="
source ../../haddock_configure.csh
$HADDOCKTOOLS/cluster_fcc.py protein-protein_fcc.disp 0.6 >cluster.out
if ( -e refe/cluster.out) then
  cat /dev/null >diff.out
  diff cluster.out refe/cluster.out >diff.out
  if ( `wc -l diff.out | awk '{print $1}'` == 0 ) then
    echo "  >>>> No difference - test OK"
  else
    cat diff.out
  endif
else
  echo "No reference clustering data present"
endif
echo "=========================================================="
echo " " $tname "TEST COMPLETED"
echo "=========================================================="
echo "=========================================================="
