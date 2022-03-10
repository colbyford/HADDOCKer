#!/bin/csh
echo "=========================================================="
echo "=========================================================="
echo " CHECKING NOW PROTEIN-DNA EXAMPLE"
echo "=========================================================="
echo "=========================================================="
./results-stats.csh protein-dna/run1*/
echo "=========================================================="
echo "=========================================================="
echo " CHECKING NOW THE NEURAMINIDASE PROTEIN-LIGAND DOCKING EXAMPLE"
echo "=========================================================="
echo "=========================================================="
./results-stats-ligand.csh protein-ligand/run1*/
echo "=========================================================="
echo "=========================================================="
echo " CHECKING NOW THE SHAPE-BASED DOCKING PROTEIN-LIGAND EXAMPLE"
echo "=========================================================="
echo "=========================================================="
./results-stats-ligand.csh protein-ligand-shape/run1*/
echo "=========================================================="
echo "=========================================================="
echo " CHECKING NOW PROTEIN-PEPTIDE DOCKING EXAMPLE"
echo "=========================================================="
echo "=========================================================="
./results-stats.csh protein-peptide/run1*/ 
echo "=========================================================="
echo "=========================================================="
echo " CHECKING NOW E2A-HPR PROTEIN-PROTEIN DOCKING EXAMPLE"
echo "=========================================================="
echo "=========================================================="
./results-stats.csh protein-protein/run1*/ 
echo "=========================================================="
echo "=========================================================="
echo " CHECKING NOW PROTEIN-PROTEIN-EM DOCKING EXAMPLE"
echo "=========================================================="
echo "=========================================================="
./results-stats.csh protein-protein-em/run1*/ 
echo "=========================================================="
echo "=========================================================="
echo "=========================================================="
echo " CHECKING NOW E2A-HPR PROTEIN-PROTEIN-DANI DOCKING EXAMPLE"
echo "=========================================================="
echo "=========================================================="
./results-stats.csh protein-protein-dani/run1*/ 
echo "=========================================================="
echo "=========================================================="
echo " CHECKING NOW PROTEIN-PROTEIN-PCS EPS-HOT DOCKING EXAMPLE"
echo "=========================================================="
echo "=========================================================="
./results-stats.csh protein-protein-pcs/run1*/ 
echo "=========================================================="
echo "=========================================================="
echo " CHECKING NOW PROTEIN-PROTEIN-RDC DOCKING EXAMPLE"
echo "=========================================================="
echo "=========================================================="
./results-stats.csh protein-protein-rdc/run1*/ 
echo "=========================================================="
echo "=========================================================="
echo " CHECKING NOW PROTEIN-TRIMER 1QU9 C3-SYMM DOCKING EXAMPLE"
echo "=========================================================="
echo "=========================================================="
./results-stats.csh protein-trimer/run1*/
echo "=========================================================="
echo "=========================================================="
echo " CHECKING NOW PROTEIN-TETRAMER COARSE GRAINED DOCKING EXAMPLE"
echo "=========================================================="
echo "=========================================================="
./results-stats.csh protein-tetramer-CG/run1*/
echo "=========================================================="
echo "=========================================================="
echo " CHECKING NOW BARNASE-BARSTAR SOLVATED DOCKING EXAMPLE"
echo "=========================================================="
echo "=========================================================="
./results-stats.csh solvated-docking/run1*/
echo "=========================================================="
echo "=========================================================="
echo "=========================================================="
echo " CHECKING NOW COMPLEX REFINEMENT EXAMPLE"
echo "=========================================================="
echo "=========================================================="
./results-stats.csh refine-complex/run1*/
echo "=========================================================="
echo "=========================================================="
