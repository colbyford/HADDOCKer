#!/bin/csh

set dx=$1
set dy=$2
set dz=$3

set scale=1E8
echo "calculating tensor params using dx=$1,dy=$2,dz=$3; scale="$scale

set tc = `echo $dx $dy $dz | awk '{print 1/(2*($1*a+$2*a+$3*a))}' a=$scale`
set anis = `echo $dx $dy $dz | awk '{print $3/(0.5*($1+$2))}'`
set r = `echo $dx $dy $dz | awk '{print 1.5*($2-$1)/($3-0.5*($1+$2))}'`

echo "tc = " $tc
echo "anis = " $anis
echo "r = " $r
