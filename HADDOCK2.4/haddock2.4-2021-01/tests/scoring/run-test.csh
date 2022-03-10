#!/bin/csh
#
set tname="SCORING"
echo "=========================================================="
echo "=========================================================="
echo " RUNNING NOW " $tname " TEST"
echo "=========================================================="
source ../../haddock_configure.csh
set cnsexe=`grep cns_exe_1 $HADDOCK/protocols/run.cns | awk -F \" '{print $2}'`
$cnsexe <$HADDOCK/protocols-scoring/scoring.inp >scoring.out
./extract-score.csh *conv.pdb
if ( -e refe/file.list) then
  cat /dev/null >diff.out
  diff file.list refe/file.list >diff.out
  if (`wc -l diff.out |awk '{print $1}'` == 0) then
    \rm *_conv.* scoring.out
  endif
  if ( `wc -l diff.out | awk '{print $1}'` == 0 ) then
    echo "  >>>> No difference - test OK"
  else
    cat diff.out
  endif
else
  \rm *_conv.* scoring.out
  echo "No reference scoring data present"
endif
echo "=========================================================="
echo " " $tname "TEST COMPLETED"
echo "=========================================================="
echo "=========================================================="
