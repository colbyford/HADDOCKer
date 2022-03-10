"""
CallCnsProtocols.py

some functions to call single CNS protocols

generateA.inp
generateB.inp
merge_topologies.inp

"""
__author__   = "$Author: abonvin $"
__revision__ = "$Revision: 2.1 $"
__date__     = "$Date: 2010/02/10 16:11:34 $"

import os

def GeneratePsfA(cnsExe, protocols, begin):
    """
    generates PSF file, the shell paths have to be set properly before
    """
    print 'generating PSF and PDB files of protein A'
    whatToDo = cnsExe + ' < ' + protocols + '/generateA.inp >! ' + begin + \
               '/generateA.out' 
    os.system(whatToDo)
    

def GeneratePsfB(cnsExe, protocols, begin):
    """
    generates PSF file, the shell paths have to be set properly before
    """
    print 'generating PSF and PDB files of protein B'
    whatToDo = cnsExe + ' < ' + protocols + '/generateB.inp >! ' + begin + \
               '/generateB.out' 
    os.system(whatToDo)
    

def MergeTopolodies(cnsExe, protocols, begin):
    """
    merge topology and coordinate files, the shell paths have to be set
    properly before
    """
    print 'merging topologies and coordinate files'
    whatToDo = cnsExe + ' < ' + protocols + '/merge_topologies.inp >! ' + \
               begin + '/merge_topologies.out'
    os.system(whatToDo)
