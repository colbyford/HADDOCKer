# HADDOCKer
Docker image for the running the HADDOCK system for predicting the structure of biomolecular complexes.

<h3 align="right">Colby T. Ford, Ph.D.</h3>

## Build Instructions
1. Clone this repository to your local machine

2. Open terminal and navigate to the directory of this repository.

3. Run the following command. This will generate the Docker image.
```
docker build -t haddock2_4 .
```

4. Once the container is ready, remote into the tcsh terminal.
```
docker run --name haddock2_4 -d haddock2_4
docker run -v T:\haddock_tests:/data --name haddock2_4 -d haddock2_4
docker exec -it haddock2_4 /bin/tcsh
```

## Usage
```sh
cd $HOME/haddock/haddock2.4-2021-01/
# source haddock_configure.csh

cd examples/protein-protein

# haddock2.4 run.cns
# cd run1
# haddock2.4 run.param

./run-example.csh

## Find the best PDB based on HADDOCK Score
cluster_haddock-score.txt_best4
file.nam_clust1_haddock-score
nano protein-protein_3.pdb
```

-------------------------------------------

## Licensing

This container image includes software libraries that each require a license. Please fill out the following license request forms before using this software:
- HADDOCK 2.4: https://www.bonvinlab.org/software/haddock2.4/download
- CNSsolve 1.3: http://cns-online.org/v1.3/

## Citations

HADDOCK:
- Cyril Dominguez, Rolf Boelens and Alexandre M.J.J. Bonvin. HADDOCK: a protein-protein docking approach based on biochemical and/or biophysical information. J. Am. Chem. Soc. 125, 1731-1737 (2003).
- G.C.P van Zundert, J.P.G.L.M. Rodrigues, M. Trellet, C. Schmitz, P.L. Kastritis, E. Karaca, A.S.J. Melquiond, M. van Dijk, S.J. de Vries and A.M.J.J. Bonvin. "The HADDOCK2.2 webserver: User-friendly integrative modeling of biomolecular complexes." J. Mol. Biol., 428, 720-725 (2016).

CNSsolve:
- A.T. Brunger, P.D. Adams, G.M. Clore, P.Gros, R.W. Grosse-Kunstleve, J.-S. Jiang, J. Kuszewski, N. Nilges, N.S. Pannu, R.J. Read, L.M. Rice, T. Simonson, G.L. Warren,Crystallography & NMR System (CNS), A new software suite for macromolecular structure determination, Acta Cryst.D54, 905-921(1998).
- A.T. Brunger, Version 1.2 of the Crystallography and NMR System, Nature Protocols 2, 2728-2733 (2007).
