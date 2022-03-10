#!/bin/csh
#
foreach i ($argv)
  echo $i
  echo '#it0: structures with i-RMSD<4A:' |awk '{printf "  %s %s %s %s %s ",$1,$2,$3,$4,$5}'
  grep pdb $i/structures/it0/i-RMSD.dat | awk '$2<=4' | wc -l
  echo '#it0: structures within best200 with i-RMSD<4A:' |awk '{printf "  %s %s %s %s %s %s ",$1,$2,$3,$4,$5,$6}'
  grep pdb $i/structures/it0/i-RMSD.dat | head -200 | awk '$2<=4' | wc -l
  echo '#it0: structures within best200 with i-RMSD<2A:' |awk '{printf "  %s %s %s %s %s %s ",$1,$2,$3,$4,$5,$6}'
  grep pdb $i/structures/it0/i-RMSD.dat | head -200 | awk '$2<=2' | wc -l
  echo '#it0: structures within best200 with i-RMSD<1A:' |awk '{printf "  %s %s %s %s %s %s ",$1,$2,$3,$4,$5,$6}'
  grep pdb $i/structures/it0/i-RMSD.dat | head -200 | awk '$2<=1' | wc -l
  echo '#it1: structures with i-RMSD<4A:' |awk '{printf "  %s %s %s %s %s ",$1,$2,$3,$4,$5}'
  grep pdb $i/structures/it1/i-RMSD.dat | awk '$2<=4' | wc -l
  echo '#it1: structures with i-RMSD<2A:' |awk '{printf "  %s %s %s %s %s ",$1,$2,$3,$4,$5}'
  grep pdb $i/structures/it1/i-RMSD.dat | awk '$2<=2' | wc -l
  echo '#it1: structures with i-RMSD<1A:' |awk '{printf "  %s %s %s %s %s ",$1,$2,$3,$4,$5}'
  grep pdb $i/structures/it1/i-RMSD.dat | awk '$2<=1' | wc -l
  echo '#water: structures with i-RMSD<4A:' |awk '{printf "  %s %s %s %s %s ",$1,$2,$3,$4,$5}'
  grep pdb $i/structures/it1/water/i-RMSD.dat | awk '$2<=4' | wc -l
  echo '#water: structures with i-RMSD<2A:' |awk '{printf "  %s %s %s %s %s ",$1,$2,$3,$4,$5}'
  grep pdb $i/structures/it1/water/i-RMSD.dat | awk '$2<=2' | wc -l
  echo '#water: structures with i-RMSD<1A:' |awk '{printf "  %s %s %s %s %s ",$1,$2,$3,$4,$5}'
  grep pdb $i/structures/it1/water/i-RMSD.dat | awk '$2<=1' | wc -l
end

