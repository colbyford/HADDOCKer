"""
A module to delete all cns- and xplor-type comments from any input file.
The following comments are thrown out:
    ! blabla until end of line
    # blabla until end of line
    {blabla}
    {bla{bla}bla}
Don't use (this will cause problems):
    {bla!bla}
    {bla#bla}
    
    
NOTE:
    -curly braces after '!' or '#' (until lineend) are not interpreted as the
     beginning of another comment
    -be careful: '!' and '#' within curly braces are interpreted as 'comment
     until lineend'.

EXAMPLE:
    this tiny cns script (let's call it test.cns):
        evaluate ($i = 1)
        {
        evaluate ($j = {2} 3)
        }
        {evaluate ($k = 4)}
        evaluate ($l = 5) ! braces like { after exclamationmark don't count
        display $i
        display $l
        stop
    can be parsed with:
    from DeleteComments import *
    GetFile('/home/linge/tmp/test.cns', '/home/linge/tmp/test.without')
    it will look like:
        evaluate ($i = 1)

                          
        evaluate ($l = 5)
        display $i
        display $l
        stop

    this example shows that linebreaks before and after the { bla } are not removed.
"""
__author__   = "$Author: abonvin $"
__revision__ = "$Revision: 2.1 $"
__date__     = "$Date: 2010/02/10 16:11:47 $"


import re, string

def GetFile(input, output):
    """
    reads in a file
    deletes all comments
    returns an outputfile with the contents of the original file with
    linebreaks \012 and without comments
    """
    getback = GetString(input)
    print 'writing the output to', output
    outhandle = open(output, 'w')
    outhandle.write(getback)
    outhandle.close()
##    print getback #test

def GetString(input):
    """
    reads in a file
    deletes all comments
    returns a string with the contents of the whole file with
    linebreaks \012 and without comments
    """
    #message:
    print 'reading', input
    print 'deleting comments'
    
    #opening the filehandles, get one big string:
    inhandle = open(input)
    stuff = string.join(inhandle.readlines(), '')
    
    #compile some patterns (? for non-greedy, re.DOTALL for multiline):
    openbr = re.compile('{')
    closebr = re.compile('}')
    openclosemin = re.compile('{.*?}', re.DOTALL)
    openopenmin = re.compile('{.*?{', re.DOTALL)

    #delete the comments after ! and # until the line end:
    stuff = re.sub('!.*\012', '\012', stuff)
    stuff = re.sub('#.*\012', '\012', stuff)

    #initialize the start position:
    start = 0
    
    #loop, until there are no braces pairs left:
    while (openbr.search(stuff) != None) and (closebr.search(stuff) != None):
        #search for the patterns:
        openfound = openbr.search(stuff, start)
        closefound = closebr.search(stuff, start)
        ocminfound = openclosemin.search(stuff, start)
        oominfound = openopenmin.search(stuff, start)
        if (not ocminfound == None) and (not oominfound == None):
            #first look for normal braces { bla }:
            if ocminfound.span()[1] < oominfound.span()[1]:
                stuff = stuff[:start] + openclosemin.sub('', stuff[start:], 1)
                #reset start position to 0 after substitution:
                start = 0
            #second look for nested braces { bla { bla } bla}:
            else:
                #choose a higher start position:
                start = ocminfound.span()[0] + 1
        #for the last braces pairs:
        elif (not ocminfound == None) and (oominfound == None) and\
             (not closefound == None):
            stuff = openclosemin.sub('', stuff, 1)
                
    #write warning, if there are still braces left:
    if openbr.search(stuff) != None:
        print 'WARNING: there are more { than }'
    if closebr.search(stuff) != None:
        print 'WARNING: there are more } than {'
    inhandle.close()
    return stuff

