# CGtools

Please refer to the HADDOCK2.4 manual for a complete descriptions of parameters and protocols at https://www.bonvinlab.org/software/haddock2.4/manual and in particular https://www.bonvinlab.org/software/haddock2.4/pdb-cg/

This set of scripts are used in the local version of HADDOCK to convert all-atom PDB structures to a compatible 
coarse-grain.

## Requirements:
* Python 2.7.x
* BioPython 1.72 or newer

## Usage
`$ python aa2cg.py e2a_1F3G.pdb`

This will generate the files `e2a_1F3G_cg.pdb` and `e2a_1F3G_cg_to_aa.tbl`. The `.tbl` file contains restraints 
which will be used internally during the cg2aa protocol. 

Note that the PDB to be converted must have a chainID and it must match the `PROT_SEGID` of your `run.param`. Adding or changing ChainID can be done with `pdb-tools`, available locally or via webserver at https://bianca.science.uu.nl/pdbtools

## Setup CG run

Example `protein-tetramer-CG`

* Prepare CG PDBs
```bash
$ python aa2cg_v2-2.py chainA.pdb
$ python aa2cg_v2-2.py chainB.pdb
$ python aa2cg_v2-2.py chainC.pdb
$ python aa2cg_v2-2.py chainD.pdb
$ cat chainA_cg_to_aa.tbl chainB_cg_to_aa.tbl chainC_cg_to_aa.tbl chainD_cg_to_aa.tbl > cg-to-aa.tbl
``` 

* Create `run.param`

```
CGTOAA_TBL=./cg-to-aa.tbl
N_COMP=4
PDB_FILE1=./chainA.pdb
PDB_FILE2=./chainB.pdb
PDB_FILE3=./chainC.pdb
PDB_FILE4=./chainD.pdb
CGPDB_FILE1=./chainA_cg.pdb
CGPDB_FILE2=./chainB_cg.pdb
CGPDB_FILE3=./chainC_cg.pdb
CGPDB_FILE4=./chainD_cg.pdb
PROJECT_DIR=./
PROT_SEGID_1=A
PROT_SEGID_2=B
PROT_SEGID_3=C
PROT_SEGID_4=D
RUN_NUMBER=1
HADDOCK_DIR=../../
```

***

Example `protein-dna-CG`

* Prepare CG PDBs
```bash
$ python aa2cg.py 1RZR_unbound-protA-1.pdb
$ python aa2cg.py 1RZR_unbound-protB-1.pdb
$ python aa2cg.py DNA_unbound.pdb
```

* Create `run.param`
```
CGTOAA_TBL=./cg2aa.tbl
HADDOCK_DIR=../../
N_COMP=3
PDB_FILE1=./1RXR_unbound-protA-1.pdb
PDB_FILE2=./1RXR_unbound-protB-1.pdb
PDB_FILE3=./DNA_unbound.pdb
CGPDB_FILE1=./1RXR_unbound-protA-1_cg.pdb
CGPDB_FILE2=./1RXR_unbound-protB-1_cg.pdb
CGPDB_FILE3=./DNA_unbound_cg.pdb
PROT_SEGID_1=A
PROT_SEGID_2=B
PROT_SEGID_3=C
RUN_NUMBER=1
PROJECT_DIR=./
```

### Important
The machinery to convert and dock CG RNA is implement but has not been thoroughly tested.
