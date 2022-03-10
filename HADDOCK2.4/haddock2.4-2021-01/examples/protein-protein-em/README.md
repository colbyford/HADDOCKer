Protein-protein docking with EM-data
====================================


Overview
--------

This example explains most of the steps required for a successful HADDOCK run
using cryo-EM data. The two proteins that will be docked are part of a ribosome
crystal structure (PDB-ID: 2YKR), for which also a 9.8Å resolution cryo-EM map
was available (EMDB-ID: 1884). Even though the problem here is artificial, it
does address all practical points and issues for performing a HADDOCK run with
cryo-EM data.

HADDOCK requires as input the density map in XPLOR format, where the number of
voxels in each dimension should be a multiple of 2, 3 and 5. Since the standard
format for the EMDB is CCP4, we provide a tool for the conversion that also
respects the size restraint.

HADDOCK also requires as input, in addition to the density map, so-called
centroids, coordinates that represent the approximate center of mass position
of each chain. This document describes all steps and tools used for preparing
the input data, though it assumes the PDB files are already properly processed.


Preparing the input data
-----------------------

The HADDOCK-EM protocol works significantly faster if the the cryo-EM map is as
small as possible. Thus, the first step should be to extract the part of the
map that you are interested in. This can be easily done with [UCSF
Chimera][link-chimera], where the map can be cropped to the region of interest.
See [here][link-crop1] and [here][link-crop2] to see how. Save the cropped
region of interest to file.

To be compliant with HADDOCK the cropped cryo-EM data should be converted to
XPLOR format. We ship the `em2xplor.py` Python tool for this, located in the
'EMtools' directory in the HADDOCK distribution. The tool can be used in a
terminal simple as

    python em2xplor.py <input-map> <output-map>

where `<input-map>` is the original map, and `<out-map>` the name of the
resulting XPLOR file. The XPLOR map is ultimately the input density to run
HADDOCK-EM. This covers the first part of preparing the input data.

The next step is to determine the centroids, the coordinates of the approximate
center of mass of each subunit in the density. There are many approaches to
determine these, but the two methods we discuss each have at its core an
initial rigid body fitting of subunits in the density, where the precise
orientation is unimportant. The first is through manual fitting again using
UCSF Chimera. After the manual placement of the subunit to its approximate
position, save the structure to file File -> Save PDB ..., but tag the box
`Save relative to model:` and pick the cryo-EM data as the relative model.
The centroid of the chain can then be determined using the
`centroid-from-structure.py` EMtools script

    python centroid-from-structure.py <PDB-file>

This will print the x, y and z coordinate of the center of the structure, and
create a [BILD file][link-bild-format] `centroid.bld` that can be opened with
UCSF Chimera to visualize the centroid.

Another method is via automatic rigid body fitting using
[PowerFit][link-powerfit]. After installing PowerFit, the command line tool
`powerfit` should be at your disposal. Perform an automatic rigid body fitting
by the command

    powerfit <PDB-file> <cryo-EM map> <resolution> -l -d results

The fitting might take awhile depending on the size of the density map.
Ultimately PowerFit will print out the results in the `results` directory. Open
the file `solutions.out` here, with a simple text editor. It shows the best
fits that were found during the search ordered by their rank through the
cross-correlation coefficient, together with the position of the center of mass
of each subunit, and the corresponding rotation matrix elements. Thus the
centroids can be extracted by looking at column 3 to 5, which represent the z,
y and x coordinate, respectively.


Setting up a docking run
------------------------

After the cryo-EM data has been cropped and converted in the correct format,
and the centroids have been determined, a docking run can be set up just as
usual. The only extra keyword that is required in the `new.html` file is
`CRYO-EM_FILE`, that should point to the location of the XPLOR density file.
After that a new docking run can be setup using the regular `haddock` command.


Performing the docking
----------------------

Now that the docking run has been created, some parameters in the `run.cns`
file need to be adjusted in order to properly run HADDOCK-EM. Go to the
`Cryo-EM parameters` section, and set the parameter `centroid_rest` to `true`.
This will turn on the option to use centroid-based distance restraints. Below
that the centroids themselves need to be defined, where `xcom_N`, `ycom_N` and
`zcom_N` are the x, y and z coordinate of the centroid, respectively. Set those
coordinates to the values found as described in the *Preparing the input* data
section. In case you are docking with more than 2 chains, add another set of
centroid restraints to the list manually up to the total number of chains you
are docking, e.g. `xcom_3`, `ycom_3`, `zcom_3`, `xcom_4`, etc. After defining
the centroids, they can be set to either ambiguous or unambiguous using the
`ambi_N` parameters. In case of the default unambiguous restraints, distance
restrains will be created between the center of chain 1 (or A) and centroid
1, and between the center of chain 2 (or B) and centroid 2, etc. Conversely, in
case of in case of ambiguous distance restraints, distance restraints will be
created between the center of each chain and all the other centroids. The use
of ambiguous restraints is required in docking cases where also symmetry
restraints are used, but they are also useful when it is not known which
centroid corresponds to which chain.

Besides setting the centroids, also the density based restraints need to be
activated by setting `em_rest` to `true`. This allows the use of
energy minimzation directly against the density at each docking stage. The
`em_kscale` parameter is the force constant used for the density based
restraints during the docking and the default value of `15000` should be fine.
The three parameters `em_it0`, `em_it1`, and `em_itw` gives control over when
to use the density based restraints, which are all set to `true` by default.
The last parameter that needs to be set is the `em_resolution` parameter, which
represents the resolution of the cryo-EM data in angstrom. The remaining
parameters `nx`, `ny`, `nz` represent number of voxels in the x, y and z
direction, while `xlength`, `ylength` and `zlength` gives the dimensions of the
cryo-EM density. These six parameters are set automatically and should not be
changed. The last 3 parameters `w_lcc_0`, `w_lcc_1` and `w_lcc_2` are the
weights of the local cross-correlation score in the HADDOCK-EM score; the
default values here should be sufficient for most cases. 

Now that all parameters have been set to their proper values for HADDOCK-EM,
the docking can start as usual by typing `haddock` in the terminal where the
`run.cns` file resides.


Inspecting the results
----------------------

The analysis of the results is similar to a regular HADDOCK run. The fit of a
particular solution can be straightforwardly opened with UCSF Chimera and the
density simultaneous, since the docking has been performed in the coordinate
frame of the cryo-EM data. In addition, the influence and fit of the
centroid-based restraints can be appreciated by also opening the `centroid.bld`
file of each chain to visualize the position of the centroid.


[link-chimera]: https://https://www.cgl.ucsf.edu/chimera/ "UCSF Chimera"
[link-crop1]: http://plato.cgl.ucsf.edu/pipermail/chimera-users/2015-June/011162.html
[link-crop2]: http://www.cgl.ucsf.edu/chimera/data/tutorials/volumetour/volumetour.html
[link-bild-format]: https://www.cgl.ucsf.edu/chimera/docs/UsersGuide/bild.html
[link-powerfit]: https://github.com/haddocking/powerfit "PowerFit"
