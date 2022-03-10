"""
ParsePath.py

some procedures for file and directory names

"""
__author__   = "$Author $"
__revision__ = "$Revision $"
__date__     = "$Date $"

import os, string

def GetTail(path, recursive=False):
    """
    parse the tail (directory or file) out of an absolute path
    usage: dir = GetTail(fullpath)
    e.g. '/home/nmr/il4/' will be ' il4'
    if path is empty, an empty string is returned
    if path is root ('/'), root is returned
    if path is None, None is returned
    """
    if not path: return None
    relative_path = path.startswith(".")     
    if string.strip(path) == '/':  
        return '/'              # for root
    if (path[-1] == '/'):
        path = path [:-1]       # get rid of trailing slashes
    pathlist = os.path.split(path)
    ret = pathlist[1]
    if relative_path and not recursive:
      return GetTail(os.getcwd() + "/" + path[2:], True)
    return ret


def DelTrailSlash(path):
    """gets rid of trailing slahes, if there are any"""
    if ((path[-1] == '/') and (string.strip(path) != '/')):
        path = path [:-1]
    return path


def TooLong(path):
    if len(path) > 78:
        print 'WARNING: the following path is too long:'
        print path
    
