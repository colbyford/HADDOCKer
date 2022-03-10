#!/bin/csh
#
setenv WDIR $HADDOCK/examples/protein-ligand/ana_scripts
set REFE=$WDIR/target.contacts5
mkdir contacts
foreach i (`cat file.nam`)
  $HADDOCKTOOLS/contact $i 5.0 > contacts/$i:t:r".contacts"
  echo $i |awk '{printf "%s ",$1}' >>file.nam_fnat
  awk '{nr = 100000 * $1 + $4} FILENAME == ARGV[1] && (!(nr in done1)){done1[nr] = 1; counter++; contact[nr] = $1} FILENAME == ARGV[2] && (!(nr in done2)) {done2[nr] = 1; if(nr in contact) natcounter++} END {print natcounter / counter}' $REFE contacts/$i:t:r".contacts" >>file.nam_fnat
end

