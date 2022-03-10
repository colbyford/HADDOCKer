# Text files with automatic (un)compression
#
# Written by: Konrad Hinsen <hinsenk@ere.umontreal.ca>
# Last revision: 1996-11-8
# 

"""This module defines a class TextFile whose instances can be
accessed like normal file objects (i.e. by calling readline(),
readlines(), and write()), but can also be used as line iterators
in for loops.

The class TextFile also handles compression transparently, i.e. it is
possible to read lines from a compressed text file as if it were not
compressed.  Compression is deduced from the file name suffixes '.Z'
(compress/uncompress) and '.gz' (gzip/gunzip).

Finally, TextFile objects accept file names that start with '~' or
'~user' to indicate a home directory.
"""

import os

class TextFile:

    def __init__(self, filename, mode = 'r'):
        filename = os.path.expanduser(filename)
        if mode == 'r':
            if not os.path.exists(filename):
                raise IOError, (2, 'No such file or directory: ' + filename)
            if filename[-2:] == '.Z':
                self.file = os.popen("uncompress -c " + filename, mode)
            elif filename[-3:] == '.gz':
                self.file = os.popen("gunzip -c " + filename, mode)
            else:
                self.file = open(filename, mode)
        elif mode == 'w':
            if filename[-2:] == '.Z':
                self.file = os.popen("compress > " + filename, mode)
            elif filename[-3:] == '.gz':
                self.file = os.popen("gzip > " + filename, mode)
            else:
                self.file = open(filename, mode)
        else:
            raise IOError, (0, 'Illegal mode')

    def __del__(self):
        self.close()

    def __getitem__(self, item):
        line = self.file.readline()
        if not line:
            raise IndexError
        return line

    def readline(self):
        return self.file.readline()

    def readlines(self):
        return self.file.readlines()

    def write(self, data):
        self.file.write(data)

    def writelines(self, list):
        for line in list:
            self.file.write(line)

    def close(self):
        self.file.close()

