#!/bin/csh
source ../haddock_configure.csh
rm -rf */refe/* */run1 */test.out
foreach i (./*/)
  date 
  cd $i
  if (! -e refe) mkdir refe
  source ./run-test.csh
  if ( -e run1 ) mv run1 refe
  if ( -e test.out ) mv test.out refe
  if ( -e file.nam ) mv file.nam refe/
  if ( -e file.list) mv file.list refe/
  if ( -e cluster.out) mv cluster.out refe/
  cd ..
end
