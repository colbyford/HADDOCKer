"""
ShellEnv.py

a module to handle all the shell variables
shell variables are used to communicate with the CNS protocols
they are some sort of global variables (ugly!) which are used to set the
directories etc.
the protocols in the /haddock/protocols directory use shell variables quite often
"""
__author__   = "$Author: abonvin $"
__revision__ = "$Revision: 2.1 $"
__date__     = "$Date: 2010/02/10 16:11:34 $"

import os



def SetEnvironment(HaddockDir, cnsExe, currit, newitDir, previtDir, runDir,\
                   tempTrashDir):
    """
    sets all the shell environment variables for the CNS protocols
    """
    dictionary = {'HADDOCK': HaddockDir,\
                  'cns': cnsExe,\
                  'CURRIT': currit,\
                  'NEWIT': newitDir,\
                  'PREVIT': previtDir,\
                  'RUN': runDir,\
                  'TEMPTRASH': tempTrashDir}
    for x in dictionary.keys():
        os.putenv(x, dictionary[x])
