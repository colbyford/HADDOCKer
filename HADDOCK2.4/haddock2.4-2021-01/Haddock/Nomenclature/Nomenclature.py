"""
A module to convert atomnames to IUPAC nomenclature

uses two library files which have to be in the directory
Haddock.Nomenclature

"""
__author__   = "$Author: abonvin $"
__revision__ = "$Revision: 2.1 $"
__date__     = "$Date: 2010/02/10 16:12:48 $"

import os, re, string, sys

from Haddock.Nomenclature import AminoAcid, PseudoAtom


##  we put the XPLOR BMRB files in the directory Haddock/Nomenclature
##  the files are:  PseudoLIB-aqua
##                  AtomLIB-xplor

# get the path:
from Haddock.Nomenclature import PseudoAtom
NomenclatureDir = os.path.split(PseudoAtom.__file__)[0]
AtomLIBFN = os.path.join(NomenclatureDir, 'AtomLIB-xplor')
PseudoLIBFN = os.path.join(NomenclatureDir, 'PseudoLIB-aqua')
StereoLIBFN = os.path.join(NomenclatureDir, 'StereoLIB-aqua')


class Lister:
    """Example from 'Learning Python from O'Reilly publisher'"""
    def __repr__(self):
        return ("<Instance of %s, address %s:\n%s>" %
           (self.__class__.__name__, id(self), self.attrnames()))

    def attrnames(self):
        result=''
        keys = self.__dict__.keys()
        keys.sort()
        for attr in keys:
            if attr[:2] == "__":
                result = result + "\tname %s=<built-in>\n" % attr
            else:
                result = result + "\tname %s=%s\n" % (attr, self.__dict__[attr])
        return result


class AtomLib_Xplor( Lister ):

    # Exports only one attribute: iupac_name
    
    #I. Set up the mapping table, this should of course be done only once
    ## and the results stored in a global class
    def __init__(self, AtomLib_Xplor_FileName):
    
        ## Regular expression pattern matching just the definitions from the
        ## AQUA atom name library
        pattern = re.compile(r"""
            ^def         \s+      # Start with def
             (\w+)       \s+      # Residue name
             \*          \s+      # Actual '*'
             (\w+\#)     \s+      # CNS pseudo atom name with trailing '#'
             (\w+)       \s*$     # IUPAC pseudo atom name
                 """, re.IGNORECASE | re.MULTILINE | re.VERBOSE )
            
        ## Read file contents, leave file handle open later on?
        file_content = open(AtomLib_Xplor_FileName, 'r').read()
        match_list = pattern.findall( file_content ) 
        if ( match_list ):
            pass
#            print "Read %d definitions from file: %s"         % ( len(match_list), AtomLib_Xplor_FileName )
        else:
            print "ERROR: No definitions read from file: %s"    % AtomLib_Xplor_FileName
            print "       Please check the library filenames specified in Nomenclature.py"
#            sys.exit(1)
            
        self.iupac_name = {}    
        for match in match_list:
            # Create a new sub dictionary if needed
            if not self.iupac_name.has_key( match[0] ):
                self.iupac_name[ match[0] ] = {}
            self.iupac_name[ match[0] ][ match[1] ] = match[2]

class PseudoAtomLib( Lister ):

    ## Exports two attributes: pseudo_atom and pseudo_atom_by_type
    ## E.g.:
    ## pseudo_atom             ["LEU"]["MD1"]  = ( 2, ("HD11", "HD12", "HD13") )
    ## pseudo_atom_by_type["2"]["LEU"]["HD11"] = "MD1"
    
    ## Results stored in a global class
    def __init__(self, PseudoAtomLib_FileName):

        PseudoAtomTypeList          = [ 1, 2, 3, 4, 5, 6, 7 ]  ## See file for type listing
        # Number of atoms in pseudo atom before expanding pseudoatoms in pseudoatom again
        PseudoAtomMembers           = {
            1:2, # CH2 or NH2
            2:3, # methyl or NH3
            3:4, # double CH2/NH2
            4:6, # double methyl
            5:2, # Aromat with 2 H
            6:4, # Aromat with 4 H
            7:5  # Aromat with 5 H
            }

        maximumPseudoAtomType       = 7 ## All ring protons of PHE or TYR
        maximumPseudoAtomMembers    = 6 ## Double methyl group

        self.pseudoAtomLib_FileName = PseudoAtomLib_FileName
        ## Regular expression pattern matching just the definitions from the
        ## AQUA atom name library
        pattern = re.compile(r"""
            ^def         \s+        # Start with def
             (\S+)       \s+        # Residue name, GROUP 0
                                    # \S used to allow - and + signs
             \*          \s+        # Actual '*'
             (\S+)       \s+        # IUPAC pseudo atom name, GROUP 1
                                    # \S used to allow single quotes to be matched
             (\d)        \s+        # Pseudo atom type (single digit), GROUP 2
             (.+)        \s*$       # IUPAC multiple constituting atom names up, GROUP 3
                                    # to the end. Still need to be parsed.
                 """, re.IGNORECASE | re.MULTILINE | re.VERBOSE )
            
        ## Read file contents, leave file handle open later on?
        file_content = open(self.pseudoAtomLib_FileName, 'r').read()
        match_list = pattern.findall( file_content ) 
        if ( match_list ):
            pass
#            print "Read %d pseudo atom definitions from file: %s"   %\
#                  ( len(match_list), self.pseudoAtomLib_FileName )
        else:
            print "ERROR: No definitions read from file: %s"        %\
                  self.pseudoAtomLib_FileName
            print "       Please check the library filenames specified in Nomenclature.py"
#            sys.exit(1)
            
        self.pseudo_atom            = {}
        self.pseudo_atom_by_type    = {}
        
        for match in match_list:
            residue_name        = match[0]
            pseudo_atom_name    = match[1]
            pseudo_atom_type    = int(  match[2] )
            atom_list           = string.split( match[3] )
            ## Test integrity pseudo atom types
            if not pseudo_atom_type in PseudoAtomTypeList:
                print "ERROR: Pseudo atom type for residue name %s and pseudo atom: %s" \
                      % ( residue_name, pseudo_atom_name )
                print "ERROR: and constituting atoms: %s" \
                      % atom_list
                print "ERROR: should be in set: %s but was found to be: %s" \
                      % ( PseudoAtomTypeList, pseudo_atom_type )
                sys.exit(1)
            
            ## Test integrity constituting atoms
            if len( atom_list ) != PseudoAtomMembers[pseudo_atom_type]:
                print "ERROR: Pseudo atom definitions for residue name %s and pseudo atom: %s" \
                      % ( residue_name, pseudo_atom_name )
                print "ERROR: number of constituting atoms: %s is not %s as expected" \
                      % ( atom_list, PseudoAtomMembers[pseudo_atom_type] )
                sys.exit(1)
                
            ## Create a new sub dictionary and sub/sub dictionary if needed
            if not self.pseudo_atom_by_type.has_key( pseudo_atom_type ):
                self.pseudo_atom_by_type[ pseudo_atom_type ] = {}
            if not self.pseudo_atom_by_type[ pseudo_atom_type ].has_key( residue_name ):
                self.pseudo_atom_by_type[ pseudo_atom_type ][ residue_name ] = {}
            for atom_name in ( atom_list ):
                if ( self.pseudo_atom_by_type[ pseudo_atom_type ][ residue_name ].has_key( atom_name ) ):
                    print "WARNING: atom: %s already defined for residue name: %s" \
                          % ( atom_name, residue_name )
                    print "WARNING: in same type of pseudoatom: %s" % pseudo_atom_type
                self.pseudo_atom_by_type[ pseudo_atom_type ][ residue_name ][ atom_name ] = \
                    pseudo_atom_name
                
            ## Create a new sub dictionary if needed
            if not self.pseudo_atom.has_key( residue_name ):
                self.pseudo_atom[ residue_name ] = {}
            if ( self.pseudo_atom[ residue_name ].has_key( pseudo_atom_name ) ):
                print "WARNING: pseudo atom: %s already defined for residue name: %s" \
                      % ( pseudo_atom_name, residue_name )
            ## So the value to this is a list of a integer and a list (which is a list of strings)
            self.pseudo_atom[ residue_name ][ pseudo_atom_name ] = ( pseudo_atom_type, atom_list )


class StereoAtomLib( Lister ):

    ## Exports two attributes: stereo_atom and stereo_atom_by_type
    ## E.g.:
    ## stereo_atom             ["LEU"]["QD"]  = ( 4, ("MD1", "MD2") )
    ## stereo_atom_by_type["4"]["LEU"]["MD1"] = "QD"
    
    ## Results stored in a global class
    def __init__(self, StereoAtomLib_FileName):

        StereoAtomTypeList          = [ 1, 2, 3, 4, 5, 6, 7 ]  ## See file for type listing
        # Number of atoms in pseudo atom before expanding pseudoatoms in pseudoatom again
        StereoAtomMembers           = {
            1:2, # CH2 or NH2
            2:3, # methyl or NH3
            3:2, # double CH2/NH2
            4:2, # double methyl
            5:2, # Aromat with 2 H
            6:2, # Aromat with 4 H
            7:3  # Aromat with 5 H
            }

        self.stereoAtomLib_FileName = StereoAtomLib_FileName
        ## Regular expression pattern matching just the definitions from the
        ## AQUA atom name library
        pattern = re.compile(r"""
            ^def         \s+        # Start with def
             (\S+)       \s+        # Residue name, GROUP 0
                                    # \S used to allow - and + signs
             \*          \s+        # Actual '*'
             (\S+)       \s+        # IUPAC pseudo atom name, GROUP 1
                                    # \S used to allow single quotes to be matched
             (\d)        \s+        # Pseudo atom type (single digit), GROUP 2
             (.+)        \s*$       # IUPAC multiple constituting atom names up, GROUP 3
                                    # to the end. Still need to be parsed.
                 """, re.IGNORECASE | re.MULTILINE | re.VERBOSE )
            
        ## Read file contents, leave file handle open later on?
        file_content = open(self.stereoAtomLib_FileName, 'r').read()
        match_list = pattern.findall( file_content ) 
        if not match_list:
            print "Read %d stereo atom definitions from file: %s"   %\
                  ( len(match_list), self.stereoAtomLib_FileName )
            print "ERROR: No definitions read from file: %s"        %\
                  self.stereoAtomLib_FileName
            print "       Please check the library filenames specified in Nomenclature.py"
#            sys.exit(1)
            
        self.stereo_atom            = {}
        self.stereo_atom_by_type    = {}
        
        for match in match_list:
            residue_name        = match[0]
            stereo_atom_name    = match[1]
            stereo_atom_type    = int(  match[2] )
            atom_list           = string.split( match[3] )
            ## Test integrity pseudo atom types
            if not (stereo_atom_type in StereoAtomTypeList ):
                print "ERROR: Pseudo atom type for residue name %s and pseudo atom: %s" \
                      % ( residue_name, stereo_atom_name )
                print "ERROR: and constituting atoms: %s" \
                      % atom_list
                print "ERROR: should be in list %s but was found to be: %s" \
                      % ( StereoAtomTypeList, stereo_atom_type )
                sys.exit(1)
            
            ## Test integrity constituting atoms
            if ( len( atom_list ) != StereoAtomMembers[stereo_atom_type] ):
                print "ERROR: Pseudo atom definitions for residue name %s and pseudo atom: %s" \
                      % ( residue_name, stereo_atom_name )
                print "ERROR: number of constituting atoms: %s is not %s" \
                      % ( atom_list, StereoAtomMembers[stereo_atom_type] )
                sys.exit(1)
                
            ## Create a new sub dictionary and sub/sub dictionary if needed
            if not self.stereo_atom_by_type.has_key( stereo_atom_type ):
                self.stereo_atom_by_type[ stereo_atom_type ] = {}
            if not self.stereo_atom_by_type[ stereo_atom_type ].has_key( residue_name ):
                self.stereo_atom_by_type[ stereo_atom_type ][ residue_name ] = {}
            for atom_name in ( atom_list ):
                if ( self.stereo_atom_by_type[ stereo_atom_type ][ residue_name ].has_key( atom_name ) ):
                    print "WARNING: atom: %s already defined for residue name: %s" \
                          % ( atom_name, residue_name )
                    print "WARNING: in same type of pseudoatom: %s" % stereo_atom_type
                self.stereo_atom_by_type[ stereo_atom_type ][ residue_name ][ atom_name ] = \
                    stereo_atom_name
                
            ## Create a new sub dictionary if needed
            if not self.stereo_atom.has_key( residue_name ):
                self.stereo_atom[ residue_name ] = {}
            if ( self.stereo_atom[ residue_name ].has_key( stereo_atom_name ) ):
                print "WARNING: pseudo atom: %s already defined for residue name: %s" \
                      % ( stereo_atom_name, residue_name )
            ## So the value to this is a list of a integer and a list (which is a list of strings)
            self.stereo_atom[ residue_name ][ stereo_atom_name ] = ( stereo_atom_type, atom_list )


def ConvertCnsProtonNames(residueName, atomName):
    """
    convert an atomname from XPLOR/CNS to IUPAC nomenclature (or vice versa)
    residueName: a string which contains 1- or 3-letter code, e.g. 'A' or 'ALA'
                 only the 20 common aminoacids are supported!
    atomName:    a string comtaining the atomnames, e.g. 'HG12'

    returns a string with the new atomname (all characters are uppercase)
    If the atom name doesn't have to be changed, it will return the input
    atom name (stripped and uppercase)
    """
    #I. get a clean three-letter code and strip & uppercase the atomName
    threeLetter = AminoAcid.AminoAcid(residueName)[1]
    if threeLetter[2] == '':
        print 'WARNING: residue name', residueName, 'not understood'
        return atomName
    atomName = string.upper(string.strip(atomName))
    
    #II. methylenes
    #1. GLY HA:
    if threeLetter == 'GLY' and atomName == 'HA1':
        atomName = 'HA2'
    elif threeLetter == 'GLY' and atomName == 'HA2':
        atomName = 'HA1'
        
    #2. ARG, ASN, ASP, CYS, GLN, GLU, HIS, LEU, LYS, MET, PHE, PRO, SER, TRP, TYR HB%:
    elif threeLetter in ('ARG', 'ASN', 'ASP', 'CYS', 'GLN', 'GLU', 'HIS', 'LEU', 'LYS',\
                         'MET', 'PHE', 'PRO', 'SER', 'TRP', 'TYR') and \
                         atomName == 'HB3':
        atomName = 'HB1'
    elif threeLetter in ('ARG', 'ASN', 'ASP', 'CYS', 'GLN', 'GLU', 'HIS', 'LEU', 'LYS',\
                         'MET', 'PHE', 'PRO', 'SER', 'TRP', 'TYR') and \
                         atomName == 'HB1':
        atomName = 'HB3'

    #3. ARG, GLN, GLU, LYS, MET, PRO HG%:
    elif threeLetter in ('ARG', 'GLN', 'GLU', 'LYS', 'MET', 'PRO') and\
         atomName == 'HG1':
        atomName = 'HG3'
    elif threeLetter in ('ARG', 'GLN', 'GLU', 'LYS', 'MET', 'PRO') and\
         atomName == 'HG3':
        atomName = 'HG1'
    #4. ILE HG1%:
    elif threeLetter == 'ILE' and atomName == 'HG13':
        atomName = 'HG11'
    elif threeLetter == 'ILE' and atomName == 'HG11':
        atomName = 'HG13' 
    #5. ARG, ASN, LYS, PRO HD:
    elif threeLetter in ('ARG', 'ASN', 'LYS', 'PRO') and atomName == 'HD1':
        atomName = 'HD3'
    elif threeLetter in ('ARG', 'ASN', 'LYS', 'PRO') and atomName == 'HD3':
        atomName = 'HD1'
    #6. LYS HE:
    elif threeLetter == 'LYS' and atomName == 'HE3':
        atomName = 'HE1'
    elif threeLetter == 'LYS' and atomName == 'HE1':
        atomName = 'HE3'
        
    #III. methyls:
    #1. ALA beta:
    elif threeLetter == 'ALA' and atomName == 'HB2':
        atomName = 'HB1'
    elif threeLetter == 'ALA' and atomName == 'HB1':
        atomName = 'HB2'
    #2. VAL gamma1:
    elif threeLetter == 'VAL' and atomName == 'HG11':
        atomName = 'HG12'
    elif threeLetter == 'VAL' and atomName == 'HG12':
        atomName = 'HG11'
    #3. ILE, VAL gamma2:
    elif threeLetter in ('ILE', 'VAL') and atomName == 'HG21':
        atomName = 'HG22'
    elif threeLetter in ('ILE', 'VAL') and atomName == 'HG22':
        atomName = 'HG21'
    #4. ILE, LEU delta1:
    elif threeLetter in ('ILE', 'LEU') and atomName == 'HD11':
        atomName = 'HD12'
    elif threeLetter in ('ILE', 'LEU') and atomName == 'HD12':
        atomName = 'HD11'    
    #5. LEU delta2:
    elif threeLetter == 'LEU' and atomName == 'HD21':
        atomName = 'HD22'
    elif threeLetter == 'LEU' and atomName == 'HD22':
        atomName = 'HD21'    
    #6. MET epsilon:
    elif threeLetter == 'MET' and atomName == 'HE1':
        atomName = 'HE2'
    elif threeLetter == 'MET' and atomName == 'HE2':
        atomName = 'HE1'

    #7. zeta:
    elif threeLetter != 'TRP' and atomName == 'HZ1':
        atomName = 'HZ2'
    elif threeLetter != 'TRP' and atomName == 'HZ2':
        atomName = 'HZ1'     
        
    #IV. ARG NHs:
    elif threeLetter == 'ARG' and atomName == 'HH11':
        atomName = 'HH12'
    elif threeLetter == 'ARG' and atomName == 'HH12':
        atomName = 'HH11'
    elif threeLetter == 'ARG' and atomName == 'HH21':
        atomName = 'HH22'
    elif threeLetter == 'ARG' and atomName == 'HH22':
        atomName = 'HH21'    

    return atomName


def Convert_PseudoAtomName_CNS_2_IUPAC(residueName, atomName):
    """
    convert an pseudo atomname from XPLOR/CNS to IUPAC nomenclature (or vice versa)
    residueName: a string which contains full code, e.g. 'A' is not 'ALA'
                 but is allowed for DADE and RADE (this needs work)
                 only the 20 common aminoacids are supported!
    atomName:    a string containing the atomnames, e.g. 'HG1#'

    returns a string with the new atomname (all characters are uppercase)
    If the atom name doesn't have to be changed, it will return the input
    atom name (stripped and uppercase)
    
    e.g.        ALA HB#  -> MB
            LEU HD1% -> MD1
            VAL HG#  -> QG
            
    This last example might be more than expected since HG# doesn't expand
    to HG11 and the 5 other protons.
    """

    if ( not atomlib_xplor ):
        print "Initialize atomlib_xplor first please"
        return atomName

    if ( ( atomName == None ) or ( residueName == None ) ):
        return atomName 

    #   Although not correct we'll use it for now.
    #convert wildcards "%", "?", "*" to "#":
    atomName = re.sub('%', '#', atomName)
    atomName = re.sub('\?', '#', atomName)
    atomName = re.sub('\*', '#', atomName)
        
    #I. get a clean three-letter code and strip & uppercase the atomName
    residueCode = AminoAcid.AminoAcid(residueName)[1]    
    atomName = string.upper(string.strip(atomName))

    replacedic = atomlib_xplor.iupac_name
    
    if ( replacedic.has_key( residueCode ) ):  
        if ( replacedic[ residueCode ].has_key( atomName ) ):
            atomName = replacedic[ residueCode ][atomName]
        
    return atomName


def Convert_AtomName_IUPAC_2_BMRB_ChemShift(residueName, atomName):
    """
    convert an IUPAC atom name to BMRB nomenclature
    residueName: a string which contains full code, e.g. 'T  ' is not 'THR'
                 but is allowed for DADE and RADE (this needs work)
                 only the 20 common aminoacids are supported!
    atomName:    a string containing the atomnames, e.g. 'MG1'

    returns a string with the new atomname if changed or the original name
    
    e.g.        ALA MB  -> HB
            LEU MD1 -> HD1
            VAL QG  -> no change
            
    """

    # This code will exclude changes to random residue types
    # including the HN -> H
    if (( atomName == None ) or ( residueName == None )):
        return atomName

    #I. get a clean three-letter code and strip & uppercase the atomName
    residueCode = AminoAcid.AminoAcid(residueName)[1]
    atomName = string.upper(string.strip(atomName))
    
    #II. Set up the mapping table, this should of course be done only once
    ## and the results stored in a global parameter
    ## Jens, do you know how to set that up? I really prefer to have the 
    ## info outside the source code.

    replacedic = {
        'ALA': {'MB': 'HB'},
        'ILE': {'MD': 'HD1', 'MG': 'HG2'},
        'LEU': {'MD1':'HD1', 'MD2':'HD2'},
        'LYS': {'QZ': 'HZ'},    
        'MET': {'ME': 'HE'},    
        'THR': {'MG': 'HG2'},    
        'VAL': {'MG1':'HG1', 'MG2':'HG2'},
        'T  ': {'M7': 'H7'}
    }

    if ( replacedic.has_key( residueCode ) ):  
        if ( replacedic[ residueCode ].has_key( atomName ) ):
            atomName = replacedic[ residueCode ][ atomName ]
           
    atomName = Convert_AtomName_IUPAC_2_BMRB( atomName )
        
    return atomName


def Convert_AtomName_IUPAC_2_BMRB(atomName):
    """
    convert an IUPAC atom name to BMRB nomenclature
    returns a string with the new atomname if changed or the original name
    
    e.g.    HN  -> H
    """

    # This code will NOT exclude changes to random residue types
    # including the HN -> H
    if ( atomName == None ):
        return atomName
    
    #II. Set up the mapping table, this should of course be done only once

    replacedic = {'HN': 'H'}

    if ( replacedic.has_key( atomName ) ):
        atomName = replacedic[ atomName ]
    return atomName


def Convert_IUPAC_AtomName_2_PseudoAtomName(pseudoAtomType, residueName, atomName):
    """
    Converts an IUPAC atom name to the corresponding name for the pseudoatom
    if they are all defined and exist in the library.
    If the pseudoAtomType is None special behaviour might be coded later on.

    pseudoAtomType: a type of pseudoatom within the range of [0,6]
    residueName:    a string which contains full code, e.g. 'T  ' is not 'THR'
                        only the 20 common aminoacids are supported!
    atomName:       a string containing the atomnames, e.g. 'HG11'

    returns a string with the new atomname if changed or the original name
    
    e.g.    (2, ALA, HB1) -> MB1
    """

## See faster/cleaner code below
##    if ( pseudo_atom_lib.pseudo_atom_by_type.haskey( pseudoAtomType ) and
##         pseudo_atom_lib.pseudo_atom_by_type[        pseudoAtomType ].haskey( residueName ) and
##         pseudo_atom_lib.pseudo_atom_by_type[        pseudoAtomType ][        residueName ].haskey( atomName ) ):
##         
##        return pseudo_atom_lib.pseudo_atom_by_type[ pseudoAtomType ][ residueName ][ atomName ]
    
    try:
        tmpName = pseudo_atom_lib.pseudo_atom_by_type[ pseudoAtomType ][ residueName ][ atomName ]
    except KeyError:
        tmpName = atomName
    except IndexError:
        print "WARNING: programmer of this code (JFD) doesn't know what he's doing"
        tmpName = atomName
    except:
        print "WARNING: programmer of this code (JFD) doesn't know at all what he's doing"
        tmpName = atomName
    return tmpName


## Initialize an instance of the library map
## when this module gets loaded.
## This will give a traceback, if the library files can't be found!!!
atomlib_xplor   = AtomLib_Xplor(AtomLIBFN)
pseudo_atom_lib = PseudoAtomLib(PseudoLIBFN)
stereo_atom_lib = StereoAtomLib(StereoLIBFN)
    
###############################################################################

#test code:
if __name__ == "__main__":    
    print 'testing module:'
##    print atomlib_xplor.iupac_name["ALA"]
    print pseudo_atom_lib.pseudo_atom["TYR"]
    print stereo_atom_lib.stereo_atom["PHE"]
    print stereo_atom_lib.stereo_atom_by_type[6]
##    print pseudo_atom_lib.pseudo_atom_by_type[2]
##    print pseudo_atom_lib.pseudo_atom_by_type[2]["LEU"]["HD11"] # pseudo atom
##    print Convert_IUPAC_AtomName_2_PseudoAtomName( 2, "LEU", "HD11")
##    print Convert_PseudoAtomNames_CNS_2_IUPAC( "VAL", "HG1#" )
##    print Convert_AtomName_IUPAC_2_BMRB_ChemShift( "LEU", "MD1" )
##    print Convert_AtomName_IUPAC_2_BMRB_ChemShift( "ALA", "HN" )
##    print Convert_AtomName_IUPAC_2_BMRB( "HN" )
##    print '\ntest done. bye.'



