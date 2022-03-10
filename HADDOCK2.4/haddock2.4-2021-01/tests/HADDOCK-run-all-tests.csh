#!/bin/csh
source ../haddock_configure.csh
\rm -rf */run1 */test.out */*conv.* >&/dev/null
cat /dev/null >HADDOCK-tests.diff
foreach i (./*/)
  date >>HADDOCK-tests.diff
  cd $i
  source ./run-test.csh >>../HADDOCK-tests.diff
  cd ..
end

