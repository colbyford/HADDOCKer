#!/bin/csh
#
echo "=========================================================="
echo "=========================================================="
echo " ANALYSING NOW CYCLIC PEPTIDE N-acetyl to CYS sulphur TEST"
echo "=========================================================="
cd cyclic-ace-cys-link
cat /dev/null >diff.out
diff run1/structures/it0/file.list refe/run1/structures/it0/file.list >> diff.out
diff run1/structures/it1/file.list refe/run1/structures/it1/file.list >> diff.out
diff run1/structures/it1/water/file.list refe/run1/structures/it1/water/file.list >> diff.out
if ( `wc -l diff.out | awk '{print $1}'` == 0 ) then
  echo "  >>>> No difference - test OK"
else
  cat diff.out
endif
cd ..
echo "=========================================================="
echo " CYCLIC PEPTIDE TEST COMPLETED"
echo "=========================================================="
echo "=========================================================="

echo "=========================================================="
echo "=========================================================="
echo " ANALYSING NOW CYCLIC PEPTIDE PEPTIDIC BOND TEST"
echo "=========================================================="
cd cyclic-peptide
cat /dev/null >diff.out
diff run1/structures/it0/file.list refe/run1/structures/it0/file.list >> diff.out
diff run1/structures/it1/file.list refe/run1/structures/it1/file.list >> diff.out
diff run1/structures/it1/water/file.list refe/run1/structures/it1/water/file.list >> diff.out
if ( `wc -l diff.out | awk '{print $1}'` == 0 ) then
  echo "  >>>> No difference - test OK"
else
  cat diff.out
endif
cd ..
echo "=========================================================="
echo " CYCLIC PEPTIDE TEST COMPLETED"
echo "=========================================================="
echo "=========================================================="

echo "=========================================================="
echo "=========================================================="
echo " ANALYSING NOW D-AMINO ACID DETECTION TEST"
echo "=========================================================="
cd d-amino-acid
cat /dev/null >diff.out
diff run1/structures/it0/file.list refe/run1/structures/it0/file.list >> diff.out
diff run1/structures/it1/file.list refe/run1/structures/it1/file.list >> diff.out
diff run1/structures/it1/water/file.list refe/run1/structures/it1/water/file.list >> diff.out
if ( `wc -l diff.out | awk '{print $1}'` == 0 ) then
  echo "  >>>> No difference - test OK"
else
  cat diff.out
endif
cd ..
echo "=========================================================="
echo " D-AMINO ACID DETECTION TEST COMPLETED"
echo "=========================================================="
echo "=========================================================="

echo "=========================================================="
echo "=========================================================="
echo " ANALYSING NOW NUCLEOSOME CG DOCKING TEST"
echo "=========================================================="
cd nucleosome
cat /dev/null >diff.out
diff run1/structures/it0/file.list refe/run1/structures/it0/file.list >> diff.out
diff run1/structures/it1/file.list refe/run1/structures/it1/file.list >> diff.out
diff run1/structures/it1/water/file.list refe/run1/structures/it1/water/file.list >> diff.out
if ( `wc -l diff.out | awk '{print $1}'` == 0 ) then
  echo "  >>>> No difference - test OK"
else
  cat diff.out
endif
cd ..
echo "=========================================================="
echo " NUCLEOSOME CG DOCKING TEST COMPLETED"
echo "=========================================================="
echo "=========================================================="

echo "=========================================================="
echo "=========================================================="
echo " ANALYSING NOW NUCLEOSOME DOCKING TEST"
echo "=========================================================="
cd nucleosome-CG
cat /dev/null >diff.out
diff run1/structures/it0/file.list refe/run1/structures/it0/file.list >> diff.out
diff run1/structures/it1/file.list refe/run1/structures/it1/file.list >> diff.out
diff run1/structures/it1/water/file.list refe/run1/structures/it1/water/file.list >> diff.out
if ( `wc -l diff.out | awk '{print $1}'` == 0 ) then
  echo "  >>>> No difference - test OK"
else
  cat diff.out
endif
cd ..
echo "=========================================================="
echo " NUCLEOSOME DOCKING TEST COMPLETED"
echo "=========================================================="
echo "=========================================================="

echo "=========================================================="
echo "=========================================================="
echo " ANALYSING NOW PROTEIN-DNA CG TEST"
echo "=========================================================="
cd protein-dna-CG
cat /dev/null >diff.out
diff run1/structures/it0/file.list refe/run1/structures/it0/file.list >> diff.out
diff run1/structures/it1/file.list refe/run1/structures/it1/file.list >> diff.out
diff run1/structures/it1/water/file.list refe/run1/structures/it1/water/file.list >> diff.out
if ( `wc -l diff.out | awk '{print $1}'` == 0 ) then
  echo "  >>>> No difference - test OK"
else
  cat diff.out
endif
cd ..
echo "=========================================================="
echo " PROTEIN-DNA CG TEST COMPLETED"
echo "=========================================================="
echo "=========================================================="

echo "=========================================================="
echo "=========================================================="
echo " ANALYSING NOW PROTEIN-DNA TEST"
echo "=========================================================="
cd protein-dna
cat /dev/null >diff.out
diff run1/structures/it0/file.list refe/run1/structures/it0/file.list >> diff.out
diff run1/structures/it1/file.list refe/run1/structures/it1/file.list >> diff.out
diff run1/structures/it1/water/file.list refe/run1/structures/it1/water/file.list >> diff.out
diff run1/structures/it0/i-RMSD.dat refe/run1/structures/it0/i-RMSD.dat >> diff.out
diff run1/structures/it1/i-RMSD.dat refe/run1/structures/it1/i-RMSD.dat >> diff.out
diff run1/structures/it1/water/i-RMSD.dat refe/run1/structures/it1/water/i-RMSD.dat >> diff.out
if ( `wc -l diff.out | awk '{print $1}'` == 0 ) then
  echo "  >>>> No difference - test OK"
else
  cat diff.out
endif
cd ..
echo "=========================================================="

echo "=========================================================="
echo "=========================================================="
echo " ANALYSING NOW PROTEIN-DUMMY TEST"
echo "=========================================================="
cd protein-dummy
cat /dev/null >diff.out
diff run1/structures/it0/file.list refe/run1/structures/it0/file.list >> diff.out
diff run1/structures/it1/file.list refe/run1/structures/it1/file.list >> diff.out
diff run1/structures/it1/water/file.list refe/run1/structures/it1/water/file.list >> diff.out
if ( `wc -l diff.out | awk '{print $1}'` == 0 ) then
  echo "  >>>> No difference - test OK"
else
  cat diff.out
endif
cd ..
echo "=========================================================="
echo " PROTEIN-DUMMY TEST COMPLETED"
echo "=========================================================="
echo "=========================================================="

echo "=========================================================="
echo "=========================================================="
echo " ANALYSING NOW PROTEIN-LIGAND SHAPE TEST"
echo "=========================================================="
cd protein-ligand-shape
cat /dev/null >diff.out
diff run1/structures/it0/file.list refe/run1/structures/it0/file.list >> diff.out
diff run1/structures/it1/file.list refe/run1/structures/it1/file.list >> diff.out
diff run1/structures/it1/water/file.list refe/run1/structures/it1/water/file.list >> diff.out
diff run1/structures/it0/i-RMSD.dat refe/run1/structures/it0/i-RMSD.dat >> diff.out
diff run1/structures/it1/i-RMSD.dat refe/run1/structures/it1/i-RMSD.dat >> diff.out
diff run1/structures/it1/water/i-RMSD.dat refe/run1/structures/it1/water/i-RMSD.dat >> diff.out
if ( `wc -l diff.out | awk '{print $1}'` == 0 ) then
  echo "  >>>> No difference - test OK"
else
  cat diff.out
endif
cd ..
echo "=========================================================="
echo " PROTEIN-LIGAND SHAPE TEST COMPLETED"
echo "=========================================================="
echo "=========================================================="

echo "=========================================================="
echo "=========================================================="
echo " ANALYSING NOW PROTEIN-LIGAND TEST"
echo "=========================================================="
cd protein-ligand
cat /dev/null >diff.out
diff run1/structures/it0/file.list refe/run1/structures/it0/file.list >> diff.out
diff run1/structures/it1/file.list refe/run1/structures/it1/file.list >> diff.out
diff run1/structures/it1/water/file.list refe/run1/structures/it1/water/file.list >> diff.out
diff run1/structures/it0/i-RMSD.dat refe/run1/structures/it0/i-RMSD.dat >> diff.out
diff run1/structures/it1/i-RMSD.dat refe/run1/structures/it1/i-RMSD.dat >> diff.out
diff run1/structures/it1/water/i-RMSD.dat refe/run1/structures/it1/water/i-RMSD.dat >> diff.out
if ( `wc -l diff.out | awk '{print $1}'` == 0 ) then
  echo "  >>>> No difference - test OK"
else
  cat diff.out
endif
cd ..
echo "=========================================================="
echo " PROTEIN-LIGAND TEST COMPLETED"
echo "=========================================================="
echo "=========================================================="

echo "=========================================================="
echo "=========================================================="
echo " ANALYSING NOW PROTEIN-PEPTIDE ENSEMBLE DOCKING TEST"
echo "=========================================================="
cd protein-peptide-ensemble
cat /dev/null >diff.out
diff run1/structures/it0/file.list refe/run1/structures/it0/file.list >> diff.out
diff run1/structures/it1/file.list refe/run1/structures/it1/file.list >> diff.out
diff run1/structures/it1/water/file.list refe/run1/structures/it1/water/file.list >> diff.out
if ( `wc -l diff.out | awk '{print $1}'` == 0 ) then
  echo "  >>>> No difference - test OK"
else
  cat diff.out
endif
cd ..
echo "=========================================================="
echo " PROTEIN-PEPTIDE ENSEMBLE DOCKING TEST COMPLETED"
echo "=========================================================="
echo "=========================================================="

echo "=========================================================="
echo "=========================================================="
echo " ANALYSING NOW PROTEIN-PEPTIDE DOCKING TEST"
echo "=========================================================="
cd protein-peptide
cat /dev/null >diff.out
diff run1/structures/it0/file.list refe/run1/structures/it0/file.list >> diff.out
diff run1/structures/it1/file.list refe/run1/structures/it1/file.list >> diff.out
diff run1/structures/it1/water/file.list refe/run1/structures/it1/water/file.list >> diff.out
diff run1/structures/it0/i-RMSD.dat refe/run1/structures/it0/i-RMSD.dat >> diff.out
diff run1/structures/it1/i-RMSD.dat refe/run1/structures/it1/i-RMSD.dat >> diff.out
diff run1/structures/it1/water/i-RMSD.dat refe/run1/structures/it1/water/i-RMSD.dat >> diff.out
if ( `wc -l diff.out | awk '{print $1}'` == 0 ) then
  echo "  >>>> No difference - test OK"
else
  cat diff.out
endif
cd ..
echo "=========================================================="
echo " PROTEIN-PEPTIDE TEST COMPLETED"
echo "=========================================================="
echo "=========================================================="

echo "=========================================================="
echo "=========================================================="
echo " ANALYSING NOW PROTEIN-PROTEIN E2A-HPR DANI DOCKING TEST"
echo "=========================================================="
cd protein-protein-dani
cat /dev/null >diff.out
diff run1/structures/it0/file.list refe/run1/structures/it0/file.list >> diff.out
diff run1/structures/it1/file.list refe/run1/structures/it1/file.list >> diff.out
diff run1/structures/it1/water/file.list refe/run1/structures/it1/water/file.list >> diff.out
diff run1/structures/it0/i-RMSD.dat refe/run1/structures/it0/i-RMSD.dat >> diff.out
diff run1/structures/it1/i-RMSD.dat refe/run1/structures/it1/i-RMSD.dat >> diff.out
diff run1/structures/it1/water/i-RMSD.dat refe/run1/structures/it1/water/i-RMSD.dat >> diff.out
if ( `wc -l diff.out | awk '{print $1}'` == 0 ) then
  echo "  >>>> No difference - test OK"
else
  cat diff.out
endif
cd ..
echo "=========================================================="
echo " E2A-HPR DANI DOCKING TEST COMPLETED"
echo "=========================================================="
echo "=========================================================="

echo "=========================================================="
echo "=========================================================="
echo " ANALYSING NOW PROTEIN-PROTEIN-EM TEST"
echo "=========================================================="
cd protein-protein-em
cat /dev/null >diff.out
diff run1/structures/it0/file.list refe/run1/structures/it0/file.list >> diff.out
diff run1/structures/it1/file.list refe/run1/structures/it1/file.list >> diff.out
diff run1/structures/it1/water/file.list refe/run1/structures/it1/water/file.list >> diff.out
diff run1/structures/it0/i-RMSD.dat refe/run1/structures/it0/i-RMSD.dat >> diff.out
diff run1/structures/it1/i-RMSD.dat refe/run1/structures/it1/i-RMSD.dat >> diff.out
diff run1/structures/it1/water/i-RMSD.dat refe/run1/structures/it1/water/i-RMSD.dat >> diff.out
if ( `wc -l diff.out | awk '{print $1}'` == 0 ) then
  echo "  >>>> No difference - test OK"
else
  cat diff.out
endif
cd ..
echo "=========================================================="
echo " PROTEIN-PROTEIN-EM DOCKING TEST COMPLETED"
echo "=========================================================="
echo "=========================================================="

echo "=========================================================="
echo "=========================================================="
echo " ANALYSING NOW PROTEIN-PROTEIN E2A-HPR DOCKING TEST NOWAT"
echo "=========================================================="
cd protein-protein-nowat
cat /dev/null >diff.out
diff run1/structures/it0/file.list refe/run1/structures/it0/file.list >> diff.out
diff run1/structures/it1/file.list refe/run1/structures/it1/file.list >> diff.out
diff run1/structures/it1/water/file.list refe/run1/structures/it1/water/file.list >> diff.out
diff run1/structures/it0/i-RMSD.dat refe/run1/structures/it0/i-RMSD.dat >> diff.out
diff run1/structures/it1/i-RMSD.dat refe/run1/structures/it1/i-RMSD.dat >> diff.out
diff run1/structures/it1/water/i-RMSD.dat refe/run1/structures/it1/water/i-RMSD.dat >> diff.out
if ( `wc -l diff.out | awk '{print $1}'` == 0 ) then
  echo "  >>>> No difference - test OK"
else
  cat diff.out
endif
cd ..
echo "=========================================================="
echo " E2A-HPR DOCKING TEST NOWAT COMPLETED"
echo "=========================================================="
echo "=========================================================="

echo "=========================================================="
echo "=========================================================="
echo " ANALYSING NOW PROTEIN-PROTEIN EPS-HOT PCS DOCKING TEST"
echo "=========================================================="
cd protein-protein-pcs
cat /dev/null >diff.out
diff run1/structures/it0/file.list refe/run1/structures/it0/file.list >> diff.out
diff run1/structures/it1/file.list refe/run1/structures/it1/file.list >> diff.out
diff run1/structures/it1/water/file.list refe/run1/structures/it1/water/file.list >> diff.out
diff run1/structures/it0/i-RMSD.dat refe/run1/structures/it0/i-RMSD.dat >> diff.out
diff run1/structures/it1/i-RMSD.dat refe/run1/structures/it1/i-RMSD.dat >> diff.out
diff run1/structures/it1/water/i-RMSD.dat refe/run1/structures/it1/water/i-RMSD.dat >> diff.out
if ( `wc -l diff.out | awk '{print $1}'` == 0 ) then
  echo "  >>>> No difference - test OK"
else
  cat diff.out
endif
cd ..
echo "=========================================================="
echo " EPS-HOT PCS DOCKING TEST COMPLETED"
echo "=========================================================="
echo "=========================================================="

echo "=========================================================="
echo "=========================================================="
echo " ANALYSING NOW PROTEIN-PROTEIN RDCS DOCKING TEST"
echo "=========================================================="
cd protein-protein-rdc
cat /dev/null >diff.out
diff run1/structures/it0/file.list refe/run1/structures/it0/file.list >> diff.out
diff run1/structures/it1/file.list refe/run1/structures/it1/file.list >> diff.out
diff run1/structures/it1/water/file.list refe/run1/structures/it1/water/file.list >> diff.out
diff run1/structures/it0/i-RMSD.dat refe/run1/structures/it0/i-RMSD.dat >> diff.out
diff run1/structures/it1/i-RMSD.dat refe/run1/structures/it1/i-RMSD.dat >> diff.out
diff run1/structures/it1/water/i-RMSD.dat refe/run1/structures/it1/water/i-RMSD.dat >> diff.out
if ( `wc -l diff.out | awk '{print $1}'` == 0 ) then
  echo "  >>>> No difference - test OK"
else
  cat diff.out
endif
cd ..
echo "=========================================================="
echo " DI-UBIQUITIN RDCS DOCKING TEST COMPLETED"
echo "=========================================================="
echo "=========================================================="

echo "=========================================================="
echo "=========================================================="
echo " ANALYSING NOW PROTEIN-PROTEIN E2A-HPR DOCKING TEST"
echo "=========================================================="
cd protein-protein
cat /dev/null >diff.out
diff run1/structures/it0/file.list refe/run1/structures/it0/file.list >> diff.out
diff run1/structures/it1/file.list refe/run1/structures/it1/file.list >> diff.out
diff run1/structures/it1/water/file.list refe/run1/structures/it1/water/file.list >> diff.out
diff run1/structures/it0/i-RMSD.dat refe/run1/structures/it0/i-RMSD.dat >> diff.out
diff run1/structures/it1/i-RMSD.dat refe/run1/structures/it1/i-RMSD.dat >> diff.out
diff run1/structures/it1/water/i-RMSD.dat refe/run1/structures/it1/water/i-RMSD.dat >> diff.out
if ( `wc -l diff.out | awk '{print $1}'` == 0 ) then
  echo "  >>>> No difference - test OK"
else
  cat diff.out
endif
cd ..
echo "=========================================================="
echo " E2A-HPR DOCKING TEST COMPLETED"
echo "=========================================================="
echo "=========================================================="

echo "=========================================================="
echo "=========================================================="
echo " ANALYSING NOW SINGLE STRUCTURE PCS REFINEMENT TEST"
echo "=========================================================="
cd protein-refine-pcs
cat /dev/null >diff.out
diff run1/structures/it0/file.list refe/run1/structures/it0/file.list >> diff.out
diff run1/structures/it1/file.list refe/run1/structures/it1/file.list >> diff.out
diff run1/structures/it1/water/file.list refe/run1/structures/it1/water/file.list >> diff.out
if ( `wc -l diff.out | awk '{print $1}'` == 0 ) then
  echo "  >>>> No difference - test OK"
else
  cat diff.out
endif
cd ..
echo "=========================================================="
echo " SINGLE STRUCTURE PCS REFINEMENT TEST COMPLETED"
echo "=========================================================="
echo "=========================================================="

echo "=========================================================="
echo "=========================================================="
echo " ANALYSING NOW PROTEIN-TETRAMER 3GD8 CG TEST"
echo "=========================================================="
cd protein-tetramer-CG
cat /dev/null >diff.out
diff run1/structures/it0/file.list refe/run1/structures/it0/file.list >> diff.out
diff run1/structures/it1/file.list refe/run1/structures/it1/file.list >> diff.out
diff run1/structures/it1/water/file.list refe/run1/structures/it1/water/file.list >> diff.out
diff run1/structures/it0/i-RMSD.dat refe/run1/structures/it0/i-RMSD.dat >> diff.out
diff run1/structures/it1/i-RMSD.dat refe/run1/structures/it1/i-RMSD.dat >> diff.out
diff run1/structures/it1/water/i-RMSD.dat refe/run1/structures/it1/water/i-RMSD.dat >> diff.out
if ( `wc -l diff.out | awk '{print $1}'` == 0 ) then
  echo "  >>>> No difference - test OK"
else
  cat diff.out
endif
cd ..
echo "=========================================================="
echo " 3GD8 CG TEST COMPLETED"
echo "=========================================================="
echo "=========================================================="

echo "=========================================================="
echo "=========================================================="
echo " ANALYSING NOW PROTEIN-TRIMER 1QU9 DOCKING TEST"
echo "=========================================================="
cd protein-trimer
cat /dev/null >diff.out
diff run1/structures/it0/file.list refe/run1/structures/it0/file.list >> diff.out
diff run1/structures/it1/file.list refe/run1/structures/it1/file.list >> diff.out
diff run1/structures/it1/water/file.list refe/run1/structures/it1/water/file.list >> diff.out
diff run1/structures/it0/i-RMSD.dat refe/run1/structures/it0/i-RMSD.dat >> diff.out
diff run1/structures/it1/i-RMSD.dat refe/run1/structures/it1/i-RMSD.dat >> diff.out
diff run1/structures/it1/water/i-RMSD.dat refe/run1/structures/it1/water/i-RMSD.dat >> diff.out
if ( `wc -l diff.out | awk '{print $1}'` == 0 ) then
  echo "  >>>> No difference - test OK"
else
  cat diff.out
endif
cd ..
echo "=========================================================="
echo " 1QU9 C3 TRIMER DOCKING TEST COMPLETED"
echo "=========================================================="
echo "=========================================================="

echo "=========================================================="
echo "=========================================================="
echo " ANALYSING NOW REFINE COMPLEX TEST"
echo "=========================================================="
cd refine-complex
cat /dev/null >diff.out
diff run1/structures/it0/file.list refe/run1/structures/it0/file.list >> diff.out
diff run1/structures/it1/file.list refe/run1/structures/it1/file.list >> diff.out
diff run1/structures/it1/water/file.list refe/run1/structures/it1/water/file.list >> diff.out
diff run1/structures/it0/i-RMSD.dat refe/run1/structures/it0/i-RMSD.dat >> diff.out
diff run1/structures/it1/i-RMSD.dat refe/run1/structures/it1/i-RMSD.dat >> diff.out
diff run1/structures/it1/water/i-RMSD.dat refe/run1/structures/it1/water/i-RMSD.dat >> diff.out
if ( `wc -l diff.out | awk '{print $1}'` == 0 ) then
  echo "  >>>> No difference - test OK"
else
  cat diff.out
endif
cd ..
echo "=========================================================="
echo " REFINE COMPLEX TEST COMPLETED"
echo "=========================================================="
echo "=========================================================="

echo "=========================================================="
echo "=========================================================="
echo " ANALYSING NOW REFINE/EXPAND COMPLEX TEST"
echo "=========================================================="
cd refine-expand-complex
cat /dev/null >diff.out
diff run1/structures/it0/file.list refe/run1/structures/it0/file.list >> diff.out
diff run1/structures/it1/file.list refe/run1/structures/it1/file.list >> diff.out
diff run1/structures/it1/water/file.list refe/run1/structures/it1/water/file.list >> diff.out
diff run1/structures/it0/i-RMSD.dat refe/run1/structures/it0/i-RMSD.dat >> diff.out
diff run1/structures/it1/i-RMSD.dat refe/run1/structures/it1/i-RMSD.dat >> diff.out
diff run1/structures/it1/water/i-RMSD.dat refe/run1/structures/it1/water/i-RMSD.dat >> diff.out
if ( `wc -l diff.out | awk '{print $1}'` == 0 ) then
  echo "  >>>> No difference - test OK"
else
  cat diff.out
endif
cd ..
echo "=========================================================="
echo " REFINE/EXPAND COMPLEX TEST COMPLETED"
echo "=========================================================="
echo "=========================================================="

echo "=========================================================="
echo "=========================================================="
echo " ANALYSING NOW SCORING TEST"
echo "=========================================================="
cd scoring
cat /dev/null >diff.out
diff file.list refe/file.list >> diff.out
if ( `wc -l diff.out | awk '{print $1}'` == 0 ) then
  echo "  >>>> No difference - test OK"
else
  cat diff.out
endif
cd ..
echo "=========================================================="
echo " SCORING TEST COMPLETED"
echo "=========================================================="
echo "=========================================================="

echo "=========================================================="
echo "=========================================================="
echo " ANALYSING NOW SHAPE DOCKING TEST"
echo "=========================================================="
cd shape-docking
cat /dev/null >diff.out
diff run1/structures/it0/file.list refe/run1/structures/it0/file.list >> diff.out
diff run1/structures/it1/file.list refe/run1/structures/it1/file.list >> diff.out
diff run1/structures/it1/water/file.list refe/run1/structures/it1/water/file.list >> diff.out
diff run1/structures/it0/i-RMSD.dat refe/run1/structures/it0/i-RMSD.dat >> diff.out
diff run1/structures/it1/i-RMSD.dat refe/run1/structures/it1/i-RMSD.dat >> diff.out
diff run1/structures/it1/water/i-RMSD.dat refe/run1/structures/it1/water/i-RMSD.dat >> diff.out
if ( `wc -l diff.out | awk '{print $1}'` == 0 ) then
  echo "  >>>> No difference - test OK"
else
  cat diff.out
endif
cd ..
echo "=========================================================="
echo " SHAPE DOCKING TEST COMPLETED"
echo "=========================================================="
echo "=========================================================="

echo "=========================================================="
echo "=========================================================="
echo " ANALYSING NOW BARNASE-BARSTAR SOLVATED DOCKING TEST"
echo "=========================================================="
cd solvated-docking
cat /dev/null >diff.out
diff run1/structures/it0/file.list refe/run1/structures/it0/file.list >> diff.out
diff run1/structures/it1/file.list refe/run1/structures/it1/file.list >> diff.out
diff run1/structures/it1/water/file.list refe/run1/structures/it1/water/file.list >> diff.out
diff run1/structures/it0/i-RMSD.dat refe/run1/structures/it0/i-RMSD.dat >> diff.out
diff run1/structures/it1/i-RMSD.dat refe/run1/structures/it1/i-RMSD.dat >> diff.out
diff run1/structures/it1/water/i-RMSD.dat refe/run1/structures/it1/water/i-RMSD.dat >> diff.out
set numwatrefe=`grep WAT refe/run1/structures/it0/solvated-docking_1_water.pdbw | wc -l |awk '{print $1}'`
set numwat=`grep WAT run1/structures/it0/solvated-docking_1_water.pdbw | wc -l |awk '{print $1}'`
if ($numwat == 0) echo "NO WATERS DETECTED! POSSIBLE PROBLEM" >> diff.out
if ($numwat != $numwatrefe) echo "Different number of waters detected: "$numwatrefe" for refe, "$numwat" for test run" >> diff.out
if ( `wc -l diff.out | awk '{print $1}'` == 0 ) then
  echo "  >>>> No difference - test OK"
else
  cat diff.out
endif
cd ..
echo "=========================================================="
echo " BARNASE-BARSTAR SOLVATED DOCKING TEST COMPLETED"
echo "=========================================================="
echo "=========================================================="
