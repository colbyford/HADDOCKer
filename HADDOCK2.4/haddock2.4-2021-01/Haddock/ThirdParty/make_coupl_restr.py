"""

Author: Niklas Blomberg, EMBL 1999
Last Update: $Date: 2010/02/10 16:13:25 $


$Header: /Users/abonvin/haddock2.1/Haddock/ThirdParty/RCS/make_coupl_restr.py,v 2.1 2010/02/10 16:13:25 abonvin Exp abonvin $
Niklas Blomberg
"""

__version__ = "$Revision: 2.1 $"


def main(fname,aninumber):
    """
    main()
    Module mainline (for standalone execution)
    """
    

    import string
    aninumber=int(aninumber)
    f=open(fname,'r')
    data=f.readlines()
    f.close()
    for item in data:
        if string.find(item,'#') == -1:
            line=string.split(item)
            res,coup=int(line[0]),float(line[1])
            print ('ASSI \t(resid %i and name OO)(resid %i and name Z) \n\t(resid %i and name X )(resid %i and name Y  ) \n\t(resid %i and name N )(resid %i and name HN ) \t%3.2f  0.50 \n ' % (aninumber,aninumber,aninumber,aninumber,res,res,coup))

    return
fname='/nmr/nilges6/blomberg/easy/unc89/hnhaj_couplings'

if __name__ == "__main__":
    import sys
    try:
        main(sys.argv[1],sys.argv[2])
    except:
        print 'Usage: python make_coupl_restr restraintfile resid_ani'
