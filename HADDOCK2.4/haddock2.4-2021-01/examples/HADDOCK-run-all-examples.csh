#!/bin/csh
source ../haddock_configure.csh
\rm -rf */run1 
date >HADDOCK-examples.out
cd ./protein-dna
./run-example.csh >>../HADDOCK-examples.out
cd ..
date >>HADDOCK-examples.out
cd ./protein-ligand
./run-example.csh >>../HADDOCK-examples.out
cd ..
date >>HADDOCK-examples.out
cd ./protein-ligand-shape
./run-example.csh >>../HADDOCK-examples.out
cd ..
date >>HADDOCK-examples.out
cd ./protein-peptide
./run-example.csh >>../HADDOCK-examples.out
cd ..
date >>HADDOCK-examples.out
cd ./protein-protein
./run-example.csh >>../HADDOCK-examples.out
cd ..
date >>HADDOCK-examples.out
cd ./protein-protein-dani
./run-example.csh >>../HADDOCK-examples.out
cd ..
date >>HADDOCK-examples.out
cd ./protein-protein-em
./run-example.csh >>../HADDOCK-examples.out
cd ..
date >>HADDOCK-examples.out
cd ./protein-protein-pcs
./run-example.csh >>../HADDOCK-examples.out
cd ..
date >>HADDOCK-examples.out
cd ./protein-protein-rdc
./run-example.csh >>../HADDOCK-examples.out
cd ..
date >>HADDOCK-examples.out
cd ./protein-trimer
./run-example.csh >>../HADDOCK-examples.out
cd ..
date >>HADDOCK-examples.out
cd ./protein-tetramer-CG
./run-example.csh >>../HADDOCK-examples.out
cd ..
date >>HADDOCK-examples.out
cd ./refine-complex
./run-example.csh >>../HADDOCK-examples.out
cd ..
date >>HADDOCK-examples.out
cd ./solvated-docking
./run-example.csh >>../HADDOCK-examples.out
cd ..
date >>HADDOCK-examples.out
cd ./protein-peptide-ensemble
./run-example.csh >>../HADDOCK-examples.out
cd ..
date >>HADDOCK-examples.out
cd ./protein-refine-pcs
./run-example.csh >>../HADDOCK-examples.out
cd ..
date >>HADDOCK-examples.out