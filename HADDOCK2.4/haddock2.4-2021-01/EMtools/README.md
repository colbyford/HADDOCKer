EMtools
=======


About
-----

This folder contains simple Python scripts to help setup a HADDOCK-EM run. It
contains the following tools:

* *centroid_from_structure.py*: Calculate the center of a PDB-structure. It
outputs the centroid coordinate, and a file `centroid.bld` that can be opened
with UCSF Chimera to visualize the centroid.

* *em2xplor.py*: Transform the cryo-EM density from CCP4 or MRC format to
XPLOR/CNS format. In the process it might also extend the number of voxels in
each direction to be a multiple of 2, 3 and 5, to be consistent with the fast
Fourier transform in CNS.


All tools have a `-h` or `--help` flag to display the required arguments and
give a small description.
