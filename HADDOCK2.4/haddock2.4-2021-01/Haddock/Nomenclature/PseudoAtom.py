"""
This module provides methods for the conversion of cns atomnames in
pseudoatomes and vice versa.

The nomenclature of the pseudoatoms is in the same spirit as in:
Markley et al. JMB 280, 933-952 (1998)

Methods:
    Pseudo2Atom(atom)   e.g. 'QA' -> 'ha#'
                             'QR' -> 'hd# or name he# or name hz'
    Pseudo2Tuple(atom)  e.g. 'QA' -> ('ha#',)
                             'QR' -> ('hd#', 'he#', 'hz#')
    Atom2Pseudo(atomname, aminoacid)
                        e.g. 'HB1', 'TYR' -> ('QB', )
                             'HG11', 'VAL' ->  ('QG1', 'QQG')
    Pseudo2IupacTuple(threelettercode, atomname)
                        
"""
__author__   = "$Author: abonvin $"
__revision__ = "$Revision: 2.1 $"
__date__     = "$Date: 2010/02/10 16:12:48 $"


import re, string


###############################################################################
def Pseudo2Atom(atom):
    """
    converts pseudoatoms into a CNS readable format
    input:   atom name (can be a pseudoatom)
    output:  CNS readable atom name
    """    
    replacedic = {'QA': 'ha#',
                  'QB': 'hb#',
                  'QG': 'hg#',
                  'QG1': 'hg1#',
                  'QG2': 'hg2#',
                  'QQG': 'hg#',
                  'QD': 'hd#',
                  'QD1': 'hd1#',
                  'QD2': 'hd2#',
                  'QQD': 'hd#',
                  'QE': 'he#',
                  'QE2': 'he2#',
                  'QR': 'hd# or name he# or name hz',
                  'QZ': 'hz#',
                  'QH1': 'hh1#',
                  'QH2': 'hh2#'}
    atom = string.upper(atom)
    atom = string.strip(atom)
    if replacedic.has_key(atom):
        atom = replacedic[atom]
    return atom

def Pseudo2IupacTuple(threelettercode, atomname):
    """
    converting pseudoatoms into tuples of atomnames in IUPAC nomenclature
    
    input:   atomname (in IUPAC nomenclature, but may contain pseudoatoms as
             specified in Markley et al. JMB 280, 933-952 (1998), may contain
             wildcards #?%*, may be without the final number in the atomname,
             e.g 'HB' instead of 'HB%')
             atomnamemust be a string! No tuples or lists!
             threelettercode must be a string, e.g. 'TRP'
    output:  tuple of IUPAC atomnames, without wildcards
             the output is a tuple of strings!
 
    example: Pseudo2IupacTuple('ALA', 'HB%')
             returns the tuple of strings:
                 ('HB1', 'HB2', 'HB3')
 
    Note:    the strings threelettercode and atomname may
             be upper or lower case
             The returned atomname is ALWAYS upper case!
    """
    #convert wildcards "#", "?", "*" to "%":
    atomname = re.sub('\#', '%', atomname)
    atomname = re.sub('\?', '%', atomname)
    atomname = re.sub('\*', '%', atomname)
    atomname = string.upper(atomname)
    atomname = string.strip(atomname)
    threelettercode = string.upper(threelettercode)
    threelettercode = string.strip(threelettercode)
    
    #define the dictionaries for the conversion:
    # some notes:
    # HZ in TYR is not included in pseudoatom QR
    # QD and QD2 are used in ASN
    # QE and QE2 are used in GLN
    # QD and QD1 are used in ILE
    replacedic = {'ALA': {'QB':  ('HB1', 'HB2', 'HB3'),\
                          'HB%': ('HB1', 'HB2', 'HB3'),\
                          'HB':  ('HB1', 'HB2', 'HB3')},\
                  'ARG': {'QB':  ('HB2', 'HB3'),\
                          'HB%': ('HB2', 'HB3'),\
                          'HB':  ('HB2', 'HB3'),\
                          'QG':  ('HG2', 'HG3'),\
                          'HG%': ('HG2', 'HG3'),\
                          'HG':  ('HG2', 'HG3'),\
                          'QD':  ('HD2', 'HD3'),\
                          'HD%': ('HD2', 'HD3'),\
                          'HD':  ('HD2', 'HD3'),\
                          'QH1': ('HH11', 'HH12'),\
                          'HH1%':('HH11', 'HH12'),\
                          'HH1': ('HH11', 'HH12'),\
                          'QH2': ('HH21', 'HH22'),\
                          'HH2%':('HH21', 'HH22'),\
                          'HH2': ('HH21', 'HH22')},\
                  'ASN': {'QB':  ('HB2', 'HB3'),\
                          'HB%': ('HB2', 'HB3'),\
                          'HB':  ('HB2', 'HB3'),\
                          'QD2': ('HD21', 'HD22'),\
                          'HD2%':('HD21', 'HD22'),\
                          'HD2': ('HD21', 'HD22'),\
                          'QD':  ('HD21', 'HD22'),\
                          'HD%': ('HD21', 'HD22'),\
                          'HD':  ('HD21', 'HD22')},\
                  'ASP': {'QB':  ('HB2', 'HB3'),\
                          'HB%': ('HB2', 'HB3'),\
                          'HB':  ('HB2', 'HB3')},\
                  'CYS': {'QB':  ('HB2', 'HB3'),\
                          'HB%': ('HB2', 'HB3'),\
                          'HB':  ('HB2', 'HB3')},\
                  'GLN': {'QB':  ('HB2', 'HB3'),\
                          'HB%': ('HB2', 'HB3'),\
                          'HB':  ('HB2', 'HB3'),\
                          'QG':  ('HG2', 'HG3'),\
                          'HG%': ('HG2', 'HG3'),\
                          'HG':  ('HG2', 'HG3'),\
                          'QE2': ('HE21', 'HE22'),\
                          'HE2%':('HE21', 'HE22'),\
                          'HE2': ('HE21', 'HE22'),\
                          'QE':  ('HE21', 'HE22'),\
                          'HE%': ('HE21', 'HE22'),\
                          'HE':  ('HE21', 'HE22'),
                          },\
                  'GLU': {'QB':  ('HB2', 'HB3'),\
                          'HB%': ('HB2', 'HB3'),\
                          'HB':  ('HB2', 'HB3'),\
                          'QG':  ('HG2', 'HG3'),\
                          'HG%': ('HG2', 'HG3'),\
                          'HG':  ('HG2', 'HG3')},\
                  'GLY': {'QA':  ('HA2', 'HA3'),\
                          'HA%': ('HA2', 'HA3'),\
                          'HA':  ('HA2', 'HA3')},\
                  'HIS': {'QB':  ('HB2', 'HB3'),\
                          'HB%': ('HB2', 'HB3'),\
                          'HB':  ('HB2', 'HB3')},
                  'ILE': {'QG1': ('HG12', 'HG13'),\
                          'HG1%':('HG12', 'HG13'),\
                          'HG1': ('HG12', 'HG13'),\
                          'QG2': ('HG21', 'HG22', 'HG23'),\
                          'HG2%':('HG21', 'HG22', 'HG23'),\
                          'HG2': ('HG21', 'HG22', 'HG23'),\
                          'QQG': ('HG12', 'HG13', 'HG21', 'HG22', 'HG23'),\
                          'HG%': ('HG12', 'HG13', 'HG21', 'HG22', 'HG23'),\
                          'HG':  ('HG12', 'HG13', 'HG21', 'HG22', 'HG23'),\
                          'QD1': ('HD1', 'HD2', 'HD3'),\
                          'HD1%':('HD1', 'HD2', 'HD3'),\
                          'HD1': ('HD1', 'HD2', 'HD3'),\
                          'QD':  ('HD1', 'HD2', 'HD3'),\
                          'HD%': ('HD1', 'HD2', 'HD3'),\
                          'HD':  ('HD1', 'HD2', 'HD3')},\
                  'LEU': {'QB':  ('HB2', 'HB3'),\
                          'HB%': ('HB2', 'HB3'),\
                          'HB':  ('HB2', 'HB3'),\
                          'QD1': ('HD11', 'HD12', 'HD13'),\
                          'HD1%':('HD11', 'HD12', 'HD13'),\
                          'HD1': ('HD11', 'HD12', 'HD13'),\
                          'QD2': ('HD21', 'HD22', 'HD23'),\
                          'HD2%':('HD21', 'HD22', 'HD23'),\
                          'HD2': ('HD21', 'HD22', 'HD23'),\
                          'QQD': ('HD11', 'HD12', 'HD13', 'HD21', 'HD22', 'HD23'),\
                          'HD%': ('HD11', 'HD12', 'HD13', 'HD21', 'HD22', 'HD23'),\
                          'HD':  ('HD11', 'HD12', 'HD13', 'HD21', 'HD22', 'HD23')},\
                  'LYS': {'QB':  ('HB2', 'HB3'),\
                          'HB%': ('HB2', 'HB3'),\
                          'HB':  ('HB2', 'HB3'),\
                          'QG':  ('HG2', 'HG3'),\
                          'HG%': ('HG2', 'HG3'),\
                          'HG':  ('HG2', 'HG3'),\
                          'QD':  ('HD2', 'HD3'),\
                          'HD%': ('HD2', 'HD3'),\
                          'HD':  ('HD2', 'HD3'),\
                          'QE':  ('HE2', 'HE3'),\
                          'HE%': ('HE2', 'HE3'),\
                          'HE':  ('HE2', 'HE3'),\
                          'QZ':  ('HZ1', 'HZ2', 'HZ3'),\
                          'HZ%': ('HZ1', 'HZ2', 'HZ3'),\
                          'HZ':  ('HZ1', 'HZ2', 'HZ3')},\
                  'MET': {'QB':  ('HB2', 'HB3'),\
                          'HB%': ('HB2', 'HB3'),\
                          'HB':  ('HB2', 'HB3'),\
                          'QG':  ('HG2', 'HG3'),\
                          'HG%': ('HG2', 'HG3'),\
                          'HG':  ('HG2', 'HG3'),\
                          'QE':  ('HE1', 'HE2', 'HE3'),\
                          'HE%': ('HE1', 'HE2', 'HE3'),\
                          'HE':  ('HE1', 'HE2', 'HE3')},\
                  'PHE': {'QB':  ('HB2', 'HB3'),\
                          'HB%': ('HB2', 'HB3'),\
                          'HB':  ('HB2', 'HB3'),\
                          'QD':  ('HD1', 'HD2'),\
                          'HD%': ('HD1', 'HD2'),\
                          'HD':  ('HD1', 'HD2'),\
                          'QE':  ('HE1', 'HE2'),\
                          'HE%': ('HE1', 'HE2'),\
                          'HE':  ('HE1', 'HE2'),\
                          'QR':  ('HD1', 'HD2', 'HE1', 'HE2', 'HZ'),\
                          'HR%': ('HD1', 'HD2', 'HE1', 'HE2', 'HZ'),\
                          'HR':  ('HD1', 'HD2', 'HE1', 'HE2', 'HZ')},\
                  'PRO': {'QB':  ('HB2', 'HB3'),\
                          'HB%': ('HB2', 'HB3'),\
                          'HB':  ('HB2', 'HB3'),\
                          'QG':  ('HG2', 'HG3'),\
                          'HG%': ('HG2', 'HG3'),\
                          'HG':  ('HG2', 'HG3'),\
                          'QD':  ('HD2', 'HD3'),\
                          'HD%': ('HD2', 'HD3'),\
                          'HD':  ('HD2', 'HD3')},\
                  'SER': {'QB':  ('HB2', 'HB3'),\
                          'HB%': ('HB2', 'HB3'),\
                          'HB':  ('HB2', 'HB3')},\
                  'THR': {'QB':  ('HB', ),\
                          'HB%': ('HB', ),\
                          'HB':  ('HB', ),\
                          'QG2': ('HG21', 'HG22', 'HG23'),\
                          'HG2%':('HG21', 'HG22', 'HG23'),\
                          'HG2': ('HG21', 'HG22', 'HG23')},\
                  'TRP': {'QB':  ('HB2', 'HB3'),\
                          'HB%': ('HB2', 'HB3'),\
                          'HB':  ('HB2', 'HB3'),\
                          'QG2': ('HG21', 'HG22', 'HG23'),\
                          'HG2%':('HG21', 'HG22', 'HG23'),\
                          'HG2': ('HG21', 'HG22', 'HG23')},
                  'TYR': {'QB':  ('HB2', 'HB3'),\
                          'HB%': ('HB2', 'HB3'),\
                          'HB':  ('HB2', 'HB3'),\
                          'QD':  ('HD1', 'HD2'),\
                          'HD%': ('HD1', 'HD2'),\
                          'HD':  ('HD1', 'HD2'),\
                          'QE':  ('HE1', 'HE2'),\
                          'HE%': ('HE1', 'HE2'),\
                          'HE':  ('HE1', 'HE2'),\
                          'QR':  ('HD1', 'HD2', 'HE1', 'HE2'),\
                          'HR%': ('HD1', 'HD2', 'HE1', 'HE2'),\
                          'HR':  ('HD1', 'HD2', 'HE1', 'HE2')},\
                  'VAL': {'QG1': ('HG11', 'HG12', 'HG13'),\
                          'HG1%':('HG11', 'HG12', 'HG13'),\
                          'HG1': ('HG11', 'HG12', 'HG13'),\
                          'QG2': ('HG21', 'HG22', 'HG23'),\
                          'HG2%':('HG21', 'HG22', 'HG23'),\
                          'HG2': ('HG21', 'HG22', 'HG23'),\
                          'QQG': ('HG11', 'HG12', 'HG13', 'HG21', 'HG22', 'HG23'),\
                          'HG%': ('HG11', 'HG12', 'HG13', 'HG21', 'HG22', 'HG23'),\
                          'HG':  ('HG11', 'HG12', 'HG13', 'HG21', 'HG22', 'HG23')}}
 
    if replacedic.has_key(threelettercode):
        if replacedic[threelettercode].has_key(atomname):
            atomname = replacedic[threelettercode][atomname]
        else:
            atomname = (atomname, )
    else:
        atomname = (atomname, )
    return atomname



###############################################################################
def Pseudo2Tuple(atom):
    """
    converts pseudoatoms into a tuple of atomnames in a CNS readable format
    input:   atom name (can be a pseudoatom)
    output:  tuple of CNS readable atoms
    """    
    replacedic = {'QA': ('ha#', ),
                  'QB': ('hb#', ),
                  'QG': ('hg#', ),
                  'QG1': ('hg1#', ),
                  'QG2': ('hg2#', ),
                  'QQG': ('hg#', ),
                  'QD': ('hd#', ),
                  'QD1': ('hd1#', ),
                  'QD2': ('hd2#', ),
                  'QQD': ('hd#', ),
                  'QE': ('he#', ),
                  'QE2': ('he2#', ),
                  'QR': ('hd#', 'he#', 'hz'),
                  'QZ': ('hz#', ),
                  'QH1': ('hh1#', ),
                  'QH2': ('hh2#', )}
    atom = string.upper(atom)
    atom = string.strip(atom)
    if replacedic.has_key(atom):
            atom = replacedic[atom]
    else:
        atom = (atom, )
    return atom


###############################################################################
def Atom2Pseudo(atomname, aminoacid):
    """
    INPUT:   cns atomname and aminoacid type in 3-letter code
    OUTPUT:  returns a tuple of possible pseudoatoms, best hit comes first
             within the tuple
             if it is not possible to find a pseudoatom, an empty tuple
             will be returned

    The nomenclature of the pseudoatoms is in the same spirit as in:
    Markley et al. JMB 280, 933-952 (1998)
    easy:       ALA, ASP, ASN, CYS, GLN, GLU, GLY, HIS, LYS, MET,
                PRO, SER, THR, TRP
    ambiguous:  ARG: QH1, QH2 or QH
                ILE: QG1, QG2 or QQG
                LEU: QD1, QD2 or QQD
                PHE: QR
                TYR: QR
                VAL: QG1, QG2 or QQG
    """
    pseudoatom = ()
    aminoacid = string.upper(aminoacid)
    aminoacid = string.strip(aminoacid)
    atomname = string.upper(atomname)
    atomname = string.strip(atomname)
    if aminoacid == 'ALA':
        if atomname in ['HB1', 'HB2', 'HB3', 'HB%', 'HB#']:
            pseudoatom = ('QB', )
    elif aminoacid == 'ARG':
        if atomname in ['HB1', 'HB2', 'HB3', 'HB%', 'HB#']:
            pseudoatom = ('QB', )
        elif atomname in ['HG1', 'HG2', 'HG3', 'HG%', 'HG#']:
            pseudoatom = ('QG', )
        elif atomname in ['HD1', 'HD2', 'HD3', 'HD%', 'HD#']:
            pseudoatom = ('QD', )
        elif atomname in ['HH11', 'HH12', 'HH13', 'HH1%', 'HH1#']:
            pseudoatom = ('QH1', )
        elif atomname in ['HH21', 'HH22', 'HH23', 'HH2%', 'HH2#']:
            pseudoatom = ('QH2', )
    elif aminoacid == 'ASN':
        if atomname in ['HB1', 'HB2', 'HB3', 'HB%', 'HB#']:
            pseudoatom = ('QB', )
        elif atomname in ['HD1', 'HD2', 'HD3', 'HD1', 'HD2', 'HD3', 'HD%', 'HD#']:
            pseudoatom = ('QD2', )
    elif aminoacid == 'ASP':
        if atomname in ['HB1', 'HB2', 'HB3', 'HB%', 'HB#']:
            pseudoatom = ('QB', )
    elif aminoacid == 'CYS':
        if atomname in ['HB1', 'HB2', 'HB3', 'HB%', 'HB#']:
            pseudoatom = ('QB', )
    elif aminoacid == 'GLU':
        if atomname in ['HB1', 'HB2', 'HB3', 'HB%', 'HB#']:
            pseudoatom = ('QB', )
        elif atomname in ['HG1', 'HG2', 'HG3', 'HG%', 'HG#']:
            pseudoatom = ('QG', )   
    elif aminoacid == 'GLN':
        if atomname in ['HB1', 'HB2', 'HB3', 'HB%', 'HB#']:
            pseudoatom = ('QB', )
        elif atomname in ['HG1', 'HG2', 'HG3', 'HG%', 'HG#']:
            pseudoatom = ('QG', )
        elif atomname in ['HE21', 'HE22', 'HE2%', 'HE2#']:
            pseudoatom = ('QE2', )
    elif aminoacid == 'GLY':
        if atomname in ['HA1', 'HA2', 'HA3', 'HA%', 'HA#']:
            pseudoatom = ('QA', )
    elif aminoacid == 'HIS':
        if atomname in ['HB1', 'HB2', 'HB3', 'HB%', 'HB#']:
            pseudoatom = ('QB', )
    elif aminoacid == 'ILE':
        if atomname in ['HD11', 'HD12', 'HD13', 'HD1%', 'HD1#']:
            pseudoatom = ('QD1', )
        elif atomname in ['HG11', 'HG12', 'HG13', 'HG1%', 'HG1#']:
            pseudoatom = ('QG1', 'QQG')
        elif atomname in ['HG21', 'HG22', 'HG23', 'HG2%', 'HG2#']:
            pseudoatom = ('QG2', 'QQG')
        elif atomname[:2] == 'HG':
            pseudoatom == ('QQG', 'QG1', 'QG2')
    elif aminoacid == 'LEU':
        if atomname in ['HB1', 'HB2', 'HB3', 'HB%', 'HB#']:
            pseudoatom = ('QB', )
        elif atomname in ['HD11', 'HD12', 'HD13', 'HD1%', 'HD1#']:
            pseudoatom = ('QD1', 'QQD')
        elif atomname in ['HD21', 'HD22', 'HD23', 'HD2%', 'HD2#']:
            pseudoatom = ('QD2', 'QQD')
        elif atomname[:2] == 'HD':
            pseudoatom = ('QQD', 'QD1', 'QD2')
    elif aminoacid == 'LYS':
        if atomname in ['HB1', 'HB2', 'HB3', 'HB%', 'HB#']:
            pseudoatom = ('QB', )
        elif atomname in ['HG1', 'HG2', 'HG3', 'HG%', 'HG#']:
            pseudoatom = ('QG', )
        elif atomname in ['HD1', 'HD2', 'HD3', 'HD%', 'HD#']:
            pseudoatom = ('QD', )   
        elif atomname in ['HE1', 'HE2', 'HE3', 'HE%', 'HE#']:
            pseudoatom = ('QE', )
        elif atomname in ['HZ1', 'HZ2', 'HZ3', 'HZ%', 'HZ#']:
            pseudoatom = ('QZ', )
    elif aminoacid == 'MET':
        if atomname in ['HB1', 'HB2', 'HB3', 'HB%', 'HB#']:
            pseudoatom = ('QB', )
        elif atomname in ['HG1', 'HG2', 'HG3', 'HG%', 'HG#']:
            pseudoatom = ('QG', )
        elif atomname in ['HE1', 'HE2', 'HE3', 'HE%', 'HE#']:
            pseudoatom = ('QE', )    
    elif aminoacid == 'PHE':
        if atomname in ['HB1', 'HB2', 'HB3', 'HB%', 'HB#']:
            pseudoatom = ('QB', )
        elif atomname in ['HD1', 'HD2', 'HD3', 'HD%', 'HD#']:
            pseudoatom = ('QD', 'QR')   
        elif atomname in ['HE1', 'HE2', 'HE3', 'HE%', 'HE#']:
            pseudoatom = ('QE', 'QR')
    elif aminoacid == 'PRO':
        if atomname in ['HB1', 'HB2', 'HB3', 'HB%', 'HB#']:
            pseudoatom = ('QB', )
        elif atomname in ['HG1', 'HG2', 'HG3', 'HG%', 'HG#']:
            pseudoatom = ('QG', )   
        elif atomname in ['HD1', 'HD2', 'HD3', 'HD%', 'HD#']:
            pseudoatom = ('QD', )
    elif aminoacid == 'SER':
        if atomname in ['HB1', 'HB2', 'HB3', 'HB%', 'HB#']:
            pseudoatom = ('QB', )
    elif aminoacid == 'THR':
        if atomname in ['HG21', 'HG22', 'HG23', 'HG2%', 'HG2#']:
            pseudoatom = ('QG2', )
    elif aminoacid == 'TRP':
        if atomname in ['HB1', 'HB2', 'HB3', 'HB%', 'HB#']:
            pseudoatom = ('QB', )
    elif aminoacid == 'TYR':
        if atomname in ['HB1', 'HB2', 'HB3', 'HB%', 'HB#']:
            pseudoatom = ('QB', )
        elif atomname in ['HD1', 'HD2', 'HD3', 'HD%', 'HD#']:
            pseudoatom = ('QD', 'QR')   
        elif atomname in ['HE1', 'HE2', 'HE3', 'HE%', 'HE#']:
            pseudoatom = ('QE', 'QR')
    elif aminoacid == 'VAL':
        if atomname in ['HG11', 'HG12', 'HG13', 'HG1%', 'HG1#']:
            pseudoatom = ('QG1', 'QQG')
        elif atomname in ['HG21', 'HG22', 'HG23', 'HG2%', 'HG2#']:
            pseudoatom = ('QG2', 'QQG')
        elif pseudoatom[:2] == 'HG':
            pseudoatom = ('QQG', 'QG1', 'QG2')
    return pseudoatom


###############################################################################
#test code:
if __name__ == "__main__":
    print 'testing module:\n'
    print "  converting ('TYR', 'QR,) to:", Pseudo2IupacTuple('tyr', 'QR')
    print "  should be IUPAC nomenclature..."
    print '\nciao.'

