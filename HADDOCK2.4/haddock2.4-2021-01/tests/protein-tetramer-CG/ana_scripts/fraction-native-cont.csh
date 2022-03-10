#!/bin/csh
#
setenv WDIR $HADDOCK/tests/protein-tetramer-CG/ana_scripts
set REFE=$WDIR/3GD8_tetramer.contacts
#cat /dev/null >file.nam_fnat

foreach i (`cat file.nam`)
  $HADDOCKTOOLS/contact $i 5.0 > $i:t:r".contacts"
  echo $i |awk '{printf "%s ",$1}'  | awk '{if ($5<$2){print $4,$5,$6,$1,$2,$3,$7} else {print $0}}' >>file.nam_fnat
  set fnat=`awk '{nr = 100000 * $1 + $4} FILENAME == ARGV[1] && (!(nr in done1)){done1[nr] = 1; counter++; contact[nr] = $1} FILENAME == ARGV[2] && (!(nr in done2)) {done2[nr] = 1; if(nr in contact) natcounter++} END {print natcounter / counter}' $REFE $i:t:r".contacts"`
  echo $fnat >> file.nam_fnat
  \rm $i:t:r".contacts"
end
sort -nrk 2 file.nam_fnat > file.nam_fnat-sorted
