"""
Comparisons.py

CmpAttr is a callable class which can be used for sorting like the
standard cml() built-in function

CmpComposite is a callable class for sorting which can take a list
of CmpAttr classes
"""
__author__   = "$Author: abonvin $"
__revision__ = "$Revision: 2.1 $"
__date__     = "$Date: 2010/02/10 16:12:01 $"

import string

class CmpAttr:
    """
    sorting after a given attribute

    when calling this object:
        numeric = 2     used for floats
        numeric = 1     used for integers
        numeric = None  used for strings (default)
    """
    def __init__(self, attr, numeric = None):
        self.attr = attr
        self.numeric = numeric

    def __call__(self, x, y):
        if self.numeric == 1:
            if getattr(x, self.attr) == None or getattr(y, self.attr) == 0:
                return 0
            return cmp(int(getattr(x, self.attr)),\
                       int(getattr(y, self.attr)))
        elif self.numeric == 2:
            if getattr(x, self.attr) == None or getattr(y, self.attr) == 0:
                return 0
            return cmp(float(getattr(x, self.attr)),\
                       float(getattr(y, self.attr)))
        else:
            return cmp(getattr(x, self.attr), getattr(y, self.attr))

class CmpComposite:
    """
    takes a list of compare functions and sorts in that order
    """
    def __init__(self, *comparers):
        self.comparers = comparers
    def __call__(self, a, b):
        for cmp in self.comparers:
            c=cmp(a,b)
            if c:
                return c
        return 0


class CmpColumn:
    """
    sorts on an index of a sequence
    useful for sorting of columns and rows in tables
    """
    def __init__(self, column):
        self.column = column
    def __call__(self, a, b):
        return cmp(a[self.column], b[self.column])


#test code:
if __name__ == "__main__":
    print 'testing module Comparisons.py:'
    class Spam:
        def __init__(self, spam, eggs):
            self.spam = spam
            self.eggs = eggs
        def __repr__(self):
            return 'Spam(s=%s,e=%s)' %(repr(self.spam), repr(self.eggs))
    a = [Spam(9,3), Spam(1,4), Spam(4,6), Spam(4,4)]
    print 'sorting: 1. after spam and 2. after eggs'
    print 'before sorting: ', a
    a.sort(CmpComposite(CmpAttr('spam'), CmpAttr('eggs')))
    print 'after sorting:  ', a
    
