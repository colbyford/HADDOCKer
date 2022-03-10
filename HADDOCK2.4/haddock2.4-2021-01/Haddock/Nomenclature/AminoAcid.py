"""
A module to deal with aminoacids in 3- or 1-letter code
"""
__author__   = "$Author: abonvin $"
__revision__ = "$Revision: 2.1 $"
__date__     = "$Date: 2010/02/10 16:12:48 $"


def AminoAcid(input):
    """    
    INPUT:  a string containing an amino acid in 3- or 1-letter code
            (only the 20 common amino acids can be converted)
            upper- or lowercase; spaces, tabs and linebreaks are neglected
    OUTPUT: returns a list of strings with the 1-letter-code as element 0,
            the 3-letter-code as element 1 and the name as element 2.
            all returned 1- and 3-letter codes are uppercase, the name
            is lowercase.
    if the input is not a common amino acid, the elements 0 and 1 will be
    returned empty with the input string as third element.
    """
    import string
    one2all ={'A': ('A', 'ALA', 'alanine'),
              'R': ('R', 'ARG', 'arginine'),
              'N': ('N', 'ASN', 'asparagine'),
              'D': ('D', 'ASP', 'aspartic acid'),
              'C': ('C', 'CYS', 'cysteine'),
              'Q': ('Q', 'GLN', 'glutamine'),
              'E': ('E', 'GLU', 'glutamic acid'),
              'G': ('G', 'GLY', 'glycine'),
              'H': ('H', 'HIS', 'histidine'),
              'I': ('I', 'ILE', 'isoleucine'),
              'L': ('L', 'LEU', 'leucine'),
              'K': ('K', 'LYS', 'lysine'),
              'M': ('M', 'MET', 'methionine'),
              'F': ('F', 'PHE', 'phenylalanine'),
              'P': ('P', 'PRO', 'proline'),
              'S': ('S', 'SER', 'serine'),
              'T': ('T', 'THR', 'threonine'),
              'W': ('W', 'TRP', 'tryptophan'),
              'Y': ('Y', 'TYR', 'tyrosine'),
              'V': ('V', 'VAL', 'valine')}
    three2all = {'ALA': ('A', 'ALA', 'alanine'),
                 'ARG': ('R', 'ARG', 'arginine'),
                 'ASN': ('N', 'ASN', 'asparagine'),
                 'ASP': ('D', 'ASP', 'aspartic acid'),
                 'CYS': ('C', 'CYS', 'cysteine'),
                 'GLN': ('Q', 'GLN', 'glutamine'),
                 'GLU': ('E', 'GLU', 'glutamic acid'),
                 'GLY': ('G', 'GLY', 'glycine'),
                 'HIS': ('H', 'HIS', 'histidine'),
                 'ILE': ('I', 'ILE', 'isoleucine'),
                 'LEU': ('L', 'LEU', 'leucine'),
                 'LYS': ('K', 'LYS', 'lysine'),
                 'MET': ('M', 'MET', 'methionine'),
                 'PHE': ('F', 'PHE', 'phenylalanine'),
                 'PRO': ('P', 'PRO', 'proline'),
                 'SER': ('S', 'SER', 'serine'),
                 'THR': ('T', 'THR', 'threonine'),
                 'TRP': ('W', 'TRP', 'tryptophan'),
                 'TYR': ('Y', 'TYR', 'tyrosine'),
                 'VAL': ('V', 'VAL', 'Valine')}
    cleanInput = string.strip(string.upper(input))
    if len(cleanInput) == 1:
        if one2all.has_key(cleanInput):
            return one2all[cleanInput]
    elif len(cleanInput) == 3:
        if three2all.has_key(cleanInput):
            return three2all[cleanInput]
    return ['', '', input]

#test:
if __name__ == "__main__":
    import sys
    try:
        aminoacidin = sys.argv[1]
    except IndexError:
        print 'You have to give an amino acid in 1- or 3-notation as an argument.'
        print 'e.g.  AminoAcid.py trp'
        sys.exit()
    print 'converting: "' + aminoacidin + '"'
    aminoacidout = AminoAcid(aminoacidin)
    print aminoacidout
    sys.exit()
