This directory contains customized scoring script.

To run scoring, only copy the scoring.inp script into the directory where your PDB files reside.

The scoring.inp script assumes that a file listing all PDBs to be scored is present.
This file is named `filelist.list` and contains the full path to the PDB files to be scored. 
These should be defined between double quotes.

Different number of chains, types of molecules can be mixed.

What the `scoring.inp` script does is for each input PDB:

    1) Create a specific topology file (psf)
    2) Build all missing atoms
    3) Performs 50 steps of EM
    4) Output PBD files (`<original-name>_conv.pdb`) containing the usual HADDOCK header with the components of the score

If a topology file is already present for a given PDB file, this file will be skipped.
