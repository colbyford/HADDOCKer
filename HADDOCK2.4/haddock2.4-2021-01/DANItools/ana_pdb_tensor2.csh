#!/bin/csh
#
if ($#argv < 1) goto usage
#
echo "Note that you have to define manually the fitting options in the tensor2 GUI"
# Define the location of tensor2
#
if ( `printenv |grep TENSOR2 | wc -l` == 0) then
  set found=`which tensor2 |wc -l`
  if ($found == 0) then
     echo 'tensor2 environment variable not defined'
     echo '==> no fitting'
  else
     setenv TENSOR2 `which tensor2`
  endif
endif
#
\rm tmp.pdb tmp1 >&/dev/null
foreach i (*.pdb)
    $HADDOCKTOOLS/pdb_blank_segid $i |pdb_chain |pdb_reres >tmp.pdb
    tensor2 $1 tmp.pdb
    \rm tmp.pdb
    mkdir "tensor2_"$i:t:r
    mv resaniso.0 "tensor2_"$i:t:r
end
grep Dx tensor2_*/resaniso.0 > Dx_all.tmp
grep Dy tensor2_*/resaniso.0 > Dy_all.tmp
grep Dz tensor2_*/resaniso.0 > Dz_all.tmp
foreach i (tensor2_*/resaniso.0)
 grep Chi2 $i | tail -1 >> chi2_all.tmp
end
goto exit

usage:


echo 'ana_pdb_tensor2.csh: fits relaxation data using tensor2'
echo ' '
echo ' usage: ana_pdb_tensor2.csh tensor2_inputfile'

exit:

