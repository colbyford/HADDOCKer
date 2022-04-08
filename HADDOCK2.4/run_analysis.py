from distutils.archive_util import make_archive
import os
from helper_scripts.make_run_params import write_run_params

## Point to PDB files and Active Residue info
ligand_pdb = "file.pdb"
ligand_active_res = "file.pdb"
receptor_pdb = "file.list"
receptor_active_res = "file.list"
residue_file = "file.tbl"

## Make active/passive residue file
os.system(f"python3 active-passive-to-ambig.py {ligand_active_res} {receptor_active_res} > {residue_file}")

## Make `run.param` file
write_run_params(ambig_tbl = residue_file,
                 haddock_dir = "/root/haddock/haddock2.4-2021-01/",
                 n_comp = 2,
                 pdb_file_1 = ligand_pdb,
                 pdb_file_2 = receptor_pdb,
                 project_dir = "./",
                 prot_segid_1 = "A",
                 prot_segid_2 = "B",
                 run_number = 1,
                 output_file = "run.param")

## Get `haddock2.4` command
os.system("source $HOME/haddock/haddock2.4-2021-01/haddock_configure.csh")

## Set up run
os.system("haddock2.4 run.param")
# os.system("cd run1")
os.chdir('./run1')

## Run experiment
os.system("haddock2.4 run.cns")

## Perform analysis of results
# os.system("cd ..")
os.chdir('../')
os.system("./ana_scripts/run_all.csh run1")