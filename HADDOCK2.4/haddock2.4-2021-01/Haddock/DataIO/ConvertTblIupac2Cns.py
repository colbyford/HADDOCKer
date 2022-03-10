"""
converts CNS ASSIgn files from IUPAC to CNS and vice versa
use it for the chemical shift assignment files

25.8.99 @Utrecht
linge@embl-heidelberg.de
"""
from Haddock.Nomenclature import Nomenclature
from Haddock.DataIO import SequenceList
import re, string, sys

if len(sys.argv) != 3:
    print 'USAGE: ConvertTblIupac2Cns.py tblName 3lettercodeSeqFile'
    print 'the cns .tbl file must use the ASSign statement'
    print 'the sequence file may contain only 3-letter code amino acids'
    sys.exit()

tblInFile = sys.argv[1]
seqFile = sys.argv[2]

print 'working on', tblInFile

#read the sequence:
SL=SequenceList.SequenceList()
SL.ReadSeq(seqFile)
aaList = SL.aalist

#read the .tbl file, write to '_new' file:
inHandle = open(tblInFile)
outName = tblInFile + '_new'
outHandle = open(outName, 'w')

#compile the pattern:
namePA = re.compile('name\s+(\S+)\s*\)', re.IGNORECASE)
residPA = re.compile('resid\s+(\S+)\s', re.IGNORECASE)
for eachLine in inHandle.readlines():
    nameSE = namePA.search(eachLine)
    residSE = residPA.search(eachLine)
    if nameSE and residSE:
        residNO = int(residSE.group(1)) - 1
#print aaList[residNO],nameSE.group(1) #test
        eachLine = namePA.sub('name ' + Nomenclature.ConvertCnsProtonNames(aaList[residNO],nameSE.group(1)) + ')', eachLine)
    outHandle.write(eachLine)
print 'wrote to file', outName
inHandle.close()
outHandle.close()
