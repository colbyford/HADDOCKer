"""
Uses Biopython to parse the structure and DSSP output.
Uses pieces of the martinize-1.1.py script to convert the SS types

Outputs a coarse grained pdb file (*_ss.pdb) with assigned bfactors.
Outputs a tbl file to map the beads to the atoms they represent.

Updates
 - Updated python version to 2.6 to support isdisjoint() set method in DSSP.py (JR Apr 2012)
 - Residues that DSSP can't handle (incomplete backbone f ex) treated as coil  (JR Apr 2012)
 - Update to_one_letter_code library to protein_letters_3to1 (Jorge Roel 2017)
 - Inclusion of fake beads for corresponding amino-acids <SCd> (Jorge Roel 2017)
 - Changed the mapping routine to include DNA bead types (Rodrigo Honorato 2018)
 - Implemented feature to check if nucleic acid is a candidate for hbond (Rodrigo Honorato 2018)
"""
import collections
import itertools
import math
import os
import random
import sys
import warnings
import argparse

warnings.filterwarnings("ignore")

# try:
from Bio.PDB import PDBParser
from Bio.PDB import PDBIO
from Bio.PDB.DSSP import DSSP
from Bio.PDB import Entity
#  from Bio.PDB import to_one_letter_code 
from Bio.PDB.StructureBuilder import StructureBuilder


# except ImportError, emsg:
#     sys.stderr.write('Error: %s\n' %emsg)
#     sys.stderr.write("Error loading Biopython. Make sure it's on your PYTHONPATH\n")
#     sys.exit(1)

# if os.environ.get('DSSP_X') is None:
#     sys.stderr.write('Error: DSSP not found in path ($DSSP_X)\n')
#     sys.exit(1)


def add_dummy(bead_list, dist=0.11, n=2):
    new_bead_dic = {}

    # Generate a random vector in a sphere of -1 to +1, to add to the bead position
    v = [random.random() * 2. - 1, random.random() * 2. - 1, random.random() * 2. - 1]

    # Calculated the length of the vector and divide by the final distance of the dummy bead
    norm_v = norm(v) / dist

    # Resize the vector
    vn = [i / norm_v for i in v]

    # m sets the direction of the added vector, currently only works when adding one or two beads.
    m = 1
    for j in range(n):  # create two new beads
        newName = 'SCD' + str(j + 1)  # set the name of the new bead
        new_bead_dic[newName] = [i + (m * j) for i, j in zip(bead_list[-1][1], vn)]
        m *= -2
    return new_bead_dic


def map_cg(chain):
    m_dic = collections.OrderedDict()

    for aares in chain:
        m_dic[aares] = collections.OrderedDict()

        resn = aares.resname.split()[0]  # resname
        segid = aares.segid.strip()
        resi = aares.id[1]

        # for each atom segment, calculate its center of mass and map the correct bead
        for atom_segment in cg_mapping[resn]:
            atoms = [aares[a] for a in atom_segment.split() if a in aares.child_dict]

            if atoms:
                if '*' in atom_segment:  # this is important to correctly place CG DNA beads

                    # this * means it belongs to the previous residue... find it!
                    target_previous_atom_list = [a for a in atom_segment.split() if '*' in a]
                    # print target_previous_atom_list

                    for target_atom in target_previous_atom_list:
                        # does it exist?
                        target_atom_name = target_atom.split('*')[0]
                        try:
                            previous_atom = chain[resi - 1][target_atom_name]
                            # how far away the previous atom is from this atom segment?
                            #  if it is too far away this could be the next chain...!
                            minimum_dist = min([(a - previous_atom) for a in atoms])
                            if minimum_dist < 2.0:  # 2.0 A is very permissive
                                atoms.append(previous_atom)
                        except KeyError:
                            # previous atom not found, move on
                            pass

            if not atoms:
                print('Residue %s %i of chain %s cannot be processed: missing atoms %s ' % (
                resn, resi, aares.parent.id, atom_segment))
                continue

            bead_name = cg_mapping[resn][atom_segment]

            # get center of mass
            code = list(set([a.bfactor for a in aares if a.bfactor != 0]))

            if len(code) > 1:
                print('Something is wrong with HADDOCK codes')
                exit()
            if not code:
                code = 0.0
            else:
                code = code[0]

            bead_coord = center_of_mass(atoms)

            # atom_segment = ' '.join([a for a in atom_segment.split() if not '*' in a])
            atom_segment = ' '.join([a for a in atom_segment.split()]).replace('*', '')

            # restrain for backmapping
            restrain = "assign (segid %sCG and resid %i and name %s) (segid %s and resid %i and (name %s)) 0 0 0" % (
            segid, resi, bead_name, segid, resi, ' or name '.join(atom_segment.split()))

            m_dic[aares][bead_name] = bead_coord, code, restrain

    # add dummy beads whenever its needed
    for r in m_dic:

        if r.resname in polar:
            d = 0.14  # distance
            n = 2  # number of dummy beads to be placed

        elif r.resname in charged:
            d = 0.11  # distance
            n = 1  # number of dummy beads to be placed

        else:
            continue

        # add to data structure
        # this special beads have no HADDOCK code
        bead_list = [(b, m_dic[r][b][0]) for b in m_dic[r]]
        dummy_bead_dic = add_dummy(bead_list, dist=d, n=n)
        for dB in dummy_bead_dic:
            dB_coords = dummy_bead_dic[dB]
            # code should be the same as the residue
            # code = m_dic[r][m_dic[r].keys()[0]][1]
            code = m_dic[r][list(m_dic[r])[0]][1]

            m_dic[r][dB] = (dB_coords, code, None)

    return m_dic


def center_of_mass(entity, geometric=False):
    """
    Returns gravitic [default] or geometric center of mass of an Entity.
    Geometric assumes all masses are equal (geometric=True)
    """

    # Structure, Model, Chain, Residue
    if isinstance(entity, Entity.Entity):
        atom_list = entity.get_atoms()
    # List of Atoms
    elif hasattr(entity, '__iter__') and [x for x in entity if x.level == 'A']:
        atom_list = entity
    else:  # Some other weirdo object
        raise ValueError("Center of Mass can only be calculated from the following objects:\n"
                         "Structure, Model, Chain, Residue, list of Atoms.")

    masses = []
    positions = [[], [], []]  # [ [X1, X2, ..] , [Y1, Y2, ...] , [Z1, Z2, ...] ]

    for atom in atom_list:
        masses.append(atom.mass)

        for i, coord in enumerate(atom.coord.tolist()):
            positions[i].append(coord)

    # If there is a single atom with undefined mass complain loudly.
    if 'ukn' in set(masses) and not geometric:
        raise ValueError("Some Atoms don't have an element assigned.\n"
                         "Try adding them manually or calculate the geometrical center of mass instead.")

    if geometric:
        return [sum(coord_list) / len(masses) for coord_list in positions]
    else:
        w_pos = [[], [], []]
        for atom_index, atom_mass in enumerate(masses):
            w_pos[0].append(positions[0][atom_index] * atom_mass)
            w_pos[1].append(positions[1][atom_index] * atom_mass)
            w_pos[2].append(positions[2][atom_index] * atom_mass)

        return [sum(coord_list) / sum(masses) for coord_list in w_pos]


def determine_hbonds(structure):
    nuc = ['DA', 'DC', 'DG', 'DT', 'A', 'C', 'G', 'U']
    aa = ["ALA", "CYS", "ASP", "GLU", "PHE",
          "GLY", "HIS", "ILE", "LYS", "LEU",
          "MET", "ASN", "PRO", "GLN", "ARG",
          "SER", "THR", "VAL", "TRP", "TYR"]

    pair_list = []
    for model in structure:

        dna_chain_l = []

        for chain in model:

            prot_comp = len([r for r in chain.get_residues() if r.resname.split()[0] in aa])
            dna_comp = len([r for r in chain.get_residues() if r.resname.split()[0] in nuc])

            if prot_comp:
                # protein
                pass

            if dna_comp:
                # nucleic
                dna_chain_l.append(chain)

            # if dna_comp and prot_comp:
            #     print(chain, 'is mixed nucleic/protein, not supported. split into different chains and try again')
            #     # exit()

        if len(dna_chain_l) == 1:
            print('+ WARNING: Only one DNA/RNA chain detected, is this correct?')

            chainA = dna_chain_l[0]
            reslistA = [r for r in chainA.get_residues()]

            for rA, rB in itertools.combinations(reslistA, 2):
                # print rA.id[1], rB.id[1]
                pair = identify_pairing(rA, rB)
                if pair:
                    pair_list.append(pair)
                    # print pair
                    # print len(dna_chain_l)
                    # exit()

        if len(dna_chain_l) > 1:  ## list sizes could be different, this might be improbable
            for chainA, chainB in itertools.combinations(dna_chain_l, 2):
                reslistA = [r for r in chainA.get_residues()]
                reslistB = [r for r in chainB.get_residues()]
                for rA in reslistA:
                    atomlistA = rA.child_dict.values()
                    for rB in reslistB:
                        pair = identify_pairing(rA, rB)
                        pair_list.append(pair)

    # return [p for p in pair_list if p]
    return pair_list


def identify_pairing(rA, rB):
    renumber_dic = {}
    pair = []

    # check if the pairing is correct
    rA_name = rA.resname.split()[0]
    rB_name = rB.resname.split()[0]

    try:
        atom_pair_list = pairing[rA_name, rB_name]
    except KeyError:
        # pairing not possible
        return

    # check if distances are ok
    distance_l = []

    for atom_list in atom_pair_list:

        try:
            a = rA[atom_list[0]]
            b = rB[atom_list[1]]
            distance_l.append(a - b)
        except KeyError:
            # residue does not have the necessary sidechain atoms
            #  assume its not a pair
            return

    # check P-P distances to make sure its the opposite base
    # distances for perfect DNA:
    #  opposite = 18.8A
    #  sequential = 6.6A
    #
    # 10.0A should be sufficient
    p_cutoff = 10.0

    # Basedist_cutoff = 3.5
    Basedist_cutoff = 3.5
    try:
        pA = rA.child_dict['P']
        pB = rB.child_dict['P']
        Pdistance = pA - pB
    except KeyError:
        # some base is missing its P, use the geometric center instead
        cenA = center_of_mass(rA.child_dict.values())
        cenB = center_of_mass(rB.child_dict.values())
        Pdistance = math.sqrt(sum([(a - b) ** 2 for a, b in zip(cenA, cenB)]))

    if Pdistance > p_cutoff:

        resnumA = rA.id[1]
        resnumB = rB.id[1]

        if all(e < Basedist_cutoff for e in distance_l):  # if ALL bonds are within range
            ######
            # KEEP IN MIND THAT this will not account for badly paired DNA
            ## Implement a way to search for the closest possible pair? ##
            ######
            # print rA,rB
            segidA = rA.get_segid().split()[0]
            segidB = rB.get_segid().split()[0]
            pair = (resnumA, segidA), (resnumB, segidB)

            # special atoms, mark them!
            for atom_pair in atom_pair_list:
                atomA, atomB = atom_pair

                rA[atomA].bfactor = 1
                rB[atomB].bfactor = 1
        # else:
        if resnumB == 201 and resnumA == 88:
            print(distance_l, resnumA, resnumB)

    return pair


def output_cg_restraints(pair_list):
    out = open('dna_restraints.def', 'w')
    for i, e in enumerate(pair_list):
        idx = i + 1
        resA = e[0][0]
        segidA = e[0][1]
        resB = e[1][0]
        segidB = e[1][1]
        out.write('{===>} base_a_%i=(resid %i and segid %s);\n{===>} base_b_%i=(resid %i and segid %s);\n\n' % (
        idx, resA, segidA, idx, resB, segidB))
    out.close()


def extract_groups(pair_list):
    # this will be used to define AA restraints
    out = open('dna-aa_groups.dat', 'w')
    # extract groups
    groupA = [a[0][0] for a in pair_list]
    segidA = list(set([a[0][1] for a in pair_list]))

    groupB = [a[1][0] for a in pair_list]
    segidB = list(set([a[0][1] for a in pair_list]))

    if len(segidA) != 1:
        print('Something is wrong with SEGID A')
        exit()

    if len(segidB) != 1:
        print('Something is wrong with SEGID B')
        exit()

    segidA = segidA[0]
    segidB = segidB[0]

    groupA.sort()
    groupB.sort()

    out.write('%i:%i\n%s\n%i:%i\n%s' % (groupA[0], groupA[-1], segidA, groupB[0], groupB[-1], segidB))
    out.close()


def determine_ss(structure):
    # calculate SS
    ss_dic = {}
    for model in structure:
        if args.skipss:
            continue
        else:
            try:
                dssp = DSSP(model, pdbf_path)
            except:
                # no seconday structure detected for this model
                print('+ ERROR: SS could not be assigned, check under the hood or add --skipss')
                exit()


        calculated_chains = list(set([e[0] for e in dssp.keys()]))
        # print calculated_chains

        # Get SS information and translate it:
        # DSSP > MARTINI > HADDOCK
        ## this could still be improved
        for chain in model:
            if chain.id in calculated_chains:
                # if ss_dic[model]:
                # get DSSP value for each residue
                for r in chain:
                    try:
                        r.xtra["SS_DSSP"]
                    except KeyError:
                        print("+ WARNING: No SS definition found for residue: %s %s %i" % (chain.id, r.resname, r.id[1]))
                        # pass
                        r.xtra["SS_DSSP"] = '-'
                dssp_dic = collections.OrderedDict([(r, r.xtra["SS_DSSP"]) for r in chain])
                # transform DSSP > MARTINI
                dssp_ss = ''.join(dssp_dic.values())
                # print dssp_ss
                # exit()
                _, martini_types = ssClassification(dssp_ss)  # ancestral function, keep it there

                # transform MARTINI > HADDOCK
                ## and add it to the bfactor col
                for residue, ss in zip(dssp_dic, martini_types):
                    code = ss_to_code[ss]
                    # for atom in residue.get_atoms():
                    for atom in residue.get_atom():
                        # print residue, atom, code, atom.bfactor
                        atom.bfactor = code
                        # print residue, atom, code, atom.bfactor
                        # exit()
    return structure


def rename_nucbases(structure):
    chainresdic = dict([(c.get_id(), [r.get_resname() for r in c.get_residues()]) for m in structure for c in m for r in
                        c.get_residues()])

    nucleotide_list = ['CYT', 'C', 'DC', 'THY', 'T', 'DT', 'ADE', 'A', 'DA', 'G', 'GUA', 'DG', 'U', 'URI']

    if [True for c in chainresdic for e in chainresdic[c] if e in nucleotide_list]:

        if [True for c in chainresdic for e in chainresdic[c] if e in ['U', 'URI']]:
            # CG needs 1 letter for RNA
            ref_dic = {'CYT': 'C', 'URI': 'U', 'ADE': 'A', 'GUA': 'G'}
        else:
            # CG needs 2 letters for DNA
            ref_dic = {'CYT': 'DC', 'THY': 'DT', 'ADE': 'DA', 'GUA': 'DG'}

        for model in structure:
            for chain in model:
                for r in chain.get_residues():
                    if r.resname in ref_dic.keys():
                        # rename!
                        r.resname = ref_dic[r.resname]
    else:
        # not nucleotide, nothing to renumber
        pass


# ==========================================================================================#
# ==========================================================================================#
# ==========================================================================================#

##  CODE TAKEN FROM MARTINIZE 1.1 ##
"""
Reduces complexity of protein residue to the MARTINI coarse grained model:
CA, O, Bead(s) in specific atom location.

Reference:
Monticelli et al. The MARTINI coarse-grained force field: extension to proteins. 
J. Chem. Theory Comput. (2008) vol. 4 (5) pp. 819-834

Martinize Script from Tserk Wassenaar
"""


## Please refer to it for more information  ##
## SECONDARY STRUCTURE DEFINITION  ## 

def norm(a):
    return math.sqrt(norm2(a))


def norm2(a):
    return sum([i * i for i in a])


# Function to reformat pattern strings
def pat(x, c="."):
    return x.replace(c, "\x00").split()


# Make a dictionary from two lists
def hash(x, y):
    return dict(zip(x, y))


# Split a string
def spl(x):
    return x.split()


def tt(program):
    return "".join([ssd[program].get(chr(i), "C") for i in range(256)])


# Pattern substitutions
def typesub(seq, patterns, types):
    for i, j in zip(patterns, types):
        seq = seq.replace(i, j)
    return seq


# The following function translates a string encoding the secondary structure
# to a string of corresponding Martini types, taking the origin of the 
# secondary structure into account, and replacing termini if requested.
def ssClassification(ss, program="dssp"):
    # Translate dssp/pymol/gmx ss to Martini ss
    ss = ss.translate(sstt[program])
    # Separate the different secondary structure types
    sep = dict([(i, ss.translate(sstd[i])) for i in sstd.keys()])
    # Do type substitutions based on patterns
    # If the ss type is not in the patterns lists, do not substitute
    # (use empty lists for substitutions)

    typ = [typesub(sep[i], patterns.get(i, []), pattypes.get(i, []))
           for i in sstd.keys()]
    # Translate all types to numerical values
    typ = [[ord(j) for j in list(i)] for i in typ]
    # Sum characters back to get a full typed sequence
    typ = "".join([chr(sum(i)) for i in zip(*typ)])
    # Return both the actual as well as the fully typed sequence
    return ss, typ


# ----+--------------------------------------+
## A | SECONDARY STRUCTURE TYPE DEFINITIONS |
# ----+--------------------------------------+

ss_names = {
    "F": "Collagenous Fiber",  # @#
    "E": "Extended structure (beta sheet)",  # @#
    "H": "Helix structure",  # @#
    "1": "Helix start (H-bond donor)",  # @#
    "2": "Helix end (H-bond acceptor)",  # @#
    "3": "Ambivalent helix type (short helices)",  # @#
    "T": "Turn",  # @#
    "S": "Bend",  # @#
    "C": "Coil",  # @#
    }

bbss = ss_names.keys()
bbss = spl("  F     E     H     1     2     3     T     S     C")  # SS one letter

#                                                                                           
ssdefs = {
    "dssp": list(".HGIBETSC~"),  # DSSP one letter secondary structure code     #@#
    "pymol": list(".H...S...L"),  # Pymol one letter secondary structure code    #@#
    "gmx": list(".H...ETS.C"),  # Gromacs secondary structure dump code        #@#
    "self": list("FHHHEETSCC")  # Internal CG secondary structure codes        #@#
    }
cgss = list("FHHHEETSCC")  # Corresponding CG secondary structure types   #@#

patterns = {
    "H": pat(".H. .HH. .HHH. .HHHH. .HHHHH. .HHHHHH. .HHHHHHH. .HHHH HHHH.")  # @#
    }
pattypes = {
    "H": pat(".3. .33. .333. .3333. .13332. .113322. .1113222. .1111 2222.")  # @#
    }

ss_to_code = {'C': 1,  # Free,
              'S': 2,
              'H': 3,
              '1': 4,
              '2': 5,
              '3': 6,
              'E': 7,  # Extended
              'T': 8,  # Turn
              'F': 9  # Fibril
              }

ss_eq = list("CBHHHHBTF")

# List of programs for which secondary structure definitions can be processed
programs = ssdefs.keys()

# Dictionaries mapping ss types to the CG ss types                                          
ssd = dict([(i, hash(ssdefs[i], cgss)) for i in programs])

# The translation table depends on the program used to obtain the 
# secondary structure definitions
sstt = dict([(i, tt(i)) for i in programs])

# The following translation tables are used to identify stretches of 
# a certain type of secondary structure.
null = "\x00"
sstd = dict([(i, ord(i) * null + i + (255 - ord(i)) * null) for i in cgss])

# ==========================================================================================#
# ==========================================================================================#
# ==========================================================================================#

# CG MAPPING INFORMATION

bb = "CA C N O "
prot_atoms = {"ALA": [bb + "CB"],
              "CYS": [bb, "CB SG"],
              "ASP": [bb, "CB CG OD1 OD2"],
              "GLU": [bb, "CB CG CD OE1 OE2"],
              "PHE": [bb, "CB CG CD1", "CD2 CE2", "CE1 CZ"],
              "GLY": [bb],
              "HIS": [bb, "CB CG", "CD2 NE2", "ND1 CE1"],
              "ILE": [bb, "CB CG1 CG2 CD1"],
              "LYS": [bb, "CB CG CD", "CE NZ"],
              "LEU": [bb, "CB CG CD1 CD2"],
              "MET": [bb, "CB CG SD CE"],
              "ASN": [bb, "CB CG ND1 ND2 OD1 OD2"],  # ND1?
              "PRO": [bb, "CB CG CD"],
              "GLN": [bb, "CB CG CD OE1 OE2 NE1 NE2"],
              "ARG": [bb, "CB CG CD", "NE CZ NH1 NH2"],
              "SER": [bb, "CB OG"],
              "THR": [bb, "CB OG1 CG2"],
              "VAL": [bb, "CB CG1 CG2"],
              "TRP": [bb, "CB CG CD2", "CD1 NE1 CE2", "CE3 CZ3", "CZ2 CH2"],
              "TYR": [bb, "CB CG CD1", "CD2 CE2", "CE1 CZ OH"]}

bead_names = ["BB", "SC1", "SC2", "SC3", "SC4"]

# insert beads into the data structure
cg_mapping = {}
for res in prot_atoms:
    cg_mapping[res] = collections.OrderedDict()
    for i, atom_l in enumerate(prot_atoms[res]):
        bead = bead_names[i]
        cg_mapping[res][atom_l] = bead

######################################
# Nucleotide mapping,
## This is a custom naming convetion
##  but the atom mapping is defined in
##   10.1021/acs.jctc.5b00286 -  S1
######################################

DA_beads = collections.OrderedDict()
DA_beads["O3'* P O1P O2P O5' OP1 OP2"] = "BB1"
DA_beads["C5' O4' C4'"] = "BB2"
DA_beads["C3' C2' C1'"] = "BB3"
DA_beads["N9 C4"] = "SC1"
DA_beads["C2 N3"] = "SC2"
DA_beads["C6 N6 N1"] = "SC3"
DA_beads["C8 N7 C5"] = "SC4"

DC_beads = collections.OrderedDict()
DC_beads["O3'* P O1P O2P O5' OP1 OP2"] = "BB1"
DC_beads["C5' O4' C4'"] = "BB2"
DC_beads["C3' C2' C1'"] = "BB3"
DC_beads["N1 C6"] = "SC1"
DC_beads["N3 C2 O2"] = "SC2"
DC_beads["C5 C4 N4"] = "SC3"

DG_beads = collections.OrderedDict()
DG_beads["O3'* P O1P O2P O5' OP1 OP2"] = "BB1"
DG_beads["C5' O4' C4'"] = "BB2"
DG_beads["C3' C2' C1'"] = "BB3"
DG_beads["N9 C4"] = "SC1"
DG_beads["C2 N2 N3"] = "SC2"
DG_beads["C6 O6 N1"] = "SC3"
DG_beads["C8 N7 C5"] = "SC4"

DT_beads = collections.OrderedDict()
DT_beads["O3'* P O1P O2P O5' OP1 OP2"] = "BB1"
DT_beads["C5' O4' C4'"] = "BB2"
DT_beads["C3' C2' C1'"] = "BB3"
DT_beads["N1 C6"] = "SC1"
DT_beads["N3 C2 O2"] = "SC2"
DT_beads["C5 C4 O4 C7"] = "SC3"

A_beads = collections.OrderedDict()
A_beads["O3'* P O1P O2P O5' OP1 OP2"] = "BB1"
A_beads["C5' O4' C4'"] = "BB2"
A_beads["C3' C2' O2' C1'"] = "BB3"
A_beads["N9 C4"] = "SC1"
A_beads["C2 N3"] = "SC2"
A_beads["C6 N6 N1"] = "SC3"
A_beads["C8 N7 C5"] = "SC4"

C_beads = collections.OrderedDict()
C_beads["O3'* P O1P O2P O5' OP1 OP2"] = "BB1"
C_beads["C5' O4' C4'"] = "BB2"
C_beads["C3' C2' O2' C1'"] = "BB3"
C_beads["N1 C6"] = "SC1"
C_beads["N3 C2 O2"] = "SC2"
C_beads["C5 C4 N4"] = "SC3"

G_beads = collections.OrderedDict()
G_beads["O3'* P O1P O2P O5' OP1 OP2"] = "BB1"
G_beads["C5' O4' C4'"] = "BB2"
G_beads["C3' C2' O2' C1'"] = "BB3"
G_beads["N9 C4"] = "SC1"
G_beads["C2 N2 N3"] = "SC2"
G_beads["C6 O6 N1"] = "SC3"
G_beads["C8 N7 C5"] = "SC4"

U_beads = collections.OrderedDict()
U_beads["O3'* P O1P O2P O5' OP1 OP2"] = "BB1"
U_beads["C5' O4' C4'"] = "BB2"
U_beads["C3' C2' O2' C1'"] = "BB3"
U_beads["N1 C6"] = "SC1"
U_beads["N3 C2 O2"] = "SC2"
U_beads["C5 C4 O4"] = "SC3"

cg_mapping['DA'] = DA_beads
cg_mapping['DC'] = DC_beads
cg_mapping['DT'] = DT_beads
cg_mapping['DG'] = DG_beads

cg_mapping['A'] = A_beads
cg_mapping['C'] = C_beads
cg_mapping['U'] = U_beads
cg_mapping['G'] = G_beads

pairing = {
    ('DG', 'DC'): [('N2', 'O2'), ('N1', 'N3'), ('O6', 'N4')],
    ('DC', 'DG'): [('O2', 'N2'), ('N3', 'N1'), ('N4', 'O6')],
    ('DA', 'DT'): [('N6', 'O4'), ('N1', 'N3')],
    ('DT', 'DA'): [('O4', 'N6'), ('N3', 'N1')],
    #
    ('G', 'C'): [('N2', 'O2'), ('N1', 'N3'), ('O6', 'N4')],
    ('C', 'G'): [('O2', 'N2'), ('N3', 'N1'), ('N4', 'O6')],
    ('A', 'U'): [('N6', 'O4'), ('N1', 'N3')],
    ('U', 'A'): [('O4', 'N6'), ('N3', 'N1')],

    }

polar = ["GLN", "ASN", "SER", "THR"]
charged = ["ARG", "LYS", "ASP", "GLU"]

# ==========================================================================================#
# ==========================================================================================#
# ==========================================================================================#

parser = argparse.ArgumentParser()
parser.add_argument("input_pdb", help="Input PDB to be converted")
parser.add_argument("--skipss", help="Skip SS assignment, use only for xNA structures", action="store_true")
args = parser.parse_args()

if not args.input_pdb:
    exit()

P = PDBParser()
io = PDBIO()

# Parse PDB and run DSSP
pdbf_path = os.path.abspath(args.input_pdb)
aa_model = P.get_structure('aa_model', pdbf_path)

# set ALL bfactors to 0
for model in aa_model:
    for chain in model:
        if chain.id == ' ':
            print('+ ERROR: Empty chain id detected')
            exit()
        for residue in chain:
            for atom in residue:
                atom.bfactor = 0.0

# Assign HADDOCK code according to SS (1-9)
determine_ss(aa_model)

# Strandardize naming
# WARNING, THIS ASSUMES THAT INPUT DNA/RNA IS 3-LETTER CODE
rename_nucbases(aa_model)

# Assign HADDOCK code for hydrogen bonding capable nucleotides (0-1)
pair_list = determine_hbonds(aa_model)
if pair_list:
    output_cg_restraints(pair_list)
    # extract_groups(pair_list) # this might be useful for scripting

# Map CG beads to AA structure
structure_builder = StructureBuilder()
structure_builder.init_structure("cg_model")
structure_builder.init_seg(' ')  # Empty SEGID

tbl_cg_to_aa = []
restrain_counter = 0
for model in aa_model:

    structure_builder.init_model(model.id)

    for chain in model:

        structure_builder.init_chain(chain.id)
        structure_builder.init_seg(chain.id)

        mapping_dic = map_cg(chain)

        for residue in mapping_dic:
            if residue.id[0] != ' ':  # filter HETATMS
                continue

            structure_builder.init_residue(residue.resname, residue.id[0], residue.id[1], residue.id[2])

            for i, bead in enumerate(mapping_dic[residue]):

                bead_name = bead
                bead_coord = mapping_dic[residue][bead_name][0]
                haddock_code = mapping_dic[residue][bead_name][1]
                restrain = mapping_dic[residue][bead_name][2]

                structure_builder.init_atom(
                        bead_name,
                        bead_coord,
                        haddock_code,
                        1.00,
                        " ",
                        bead_name,
                        i)

                tbl_cg_to_aa.append(restrain)
                restrain_counter += 1

cg_model = structure_builder.get_structure()

# Write CG structure
io.set_structure(cg_model)
io.save('%s_cg.pdb' % (pdbf_path[:-4]), write_end=1)

# make sure atom names are in the correct place
# .BB. .BB1. .BB2. and not BB.. BB1.. BB2..
out = open('temp.pdb', 'w')
for l in open('%s_cg.pdb' % (pdbf_path[:-4])):
    if 'ATOM' in l[:4]:
        atom_name = l[12:16].split()[0]
        if len(atom_name) == 3:
            n_l = l[:12] + ' ' + atom_name + l[16:]
        elif len(atom_name) == 2:
            n_l = l[:12] + ' ' + atom_name + ' ' + l[16:]
        elif len(atom_name) == 1:
            n_l = l[:12] + ' ' + atom_name + '  ' + l[16:]
        else:
            n_l = l
    else:
        n_l = l
    out.write(n_l)

out.close()
os.system('\mv temp.pdb %s_cg.pdb' % (pdbf_path[:-4]))

# Write Restraints
tbl_file = open('%s_cg_to_aa.tbl' % pdbf_path[:-4], 'w')
tbl_file.write('\n%s' % '\n'.join([tbl for tbl in tbl_cg_to_aa if tbl]))
tbl_file.close()

# end
