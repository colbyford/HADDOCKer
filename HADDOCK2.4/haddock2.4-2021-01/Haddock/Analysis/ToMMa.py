from types import *
from Numeric import ArrayType
import string
"""
ToMMa(list) returns a string with a MMa formatted list
{{a,b},{b,c}} - uses str representation of passed objects
"""
def ToMMa(list):
    rval=[]
    for elem in list:
        if type(elem)==ListType or type(elem) == ArrayType:
           rval.append(ToMMa(elem))
        elif type(elem) == StringType:
            rval.append('\"'+elem+'\"')
        else:
            rval.append(str(elem))
    return '{'+string.join(map(str,rval),',')+'}'



