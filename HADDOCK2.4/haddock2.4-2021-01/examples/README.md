This directory contains various examples of docking scenarios using HADDOCK:

* _protein-dna_              : protein-DNA docking (3CRO)
* _protein-ligand_           : protein-ligand docking (Neuraminidase)
* _protein-ligand-shape_     : template-based protein-ligand docking with shape restraints (BACE_1 from D3R GC4)
* _protein-peptide-ensemble_ : example of ensemble-averaged PRE restraints docking with two copies of a peptide not seeing 
                           eachother (multiple binding modes) (sumo-daxx-simc system)
* _protein-peptide_          : protein-peptide docking from an ensemble of three peptide conformations with increased flexibility
* _protein-protein_          : protein-protein docking from an ensemble of NMR structure using CSP data (e2a-hpr)
* _protein-protein-dani_     : protein-protein docking from an ensemble of NMR structure using CSP data (e2a-hpr) 
                               and diffusion anisotropy restraints
* _protein-protein-em_       : protein-protein docking into a cryo-EM map
* _protein-protein-pcs_      : protein-protein docking using NMR PCS restraints (eps-hot_pcs system)
* _protein-protein-rdc_      : protein-protein docking using NMR RDC restraints (di-ubiquitin system)
* _protein-refine-pcs_       : example of single structure water refinement with NMR PCS restraints
* _protein-tetramer-CG_      : multi-body docking of a C4 tertramer with a coarse grained representation
* _protein-trimer_           : three body docking of a homotrimer using bioinformatic predictions (pdb1qu9)
* _refine-complex_           : refinement of a comple in water (it0 and it1 skipped)
* _solvated-docking_         : solvated protein-protein docking (barnase-barstar) using bioinformatic predictions



A number of scripts to run those examples are provided:

* _HADDOCK-clean-all.csh_         : clean all examples (will remove the run1 directories)
* _HADDOCK-run-all-examples.csh_  : run all examples (will take quite some time...)
* _HADDOCK-ana-all-examples.csh_  : rerun the analysis of all examples


A number of additional scripts are provided to extract statistics:

* _check_clusterranks.csh_     : print clustering statistics for it1 and water
* _check_runs_i-rmsd.csh_      : print interface RMSD statistics
* _check_runs_l-rmsd.csh_      : print liand RMSD statistics
* _results-stats.csh_          : print overall (both clustering and individual structures) statistics
* _results-stats-ligand.csh_   : print overall (both clustering and individual structures) statistics, but using 2A as acceptable cutoff

