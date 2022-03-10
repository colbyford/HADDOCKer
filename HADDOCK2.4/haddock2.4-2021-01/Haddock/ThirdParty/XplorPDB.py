"""
This module writes MMTK structures or PDBConfiguration objects out in
PDB nomenclature compatible with the CHARMM22 topology file (topallh22x.pro).
Peptide chains are recognized and C/N-terminii patches applied automatically.

So far, it's not particularly beautiful. Let me know what you think
at ehrlich@embl-heidelberg.de.

-Lutz 


* Features

-uses segID's
-patches termii
-does the hydrogen renumbering

* How to use it?

** Convert a standard PDB file

# read in a standard PDB file
from PDB import *
rs_gtp = PDBFile('../RasSos/ras_gtp_water_h.300debump.5000powell.pdb')
rs_gtp = rs_gtp.readSequenceWithConfiguration()

# write it out with the new XplorPDBFile objects (you can use a segid
import XplorPDB
rasF = XplorPDB.XplorPDBFile('../RasSos/ras_gtp_h.xplor.pdb','w',segID='rast')
rasF.writeConfiguration(rs_gtp[0])
rasF.close()


** Write out a MMTK protein object

# grab a MMTK protein

p = Protein('insulin')

import XplorPDB
of = XplorPDB.XplorPDBOutputFile('insulin.xplor.pdb',segID='insu')
of.write(p)
of.close()

* Caveats

-only single chains tested so far
-screws up files that were correct in the XPLOR sense

* Wishlist

-different XPLOR topology files (CHARMM19 etc)
-validity checks for atom nomenclature, with an interactive shell to suggest
 alternative names


$Id: XplorPDB.py,v 2.1 2010/02/10 16:13:25 abonvin Exp abonvin $
"""


import ChemicalObjects, Collection, Database, Units, Universe, Utility
import PDB



import string, re

FIRST = 1
LAST  = -1

def _dummyTranslate(atName,resName, firstLastFlag=None):
    return atName, resName
    
def _translateToXplorCHARMM19(atName,resName, firstLastFlag=None):
    atName,resName =  _translateToXplorCHARMM22(atName,resName, firstLastFlag)
    if resName=='HSP': resName = 'HIS'
    if resName=='HSD': resName = 'HIS'
    if atName =='HN': atName='H'
    if resName=='SER' and atName =='HG1':
        atName='HG'
    
    return atName, resName

def _translateToXplorCHARMM22(atName,resName, firstLastFlag=None):
    """
    given an atom and residue name, return the CHARMM22 atom name
    """
    atName = string.upper(atName)
    resName= string.upper(resName)


    """syntactic changes"""
    # turn  iHXj into HXji
    atName = re.sub('([0-9])(H[A-Z])([0-9])','\\2\\3\\1',atName)

    # turn  iHX into HXi
    atName = re.sub('([0-9])(H[A-Z])','\\2\\1',atName)

    # turn  iH  into Hi                               
    atName = re.sub('([0-9])H','H\\1',atName)


    """nomenaclature changes"""
    # water nomenclature
    resName = re.sub('WAT|HOH','TIP3',resName)
    if resName=='TIP3':
        atName = re.sub('OW?','OH2',atName)

    # hydrogens
    if atName=='H': atName='HN'
    atName = re.sub('HG2\Z','HG1',atName)
    atName = re.sub('HG3\Z','HG2',atName)


    
    if firstLastFlag:
        if firstLastFlag == LAST:
            # O->OT1, OXT->OT2
            atName = re.sub('O\Z','OT1',atName)
            atName = re.sub('OXT','OT2',atName)
            atName = re.sub('O1','OT1',atName)
            atName = re.sub('O2','OT2',atName)
        elif firstLastFlag == FIRST:
            atName = re.sub('HN','HT1',atName)            
            if resName not in ['WAT','HOH','TIP3']:
                # H[1-3] -> HT[1-3]
                atName = re.sub('\\bH([1-3])\Z','HT\\1',atName)
            
    if resName=='HIS': resName='HSD'

    """residue specific changes"""
    hRenumber = {'HB2':'HB1', 'HB3':'HB2'}
    resDict={
        'SER': {'HG':'HG1'},
        'GLY': {'HA':'HA1','HA2':'HA1','HA3':'HA2'},
        'GLU': hRenumber,
        'GLN': hRenumber,
        'ASP': hRenumber,
        'ASN': hRenumber,
        'PHE': hRenumber,
        'TYR': hRenumber,
        'TRP': hRenumber,
        'LEU': hRenumber,
        'MET': hRenumber,
        'HIS': hRenumber,
        'HSD': hRenumber,
        'HSE': hRenumber,
        'CYS': {'HB2':'HB1', 'HB3':'HB2', 'HG':'HG1'},
        'ARG': {'HB2':'HB1', 'HB3':'HB2', 'HD2':'HD1','HD3':'HD2'},
        'LYS': {'HB2':'HB1', 'HB3':'HB2','HD2':'HD1','HD3':'HD2', 'HE2':'HE1','HE3':'HE2'},
        'PRO': {'HB2':'HB1', 'HB3':'HB2','HD2':'HD1','HD3':'HD2' },
        'SER': {'HB2':'HB1', 'HB3':'HB2', 'HG':'HG1'},
        'ILE': {'HG12':'HG11','HG13':'HG12','HD11':'HD1','HD12':'HD2','HD13':'HD3','CD1':'CD'}
    }
    
    try:
        atD = resDict[resName]
        try:
            atName = atD[atName]
        except KeyError: pass
    except KeyError: pass


    return atName, resName
    
    

    
_translateToXplor = _translateToXplorCHARMM19
#_translateToXplor = _translateToXplorCHARMM22



class XplorPDBFile(PDB.PDBFile):

    def __init__(self, filename, mode='r', translateFunc=_translateToXplor, segID=''):
        PDB.PDBFile.__init__(self,filename, mode)
        if len(segID)>4:
            Utility.warning('chopping off given segID')
            segID = segID[:4]
            
        self.segID = segID #string.strip(segID)

        self._translate = translateFunc
    
    def writeConfiguration (self, data):
        ii = 0
        nData = len(data)
	for residue in data:
	    self.nextResidue(residue.name)
            # now this is ugly...
            if           ii==0: firstLast = FIRST
            elif ii==nData - 1: firstLast = LAST
            else:               firstLast = None
            ii = ii + 1
	    for atom in residue.atom_list:
                name, resName = self._translate(atom.name, residue.name, firstLast)
                self.resid = resName
		self.writeAtom(name, atom.position, atom.occupancy,
			       atom.temp_factor, atom.type() == 'HETATM')
                
    def writeAtom(self, name, position, occupancy=0., temp_factor=0.,
		  het_flag = 0):
        import string
	name = string.upper(name)
	self.atom_num = self.atom_num + 1
	if het_flag:
	    format = 'HETATM%5d '
	else:
	    format = 'ATOM  %5d '
	outStr = format % (self.atom_num)
        
        if len(name) < 4 and name[0] not in string.digits:
	    name = ' ' + name

        outStr = outStr + string.ljust(name,4)[0:4] + ' ' + string.ljust(self.resid,4)[0:4] 
        outStr = outStr + self.chain_id
        outStr = outStr + ('%4d    %8.3f%8.3f%8.3f' %\
                           (self.rel_res_num,position[0], position[1], position[2]))
        
        #self.file.write(string.ljust(name,4)[0:4] + ' ')
	#self.file.write(string.ljust(self.resid,3)[0:3] + ' ')
	#self.file.write(self.chain_id)
	#self.file.write('%4d    ' % self.rel_res_num)
	#self.file.write('%8.3f' % position[0])
	#self.file.write('%8.3f' % position[1])
	#self.file.write('%8.3f' % position[2])

        outStr = outStr + '%6.2f%6.2f' %( occupancy, temp_factor)
        #self.file.write('%6.2f' % occupancy)
	#self.file.write('%6.2f' % temp_factor)

        outStr = string.rstrip(outStr)
        nOut = len(outStr)
        # pad to the right, XPLOR segID goes into columnds 73:76 (starting count with 1)
        outStr = outStr + ((72-nOut)*' ') + self.segID
	self.file.write(outStr + '\n')


import ConfigIO
class XplorPDBOutputFile(ConfigIO.PDBOutputFile):

    def __init__(self, filename, segID='', translateFunc=_translateToXplor):
	self.file = XplorPDBFile(filename, 'w', segID=segID)
	self.warning = 0
	self.atom_sequence = []
        self._translate = translateFunc

    def write(self, object, configuration = None, tag = None):
	if not ChemicalObjects.isChemicalObject(object):
	    for o in object:
		self.write(o, configuration)
	else:
	    toplevel = tag is None
	    if toplevel:
		tag = Utility.uniqueAttribute()
	    if hasattr(object, 'pdbmap'):
                seqNum = object.sequence_number
                #
                # determine whether we're first or last in the chain
                #
                firstLast = None
                if seqNum == 1:
                    firstLast = FIRST
                else:
                    parentObject = object.parent
                    try:
                        nextObj = parentObject[seqNum] # indices start at 0, but seqNum at 1
                    except IndexError:
                        # this means there's no next neighbor, so we're last
                        # yuk, this is really awful
                        firstLast = LAST
                
		for residue in object.pdbmap:                    
		    self.file.nextResidue(residue[0])
		    for atom_name, atom in residue[1].items():
			atom = object.getAtom(atom)
			p = atom.position(configuration)
			if Utility.isDefinedPosition(p):
			    try: occ = atom.occupancy
			    except AttributeError: occ = 0.
			    try: temp = atom.temperature_factor
			    except AttributeError: temp = 0.

                            atom_name, resName = self._translate(atom_name,self.file.resid, firstLast)
                            self.file.resid = resName
			    self.file.writeAtom(atom_name, p/Units.Ang,
						occ, temp)
			    self.atom_sequence.append(atom)
			else:
			    self.warning = 1
			setattr(atom, tag, None)
	    else:
		if hasattr(object, 'is_protein'):
		    for chain in object:		    
			self.file.nextChain()
			self.write(chain, configuration, tag)
		    self.file.noChain()
		elif hasattr(object, 'molecules'):
		    for m in object.molecules:
			self.write(m, configuration, tag)
		elif hasattr(object, 'groups'):
		    for g in object.groups:
			self.write(g, configuration, tag)
	    if toplevel:
		for a in object.atomList():
		    if not hasattr(a, tag):
			self.write(a, configuration, tag)
		    delattr(a, tag)

