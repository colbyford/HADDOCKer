#!/bin/csh
#
setenv WDIR $HADDOCK/examples/protein-peptide/ana_scripts
set REFE=$WDIR/1nx1_refe.contacts
mkdir contacts
foreach i ($argv)
  $HADDOCKTOOLS/contact $i 5.0 | awk '{if ($5<$2){print $4,$5,$6,$1,$2,$3,$7} else {print $0}}' > contacts/$i:t:r".contacts"
  echo $i |awk '{printf "%s ",$1}' >>file.nam_fnat
  awk '{nr = 100000 * $1 + $4} FILENAME == ARGV[1] && (!(nr in done1)){done1[nr] = 1; counter++; contact[nr] = $1} FILENAME == ARGV[2] && (!(nr in done2)) {done2[nr] = 1; if(nr in contact) natcounter++} END {print natcounter / counter}' $REFE contacts/$i:t:r".contacts" >>file.nam_fnat
end

