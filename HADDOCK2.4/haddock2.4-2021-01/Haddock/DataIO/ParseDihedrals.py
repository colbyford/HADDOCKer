"""
generate some statistics for the dihedrals restraints violations
from the CNS .out files

jens@linge.de
29-10-2001
"""

import re, string, sys


def parseDihedralsFile(fileName):
    """
    starting from a filename
    """
    inHandle = open(fileName, 'r')
    return parseDihedralsString(inHandle)
    
def parseDihedralsString(inputStream):
    """
    parses an .out file with the dihedral violations
    """
    #compile some patterns:
    dihedralLineRE = re.compile('Dihedral=\s+(\S+)\s+Energy=\s+(\S+)\s+C=\s+(\S+)\s+Equil=\s+(\S+)\s+Delta=\s+(\S+)\s+')    
#    totalNumberRE = re.compile('\sTotal\s*number\s*of\s*dihedral\s*angle\s*restraints=\s+(\S+)')
    numberViolationsRE = re.compile('Number\s*of\s*violations\s*greater\s*than\s+(\S+)\s+ (\S*)')
    equalsRE = re.compile('\s========================================')

    #empty default values:
    dihedralsString = '#D_experiment\tD_average\tViol\tEnergy\tN_res1\tRes1\tAtom1\tN_res2\tRes2\tAtom2\tN_res3\tRes3\tAtom3\tN_res4\tRes4\tAtom4\n'
    withinAnalysis = 0
    residuenumber1 = ''
    aminoacid1 = ''
    atomname1 = ''
    residuenumber2 = ''
    aminoacid2 = ''
    atomname2 = ''
    residuenumber3 = ''
    aminoacid3 = ''
    atomname3 = ''
    residuenumber4 = ''
    aminoacid4 = ''
    atomname4 = ''
    dexp = ''
    dave = ''
    viol = '0'
    noViol = '0'
    energy = ''
     
    for line in inputStream.readlines():
##         if withinAnalysis: #test
##             print '###' + str(withinAnalysis) + ' ' + line #test
        dihedralLineSE = dihedralLineRE.search(line)
#        totalNumberSE = totalNumberRE.match(line)
        numberViolationsSE = numberViolationsRE.search(line)
        equalsSE = equalsRE.match(line)
        if equalsSE:
            withinAnalysis = 1

        if withinAnalysis == 2 and len(line) > 2:
            residuenumber1, aminoacid1, atomname1 = string.split(line)
        elif withinAnalysis == 3 and len(line) > 2:
            residuenumber2, aminoacid2, atomname2 = string.split(line)
        elif withinAnalysis == 4 and len(line) > 2:
            residuenumber3, aminoacid3, atomname3 = string.split(line)
        elif withinAnalysis == 5 and len(line) > 2:
            residuenumber4, aminoacid4, atomname4 = string.split(line)
            
        if withinAnalysis == 6 and dihedralLineSE:
#            print '###dihedralsLineSE' #test
            dexp = dihedralLineSE.group(4) + '  '
            dave = dihedralLineSE.group(1) + '  '
            viol = dihedralLineSE.group(5)
            energy = dihedralLineSE.group(2)
            
##         if numberViolationsSE:
## #            print '###numberViolationsSE' #test
##             noViol = numberViolationsSE.group(2)
##             if not noViol:
##                 noViol='0'

            dihedralsString = dihedralsString + "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (dexp,dave,viol,energy,\
                                                                                                                                                         residuenumber1, aminoacid1, atomname1,\
                                                                                                                                                         residuenumber2, aminoacid2, atomname2,\
                                                                                                                                                         residuenumber3, aminoacid3, atomname3,\
                                                                                                                                                         residuenumber4, aminoacid4, atomname4)
            withinAnalysis = 0

        if withinAnalysis:
            withinAnalysis = withinAnalysis + 1

    return dihedralsString


###############################################################################
if __name__ == '__main__':
    print 'testing...'
    testString = """
 CNSsolve>
 CNSsolve>   print thresh=$cutdih cdih
 Total number of dihedral angle restraints=    64
  overall scale =  200.0000
 ========================================
      30   ILE  N
      30   ILE  CA
      30   ILE  C
      31   VAL  N
 Dihedral=  159.572  Energy=    0.017 C=    1.000 Equil=  132.000 Delta=   -7.572
 Range=  20.000 Exponent=  2
 Number of dihedral angle restraints=   64
 Number of violations greater than    5.000:    
 RMS deviation=   1.226
 CNSsolve>   evaluate ($rms_dih = $result)
TE: symbol $NSTRUC1 set to    9.00000     (real)
 CNSsolve>   end if 
 CNSsolve> 
 CNSsolve>   print thresh=$cutdih cdih 
 Total number of dihedral angle restraints=    64
  overall scale =  200.0000
 ========================================
      48   ARG  N   
      48   ARG  CA  
      48   ARG  C   
      49   LEU  N   
 Dihedral=  157.877  Energy=    0.011 C=    1.000 Equil=  128.000 Delta=   -5.877
 Range=  24.000 Exponent=  2
 Number of dihedral angle restraints=   64
 Number of violations greater than    5.000:     1
 RMS deviation=   0.968
 CNSsolve>   evaluate ($rms_dih = $result) 
 EVALUATE: symbol $RMS_DIH set to   0.968010     (real)
 CNSsolve>   evaluate ($sum_rms_dih = $sum_rms_dih + $rms_dih ) 
Ssolve> 
 CNSsolve>   print thresh=$cutdih cdih 
 Total number of dihedral angle restraints=    62
  overall scale =  200.0000
 ========================================
      23   ASP  C   
      24   LYS  N   
      24   LYS  CA  
      24   LYS  C   
 Dihedral=  -99.326  Energy=    0.010 C=    1.000 Equil= -135.000 Delta=   -5.674
 Range=  30.000 Exponent=  2
 ========================================
      45   ASP  N   
      45   ASP  CA  
      45   ASP  C   
      46   ARG  N   
 Dihedral=   96.494  Energy=    0.022 C=    1.000 Equil=  135.000 Delta=    8.506
 Range=  30.000 Exponent=  2
 Number of dihedral angle restraints=   62
 Number of violations greater than    5.000:     2
 RMS deviation=   1.586
 CNSsolve>   evaluate ($rms_dih = $result) 
 EVALUATE: symbol $RMS_DIH set to    1.58645     (real)
 """
    print '\ninput string:'
    print testString
    print '\noutput string:'
    import StringIO
    testStringIO = StringIO.StringIO(testString)
    print parseDihedralsString(testStringIO)
    print '\nciao.'
