"""
some stdout messages for HADDOCK
"""

import sys
from datetime import datetime


def Help(helpString):
    """prints help to STDOUT"""
    print helpString
    
    
def StartHaddock(version):
    """first message when starting HADDOCK"""
    print """
##############################################################################
#                                                                            #
# Starting HADDOCK2.4                                                        #
#                                                                            #
#         N-components version of HADDOCK (current maximum is 20)            #
#                                                                            #
#   Copyright 2003-2020 Alexandre Bonvin, Utrecht University.                #
#   Originally adapted from Aria 1.2 from Nilges and Linge, EMBL.            #
#   All rights reserved.                                                     #
#   This code is part of the HADDOCK software and governed by its            #
#   license. Please see the LICENSE file that should have been included      #
#   as part of this package.                                                 #
#                                                                            #
##############################################################################
    """
    print 'Starting HADDOCK on:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print ' '
    print 'HADDOCK version:  ', version
    print 'Python version:', sys.version
    #print 'PYTHONPATH system variable contains:'
    #print sys.path

def StopHaddock():
    """last message when finishing HADDOCK"""
    print 78 * '#'
    print 'Finishing HADDOCK on: ', datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print 'Au revoir.'
    print 'Tot ziens.'
    print 'Bye bye.'
    sys.exit()


def Version():
    """just print out authors and version number to STDOUT"""
    print __author__, ' ' ,__version__
    
