"""
this module is used to check if a proton atomname can fit to a
given heteronucleus atomname

it's basically a dictionary to find the corresponding protons
to heteronuclei

I use it for reading in the XEASY .assign files.
"""
__author__   = "$Author: abonvin $"
__revision__ = "$Revision: 2.1 $"
__date__     = "$Date: 2010/02/10 16:12:01 $"

import string


def checkProton(heteronucleus, proton):
    """
    input: two strings which contain atomnames
    returns 1 if the proton may belong to the heteronucleus
    returns 0 if the proton doesn't fit to the heteronucleus

    NOTE: if in doubt, always returns 1
    """
    #define the dictionary:
    atomDic = {'CA': 'HA',\
           'CB': 'HB',\
           'CG': 'HG',\
           'CD': 'HD',\
           'CE': 'HE',\
           'N': 'HN'}
    #uppercase:
    heteronucleus = string.upper(heteronucleus)
    proton = string.upper(proton)
    #use only the first two characters:
    if len(heteronucleus) > 1:
        heteronucleus = heteronucleus[:2]
    if len(proton) > 1:
        proton = proton[:2]
    #does it fit?:
    if atomDic.has_key(heteronucleus):
        if atomDic[heteronucleus] != proton:
            return 0
    #by default, if in doubt...:
    return 1

