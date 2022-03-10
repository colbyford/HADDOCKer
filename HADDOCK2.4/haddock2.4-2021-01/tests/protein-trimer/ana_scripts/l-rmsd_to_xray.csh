#!/bin/csh
#
#C-terminal domain ignored in docking (large conf. change)
set refe=$HADDOCK/tests/protein-trimer/ana_scripts/1qu9_ABC.pdb
set atoms='CA,C,N,O'
#
# Define the location of profit
#
if ( `printenv |grep PROFIT | wc -l` == 0) then
  set found=`which profit |wc -l`
  if ($found == 0) then
     echo 'PROFIT environment variable not defined'
     echo '==> no rmsd calculations '
  else
     setenv PROFIT `which profit`
  endif
endif

cat /dev/null >rmsd_xray.disp

foreach i ($argv)
  if ($i:e == "gz") then
   gzip -dc $i > $i:t:r.tmp2
  else
   cp $i $i:t:r.tmp2
  endif
  $HADDOCKTOOLS/pdb_segid-to-chain $i:t:r.tmp2 >$i:t:r.tmp1
  echo $i >>rmsd_xray.disp
  $PROFIT <<_Eod_ |grep RMS >>rmsd_xray.disp
    refe $refe
    mobi $i:t:r.tmp1
    atom $atoms
    zone A*
    zone B*
    zone C*
    fit
    zone clear
    zone A*:A*
    zone B*:C*
    zone C*:B*
    fit
    zone clear
    zone A*
    fit
    rzone B*
    zone clear
    zone B*
    fit
    rzone C*
    zone clear
    zone C*
    fit
    rzone A* 
    zone clear
    zone A*
    fit
    rzone B*:C*
    zone clear
    zone B*
    fit
    rzone C*:A*
    zone clear
    zone C*
    fit
    rzone A*:B*
    quit
_Eod_
rm -f $i:t:r.tmp1
rm -f $i:t:r.tmp2
end
echo '#file l-RMSD-best ABC ACB l-RMSD-AB l-RMSD-BC l-RMSD-CA l-RMSD-AB/C l-RMSD-BC/A l-RMSD-CA/B' >l-RMSD.dat
echo '#file l-RMSD-best ABC ACB l-RMSD-AB l-RMSD-BC l-RMSD-CA l-RMSD-AB/C l-RMSD-BC/A l-RMSD-CA/B' >l-RMSD-sorted.dat
awk '{if ($1 == "RMS:") {printf "%8.3f ",$2} else {printf "\n %s ",$1}}' rmsd_xray.disp |grep pdb >tt
cat tt | awk '{best=$5;if($7<best){best=$7};if($9<best){best=$9};if($11<best){best=$11};if($13<best){best=$13};if($15<best){best=$15};print $1,best,$2,$3,$5,$7,$9,$11,$13,$15}' >> l-RMSD.dat
cat tt | awk '{best=$5;if($7<best){best=$7};if($9<best){best=$9};if($11<best){best=$11};if($13<best){best=$13};if($15<best){best=$15};print $1,best,$2,$3,$5,$7,$9,$11,$13,$15}' |sort -n -k2 >> l-RMSD-sorted.dat
\rm rmsd_xray.disp tt

