This directory contains the HADDOCK test suite for developers.
Before testing any changes to the HADDOCK software and protocols,
make sure to run first the HADDOCK-setup-test.csh script to define the reference runs

Then run the test suite with HADDOCK-run-all-tests.csh and check the resulting diff file (HADDOCK-tests.diff).
Some differences are expected (e.g. date, timing,...). Any other differences should be checked carefully.

```
clustering
cyclic-ace-cys-link
cyclic-peptide
d-amino-acid
glycans
nucleosome
nucleosome-CG
protein-dna
protein-dna-CG
protein-dummy
protein-ligand
protein-ligand-shape
protein-peptide
protein-peptide-ensemble
protein-protein
protein-protein-dani
protein-protein-em
protein-protein-nowat
protein-protein-pcs
protein-protein-rdc
protein-refine-pcs
protein-tetramer-CG
protein-trimer
refine-complex
refine-expand-complex
rotate-it1
scoring
shape-docking
solvated-docking
zinc-finger
```

Check `HADDOCK-tests.diff` or run [pytest](https://docs.pytest.org/en/latest/getting-started.html) (make sure all cases are covered).
***

## Testing HADDOCK with Containers
Please refer to the virtualization repository
