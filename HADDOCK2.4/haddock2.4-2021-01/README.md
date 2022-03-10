HADDOCK
=======

**High Ambiguity Driven biomolecular DOCKing**  
*based on biochemical and/or biophysical information.*  

*Version*: 2.4 (September, 2020)  
*Authors*: Alexandre Bonvin, Utrecht University  

Bijvoet Center for Biomolecular Research  
Padualaan 8, 3584 CH Utrecht, the Netherlands  
Email: a.m.j.j.bonvin@uu.nl  
Phone: +31-30-2533859  
Fax: +31-30-2537623  

------------------------------------------------------------------------
HADDOCK online: https://wenmr.science.uu.nl/haddock2.4

HADDOCK manual: https://bonvinlab.org/software/haddock2.4

HADDOCK forum: https://ask.bioexcel.eu

------------------------------------------------------------------------

When using HADDOCK cite:

* Cyril Dominguez, Rolf Boelens and Alexandre M.J.J. Bonvin.  
  HADDOCK: a protein-protein docking approach based on biochemical and/or biophysical information.  
  *J. Am. Chem. Soc.* **125**, 1731-1737 (2003).

* S.J. de Vries, A.D.J. van Dijk, M. Krzeminski, M. van Dijk, A. Thureau, V.
  Hsu, T. Wassenaar and A.M.J.J. Bonvin.  
  HADDOCK versus HADDOCK: New features and performance of HADDOCK2.0 on the
  CAPRI targets.   
  *Proteins: Struc. Funct. & Bioinformatic* **69**, 726-733 (2007).

and, if used, cite in addition any publication related to the use of RDCs,
diffusion anisotropy data, protein-DNA docking and/or solvated docking (see
below).

The use of residual dipolar couplings in HADDOCK is described in:

* A.D.J. van Dijk, D. Fushman and A.M.J.J. Bonvin.  
  Various strategies of using residual dipolar couplings in NMR-driven protein
  docking: Application to Lys48-linked di-ubiquitin and validation against
  15N-relaxation data.  
  *Proteins: Struc. Funct. & Bioinformatics* **60**, 367-381 (2005).

The use of diffusion anisotropy data in HADDOCK is described in:

* A.D.J. van Dijk, R. Kaptein, R. Boelens and A.M.J.J. Bonvin.  
  Combining NMR relaxation with chemical shift perturbation data to drive
  protein-protein docking.  
  *J. Biomol. NMR* **34**, 237-244 (2006). 

Solvated docking using HADDOCK is described in:

* A.D.J. van Dijk and A.M.J.J. Bonvin.  
  Solvated docking: introducing water into the modelling of biomolecular
  complexes.  
  *Bioinformatics* **22** 2340-2347 (2006). 

Flexible protein-DNA docking using HADDOCK is described in:

* M. van Dijk, A.D.J. van Dijk, V. Hsu, R. Boelens and A.M.J.J. Bonvin.  
  Information-driven Protein-DNA Docking using HADDOCK: it is a matter of
  flexibility.  
  *Nucl. Acids Res.* **34** 3317-3325 (2006). 

The use of cryo-electron microscopy data in HADDOCK is described in:

* G.C.P. van Zundert, A.S.J. Melquiond and A.M.J.J. Bonvin.  
  Integrative modeling of biomolecular complexes: HADDOCKing with Cryo-EM data.  
  *Structure* **23**, 949-960 (2015).

The following review on data-driven docking is freely available for
download:

* Aalt D.J. van Dijk, Rolf Boelens and Alexandre M.J.J. Bonvin.  
  Data-driven docking for the study of biomolecular complexes.  
  *FEBS Journal* **272**, 293-312 (2005).


------------------------------------------------------------------------

Introduction
------------

HADDOCK (High Ambiguity Driven biomolecular DOCKing) is an information-driven flexible docking approach for the modelling of biomolecular complexes (Dominguez et al. 2003). Docking is defined as the modelling of the structure of a complex based on the known three-dimensional structures of its constituents. HADDOCK distinguishes itself from other docking methods by incorporating a wide variety of experimental and/or bioinformatics data to drive the modelling (Melquiond and Bonvin, 2010). This allows concentrating the search to relevant portions of the interaction space using a more sophisticated treatment of conformational flexibility.  

Interface regions can be identified by mutagenesis, H/D exchange and chemical modifications (e.g. by cross-linkers or oxidative agents) detected by mass spectrometry, nuclear magnetic resonance, chemical shift perturbations and cross-saturation transfer. When experimental data are unavailable or scarce, this information can be supplemented by bioinformatics predictions (de Vries and Bonvin, 2008). These diverse information sources typically only identify or predict interfacial regions, but do not define the contacts across an interface. HADDOCK deals with this by implementing them as ambiguous interaction restraints (AIRs) that will force the interfaces to come together without imposing a particular orientation.  

HADDOCK can also incorporate classical NMR restraints such as distances from nuclear Overhauser effects and paramagnetic relaxation enhancement measurements, pseudo-contact shift, dihedral angles, residual dipolar coupling and diffusion anisotropy restraints, the latter two providing valuable information about the relative orientation of the components in a complex. Any kind of experimental data providing distances can be incorporated as restraints. A good example are cross-linking data from mass spectrometry. In addition, symmetry restraints can be defined in the case of symmetrical homomeric systems. Other valuable information can be obtained from low-to-medium resolution techniques such as small angle X-ray scattering, cryo-electron microscopy and ion mobility mass spectrometry that can provide valuable information about the shape of a complex. The 2.4 version of HADDOCK also support cryo-EM data.

The docking protocol in HADDOCK, which makes use of the Crystallography and NMR System (CNS) package as computational engine, consists of three successive steps:

*   rigid-body energy minimization
*   semi-flexible refinement in torsion angle space
*   final refinement (in explicit solvent - optional).

By allowing for explicit flexibility during the molecular dynamics refinement HADDOCK can account for small conformational changes occurring upon binding. Larger and more challenging conformational changes can be dealt with by starting the docking from ensembles of conformations and/or treating the molecules as a collection of domains. The latter approach makes use of the unique multi-body docking ability of HADDOCK, which can handle up to 20 separate domains or molecules at the same time. The selection of the final models is based on a weighted sum of electrostatics, desolvation and van der Waals energy terms, along with the energetic contribution of the restraints used to drive the docking. HADDOCK has been extensively applied to a large variety of systems, including protein-protein, protein-nucleic acids and protein-small molecule docking and has shown a very strong performance in the blind critical assessment of the prediction of interactions (CAPRI). A considerable number of experimental structures of complexes calculated using HADDOCK have been deposited into the Protein Data Bank (PDB). HADDOCK is available as a web server ([https://wenmr.science.uu.nl/haddock2.4](https://wenmr.science.uu.nl/haddock2.4){:target="_blank"}) (de Vries et al. 2010) offering a user-friendly interface to the structural biology community.  


------------------------------------------------------------------------

HADDOCK consists of [Python][link-python] scripts derived from
[ARIA][link-aria] written by Michael Nilges and Jens Linge and makes use of
[CNS][link-cns] as structure calculation software. Additional scripts (csh,
awk, perl) and/or (third party) software are also used to either prepare the
data for HADDOCK or analyze the results (see software links). On our HADDOCK
home page [https://bonvinlab.org/software/haddock2.4](https://bonvinlab.org/software/haddock2.4]) you will find:

* general information on HADDOCK
* tools to generate AIR restraint files and to setup projects
* instructions to obtain HADDOCK
* links to the various softwares required to run HADDOCK
* a manual describing the use of HADDOCK
* a frequently asked questions section
* various tutorials 

------------------------------------------------------------------------


Acknowledgments
----------------

HADDOCK is derived from [ARIA][link-aria] scripts by Michael
Nilges and Jens Linge.

* J.P. Linge, M. Habeck, W. Rieping and M. Nilges (2003).  
  ARIA: automated NOE assignment and NMR structure calculation.  
  *Bioinformatics* **19**, 315-316.

The ongoing development of HADDOCK is the result of a team effort and in
particular contributions from Cyril Dominguez, Aalt-Jan van Dijk, Sjoerd de
Vries and Marc van Dijk are acknowledged.

------------------------------------------------------------------------

Please send any suggestions or enquiries to Alexandre Bonvin

------------------------------------------------------------------------

[link-capri]: https://capri.ebi.ac.uk
[link-python]: https://www.python.org 
[link-aria]: https://aria.pasteur.fr 
[link-cns]: http://cns-online.org/v1.3/
