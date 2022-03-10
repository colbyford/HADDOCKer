#!/bin/csh
#
foreach i ($argv)
  echo $i
  echo '#it0: structures with l-RMSD<10A:' |awk '{printf "  %s %s %s %s %s ",$1,$2,$3,$4,$5}'
  grep pdb $i/structures/it0/l-RMSD.dat | awk '$2<=10' | wc -l
  echo '#it0: structures within best200 with l-RMSD<10A:' |awk '{printf "  %s %s %s %s %s %s ",$1,$2,$3,$4,$5,$6}'
  grep pdb $i/structures/it0/l-RMSD.dat | head -200 | awk '$2<=10' | wc -l
  echo '#it0: structures within best200 with l-RMSD<5A:' |awk '{printf "  %s %s %s %s %s %s ",$1,$2,$3,$4,$5,$6}'
  grep pdb $i/structures/it0/l-RMSD.dat | head -200 | awk '$2<=5' | wc -l
  echo '#it0: structures within best200 with l-RMSD<1A:' |awk '{printf "  %s %s %s %s %s %s ",$1,$2,$3,$4,$5,$6}'
  grep pdb $i/structures/it0/l-RMSD.dat | head -200 | awk '$2<=1' | wc -l
  echo '#it1: structures with l-RMSD<10A:' |awk '{printf "  %s %s %s %s %s ",$1,$2,$3,$4,$5}'
  grep pdb $i/structures/it1/l-RMSD.dat | awk '$2<=10' | wc -l
  echo '#it1: structures with l-RMSD<5A:' |awk '{printf "  %s %s %s %s %s ",$1,$2,$3,$4,$5}'
  grep pdb $i/structures/it1/l-RMSD.dat | awk '$2<=5' | wc -l
  echo '#it1: structures with l-RMSD<1A:' |awk '{printf "  %s %s %s %s %s ",$1,$2,$3,$4,$5}'
  grep pdb $i/structures/it1/l-RMSD.dat | awk '$2<=1' | wc -l
  echo '#water: structures with l-RMSD<10A:' |awk '{printf "  %s %s %s %s %s ",$1,$2,$3,$4,$5}'
  grep pdb $i/structures/it1/water/l-RMSD.dat | awk '$2<=10' | wc -l
  echo '#water: structures with l-RMSD<5A:' |awk '{printf "  %s %s %s %s %s ",$1,$2,$3,$4,$5}'
  grep pdb $i/structures/it1/water/l-RMSD.dat | awk '$2<=5' | wc -l
  echo '#water: structures with l-RMSD<1A:' |awk '{printf "  %s %s %s %s %s ",$1,$2,$3,$4,$5}'
  grep pdb $i/structures/it1/water/l-RMSD.dat | awk '$2<=1' | wc -l
end

