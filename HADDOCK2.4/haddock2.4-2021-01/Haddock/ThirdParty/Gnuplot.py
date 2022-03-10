#!/usr/local/bin/python -t
# $Id: Gnuplot.py,v 2.1 2010/02/10 16:13:25 abonvin Exp abonvin $

# A pipe-based interface to the gnuplot plotting program.  To obtain
# gnuplot itself, see <http://www.cs.dartmouth.edu/gnuplot_info.html>.

# Written by Michael Haggerty <mhagger@blizzard.harvard.edu>.
# Inspired by and partly derived from an earlier version by Konrad
# Hinsen <hinsen@ibs.ibs.fr>.

# This module is provided with no warranties whatsoever.  However, if
# you find a problem or have a suggestion, please let me know at
# <mhagger@blizzard.harvard.edu>.  Any feedback is welcome.

# For information about how to use this module, see the documentation
# string for class Gnuplot, and the test code at the bottom of the
# file.  You can run the test code by typing `python Gnuplot.py'

# You should import this file with `import Gnuplot', not with `from
# Gnuplot import *'; otherwise you will have problems with conflicting
# names (namely the Gnuplot module name conflicting with the Gnuplot
# class name.

# Features:
#  +  A gnuplot session is an instance of class `Gnuplot', so multiple
#     sessions can be open at once:
#         g1 = Gnuplot.Gnuplot(); g2 = Gnuplot.Gnuplot()
#  +  The implicitly-generated gnuplot commands can be stored to a file
#     instead of executed immediately:
#         g = Gnuplot.Gnuplot("commands.gnuplot")
#     The file can then be run later with gnuplot's `load' command.
#     Note, however, that this option does not cause the life of any
#     temporary data files to be extended.
#  +  Can pass arbitrary commands to the gnuplot command interpreter:
#         g("set pointsize 2")
#  +  A Gnuplot object knows how to plot three types of `PlotItem':
#     `Data', `File', and `Func'tion.  See those classes for
#     information.
#  +  Any PlotItem can have optional `title' and/or `with' suboptions.
#  +  Builtin PlotItem types:
#      *  Data(array1) -- data from a Python list or NumPy array
#         (permits additional option `cols')
#      *  File("filename") -- data from an existing data file (permits
#         additional option `using')
#      *  Func("exp(4.0 * sin(x))") -- functions (passed as a string
#         for gnuplot to evaluate)
#  +  PlotItems are implemented as objects that can be assigned to
#     variables (including their options) and plotted
#     repeatedly---this also saves much of the overhead of plotting
#     the same data multiple times.
#  +  Communication of data between python and gnuplot is via
#     temporary files, which are deleted automatically when their
#     associated PlotItem is deleted.  (Communication of commands is
#     via a pipe.)  The PlotItems currently in use by a Gnuplot object
#     are stored in an internal list so that they won't be deleted
#     prematurely.
#  +  Can use `replot' method to add datasets to an existing plot.
#  +  Can make persistent gnuplot windows by using the constructor
#     option `persist=1'.  (`persist' is no longer the default.)  Such
#     windows stay around even after the gnuplot program is exited.
#     Note that only newer version of gnuplot support this option.
#  +  Plotting to a postscript file is via new `hardcopy' method,
#     which outputs the currently-displayed plot to either a
#     postscript printer or to a postscript file.
#  +  There is a `plot' command which is roughly compatible with the
#     command from the old Gnuplot.py.
#
# Restrictions:
#  -  Relies on the Numeric Python extension.  This can be obtained
#     from LLNL (See ftp://ftp-icf.llnl.gov/pub/python/README.html).
#     If you're interested in gnuplot, you would probably also want
#     NumPy anyway.
#  -  Probably depends on a unix-type environment.  Anyone who wants
#     to remedy this situation should get in contact with me.
#  -  Only a small fraction of gnuplot functionality is implemented as
#     explicit Gnuplot method functions.  However, you can give
#     arbitrary commands to gnuplot manually; for example:
#         g = Gnuplot.Gnuplot()
#         g('set data style linespoints')
#         g('set pointsize 5')
#     etc.  I might add a more organized way of setting arbitrary
#     options.
#  -  Only 2-d plots are supported so far.
#  -  There is no provision for missing data points in array data
#     (which gnuplot would allow by specifying `?' as a data point).
#     I can't think of a clean way to implement this; maybe one could
#     use NaN for machines that support IEEE floating point.
#  -  There is no supported way to change the plotting options of
#     PlotItems after they have been created.
#  -  The object-oriented interface doesn't automatically plot
#     datasets column-by-column using 1:2, 1:3, 1:4, etc as did the
#     old version of Gnuplot.py.  Instead, make a temporary data file
#     then plot that file multiple times with different `using='
#     options:
#         a = Gnuplot.TemparrayFile(array_nx3)
#         g.plot(Gnuplot.File(a, using=(1,2)), Gnuplot.File(a, using=(1,3)))
#  -  Does not support parallel axis plots, as did the old Gnuplot.py.
#
# Bugs:
#  -  No attempt is made to check for errors reported by gnuplot (but
#     they will appear on stderr).
#  -  All of these classes perform their resource deallocation when
#     __del__ is called.  If you delete things explicitly, there will
#     be no problem.  If you don't, an attempt is made to delete
#     remaining objects when the interpreter is exited, but this is
#     not completely reliable, so sometimes temporary files will be
#     left around.  If anybody knows how to fix this problem, please
#     let me know.


import sys, os, string, tempfile, Numeric


# Set after first call of test_persist().  This will be set from None
# to 0 or 1 upon the first call of test_persist(), then the stored
# value will be used thereafter.  To avoid the test, type 1 or 0 on
# the following line corresponding to whether your gnuplot is new
# enough to understand the -persist option.
_recognizes_persist = None

# Test if gnuplot is new enough to know the option -persist.  It it
# isn't, it will emit an error message with '-persist' in the first
# line.
def test_persist():
    global _recognizes_persist
    if _recognizes_persist is None:
        g = os.popen('echo | gnuplot -persist 2>&1', 'r')
        response = g.readlines()
        g.close()
        _recognizes_persist = ((not response)
                               or (string.find(response[0], '-persist') == -1))
    return _recognizes_persist


# raised for unrecognized option(s):
class OptionException(Exception): pass

# raised for data in the wrong format:
class DataException(Exception): pass


class PlotItem:
    """Plotitem represents an item that can be plotted by gnuplot.

    For the finest control over the output, you can create the
    PlotItems yourself with additional keyword options, or derive new
    classes from PlotItem.

    Members:
      basecommand -- a string holding the elementary argument that
                     must be passed to gnuplot's `plot' command for
                     this item; e.g., 'sin(x)' or '"filename.dat"'.
      options -- a list of strings that need to be passed as options
                 to the plot command, in the order required; e.g.,
                 ['title "data"', 'with linespoints'].
      title -- the title requested (undefined if not requested).  Note
               that `title=None' implies the `notitle' option, whereas
               omitting the title option implies no option (the
               gnuplot default is then used).
      with -- the string requested as a `with' option (undefined if
              not requested)"""

    def __init__(self, basecommand, **keyw):
        self.basecommand = basecommand
        self.options = []
        if keyw.has_key('title'):
            self.title = keyw['title']
            del keyw['title']
            if self.title is None:
                self.options.append('notitle')
            else:
                self.options.append('title "' + self.title + '"')
        if keyw.has_key('with'):
            self.with = keyw['with']
            del keyw['with']
            self.options.append('with ' + self.with)
        if keyw:
            raise OptionException(keyw)

    def command(self):
        """Build the `plot' command to be sent to gnuplot.

        Build and return the `plot' command, with options, necessary
        to display this item."""

        if self.options:
            return self.basecommand + ' ' + string.join(self.options)
        else:
            return self.basecommand

    # if the plot command requires data to be put on stdin (i.e.,
    # `plot "-"'), this method should put that data there.
    def pipein(self, file):
        pass


class Func(PlotItem):
    """Represents a mathematical expression to plot.

    Func represents a mathematical expression that is to be computed
    by gnuplot itself, as in
        gnuplot> plot sin(x)
    The argument to the contructor is a string which is a gnuplot
    expression.  Example:
        g.plot(Func("sin(x)", with="line 3"))
    or shorthand
        g.plot("sin(x)")"""

    def __init__(self, funcstring, **keyw):
        apply(PlotItem.__init__, (self, funcstring), keyw)


class AnyFile:
    """An AnyFile represents any kind of file to be used by gnuplot.

    An AnyFile represents a file, but presumably one that holds data
    in a format readable by gnuplot.  This class simply remembers the
    filename; the existence and format of the file are not checked
    whatsoever.  Note that this is not a PlotItem, though it is used by
    the `File' PlotItem.  Members:

        self.filename -- the filename of the file"""

    def __init__(self, filename):
        self.filename = filename


class TempFile(AnyFile):
    """A TempFile is a file that is automatically deleted.

    A TempFile points to a file.  The file is deleted automatically
    when the TempFile object is deleted.  WARNING: whatever filename
    you pass to this constructor WILL BE DELETED when the TempFile
    object is deleted, even if it was a pre-existing file!  This is
    intended to be used as a parent class of TempArrayFile."""

    def __del__(self):
        os.unlink(self.filename)


class ArrayFile(AnyFile):
    """A file to which, upon creation, an array is written.

    When an ArrayFile is constructed, it creates a file and fills it
    with the contents of a 2-d Numeric array in the format expected by
    gnuplot (i.e., whitespace-separated columns).  The filename can be
    specified, otherwise a random filename is chosen.  The file is NOT
    deleted automatically."""

    def __init__(self, set, filename=None):
        # <set> must be a Numeric array
        assert(len(set.shape) == 2)
        (points, columns) = set.shape
        assert(points > 0)
        assert(columns > 0)
        if not filename:
            filename = tempfile.mktemp()
        f = open(filename, 'w')
        for point in set:
            f.write(string.join(map(repr, point.tolist())) + '\n')
        f.close()
        AnyFile.__init__(self, filename)


class TempArrayFile(ArrayFile, TempFile):
    """An ArrayFile that is deleted automatically."""

    def __init__(self, set, filename=None):
        ArrayFile.__init__(self, set, filename)


class File(PlotItem):
    """A PlotItem representing a DataFile.

    File is a PlotItem that represents a file that should be plotted
    by gnuplot.  <file> can be either a string holding the filename of
    a file that already exists, or it can be anything derived from
    AnyFile (such as a TempArrayFile).  Keyword arguments recognized
    (in addition to those supplied by PlotItem):
        using=<n> -- plot that column against line number
        using=<tuple> -- plot using a:b:c:d etc.
        using=<string> -- plot `using <string>' (allows gnuplot's
                          arbitrary column arithmetic) 
    Note that the `using' option is interpreted by gnuplot, so columns
    must be numbered starting with 1.  Other keyword arguments are
    passed along to PlotItem.  The default `title' for an AnyFile
    PlotItem is `notitle'."""

    def __init__(self, file, using=None, **keyw):
        if isinstance(file, AnyFile):
            self.file = file
            # If no title is specified, then use `notitle' for
            # TempFiles (to avoid using the temporary filename as the
            # title.)
            if isinstance(file, TempFile) and not keyw.has_key('title'):
                keyw['title'] = None
        elif type(file) == type(""):
            self.file = AnyFile(file)
        else:
            raise OptionException
        apply(PlotItem.__init__, (self, '"' + self.file.filename + '"'), keyw)
        self.using = using
        if self.using is None:
            pass
        elif type(self.using) == type(""):
            self.options.insert(0, "using " + self.using)
        elif type(self.using) == type(()):
            self.options.insert(0,
                                "using " +
                                string.join(map(repr, self.using), ':'))
        elif type(self.using) == type(1):
            self.options.insert(0, "using " + `self.using`)
        else:
            raise OptionException('using=' + `self.using`)


class Data(File):
    """Used to plot array data with Gnuplot.

    Create a PlotItem out of a Python Numeric array (or something that
    can be converted to a Float Numeric array).  The array is first
    written to a temporary file, then that file is plotted.  Keyword
    arguments recognized (in addition to those supplied by PlotItem):
        cols=<tuple>
    which outputs only the specified columns of the array to the file.
    Since cols is used by python, the columns should be numbered in
    the python style (starting from 0), not the gnuplot style
    (starting from 1).  The data are written to the temp file; no copy
    is kept in memory."""

    def __init__(self, set, cols=None, **keyw):
        set = Numeric.asarray(set, Numeric.Float)
        if cols is not None:
            set = Numeric.take(set, cols, 1)
        apply(File.__init__, (self, TempArrayFile(set)), keyw)


class Gnuplot:
    """gnuplot plotting object.

    A Gnuplot represents a running gnuplot program and a pipe to
    communicate with it.  It keeps a reference to each of the
    PlotItems used in the current plot, so that they (and their
    associated temporary files) are not deleted prematurely.  The
    communication is one-way; gnuplot's text output just goes to
    stdout with no attempt to check it for error messages.

    Members:
        gnuplot -- the pipe to gnuplot or a file gathering the commands
        itemlist -- a list of the PlotItems that are associated with the
                    current plot.  These are deleted whenever a new plot
                    command is issued via the `plot' method.
        debug -- if this flag is set, commands sent to gnuplot will also
                 be echoed to stderr.

    Methods:
        __init__ -- if a filename argument is specified, the commands
                    will be written to that file instead of being piped
                    to gnuplot immediately.
        plot -- clear the old plot and old PlotItems, then plot the
                arguments in a fresh plot command.  Arguments can be: a
                PlotItem, which is plotted along with its internal
                options; a string, which is plotted as a Func; or
                anything else, which is plotted as a Data.
        hardcopy -- replot the plot to a postscript file (if filename
                    argument is specified) or pipe it to lpr othewise.
                    If the option `color' is set to true, then output
                    color postscript.
        replot -- replot the old items, adding any arguments as
                  additional items as in the plot method.
        refresh -- issue (or reissue) the plot command using the current
                   PlotItems.
        __call__ -- pass an arbitrary string to the gnuplot process,
                    followed by a newline.
        xlabel,ylabel,title --  set attribute to be a string.
        interact -- read lines from stdin and send them, one by one, to
                    the gnuplot interpreter.  Basically you can type
                    commands directly to the gnuplot command processor
                    (though without command-line editing).
        load -- load a file (using the gnuplot `load' command).
        save -- save gnuplot commands to a file (using gnuplot `save'
                command) If any of the PlotItems is a temporary file,
                it will be deleted at the usual time and the save file
                might be pretty useless :-).
        clear -- clear the plot window (but not the itemlist).
        reset -- reset all gnuplot settings to their defaults and clear
                 the current itemlist.
        set_string -- set or unset a gnuplot option whose value is a
                      string.
        _clear_queue -- clear the current PlotItem list.
        _add_to_queue -- add the specified items to the current
                         PlotItem list."""

    def __init__(self, filename=None, persist=0, debug=0):
        """Create a Gnuplot object.

        Gnuplot(filename=None, persist=0, debug=0):
        Create a Gnuplot object.  By default, this starts a gnuplot
        process and prepares to write commands to it.  If a filename
        is specified, the commands are instead written to that file
        (i.e., for later use using `load').  If persist is set,
        gnuplot will be started with the `-persist' option (which
        creates a new X11 plot window for each plot command).  (This
        option is not available on older versions of gnuplot.)  If
        debug is set, the gnuplot commands are echoed to stderr as
        well as being send to gnuplot."""

        if filename:
            # put gnuplot commands into a file:
            self.gnuplot = open(filename, 'w')
        else:
            if persist:
                if not test_persist():
                    raise OptionException(
                        '-persist does not seem to be supported '
                        'by your version of gnuplot!')
                self.gnuplot = os.popen('gnuplot -persist', 'w')
            else:
                self.gnuplot = os.popen('gnuplot', 'w')
        self._clear_queue()
        self.debug = debug

    def __del__(self):
        self('quit')
        self.gnuplot.close()

    def __call__(self, s):
        """Send a command string to gnuplot.

        __call__(s): send the string s as a command to gnuplot,
        followed by a newline and flush.  All interaction with the
        gnuplot process is through this method."""

        self.gnuplot.write(s + "\n")
        self.gnuplot.flush()
        if self.debug:
            # also echo to stderr for user to see:
            sys.stderr.write("gnuplot> %s\n" % (s,))

    def refresh(self):
        """Refresh the plot, using the current PlotItems.

        Refresh the current plot by reissuing the gnuplot plot
        command corresponding to the current itemlist."""

        plotcmds = []
        for item in self.itemlist:
            plotcmds.append(item.command())
        self('plot ' + string.join(plotcmds, ', '))
        for item in self.itemlist:
            item.pipein(self.gnuplot)

    def _clear_queue(self):
        """Clear the PlotItems from the queue."""

        self.itemlist = []

    def _add_to_queue(self, items):
        """Add a list of items to the itemlist, but don't plot them.

        An item can be a PlotItem of any kind, a string (interpreted
        as a function string for gnuplot to evaluate), or a Numeric
        array (or something that can be converted to a Numeric
        array)."""

        for item in items:
            if isinstance(item, PlotItem):
                self.itemlist.append(item)
            elif type(item) is type(""):
                self.itemlist.append(Func(item))
            else:
                # assume data is an array:
                self.itemlist.append(Data(item))

    def plot(self, *items, **kw):
        """Draw a new plot.

        plot(item, ...): Clear the current plot and create a new one
        containing the specified items.  Arguments can be of the
        following types:

        PlotItem (e.g., Data, File, Func):
            This is the most flexible way to call plot because the
            PlotItems can contain suboptions.  Moreover, PlotItems can
            be saved to variables so that their lifetime is longer
            than one plot command--thus they can be replotted with
            minimal overhead.
        string (i.e., "sin(x)"):
            The string is interpreted as a Func() (a function that is
            computed by gnuplot).
        Anything else:
            The object is converted to a Data() item, and thus plotted
            as two-column data.  If the conversion fails, an exception
            is raised."""

        # remove old files:
        self._clear_queue()
        self._add_to_queue(items)
        self.refresh()

    def replot(self, *items):
        """Replot the data, possibly adding new PlotItems.

        Replot the existing graph, using the items in the current
        itemlist.  If arguments are specified, they are interpreted as
        additional items to be plotted alongside the existing items on
        the same graph.  See plot for details."""

        self._add_to_queue(items)
        self.refresh()

    def interact(self):
        """Allow user to type arbitrary commands to gnuplot.

        Read stdin, line by line, and send each line as a command to
        gnuplot.  End by typing C-d."""

        sys.stderr.write("Press C-d to end interactive input\n")
        while 1:
            sys.stderr.write("gnuplot>>> ")
            line = sys.stdin.readline()
            if not line:
                break
            if line[-1] == "\n": line = line[:-1]
            self(line)

    def clear(self):
        """Clear the plot window (without affecting the current itemlist)."""

        self('clear')

    def reset(self):
        """Reset all gnuplot settings to their defaults and clear itemlist."""

        self('reset')
        self.itemlist = []

    def load(self, filename):
        """Load a file using gnuplot's `load' command."""

        self('load "%s"' % (filename,))

    def save(self, filename):
        """Save the current plot commands using gnuplot's `save' command."""

        self('save "%s"' % (filename,))

    def set_string(self, option, s=None):
        """Set a string option, or if s is omitted, unset the option."""

        if s is None:
            self('set %s' % (option,))
        else:
            self('set %s "%s"' % (option, s))

    def xlabel(self, s=None):
        """Set the plot's xlabel."""

        self.set_string('xlabel', s)

    def ylabel(self, s=None):
        """Set the plot's ylabel."""

        self.set_string('ylabel', s)

    def title(self, s=None):
        """Set the plot's title."""

        self.set_string('title', s)

    def hardcopy(self, filename='| lpr', eps=0, color=0):
        """Create a hardcopy of the current plot.

        Create a postscript hardcopy of the current plot.  If a
        filename is specified, save the output in that file; otherwise
        print it immediately using lpr.  If eps is specified, generate
        encapsulated postscript.  If color is specified, create a
        color plot.  Note that this command will return immediately
        even though it might take gnuplot a while to actually finish
        working."""

        setterm = ['set', 'term', 'postscript']
        if eps: setterm.append('eps')
        else: setterm.append('default')
        setterm.append('enhanced')
        if color: setterm.append('color')
        self(string.join(setterm))
        self('set output "%s"' % (filename,))
        self.refresh()
        self('set term x11')
        self('set output')


# The following is a command defined for compatibility with Hinson's
# old Gnuplot.py module.  Its use is deprecated.

# When the plot command is called and persist is not available, the
# plotters will be stored here to prevent their being closed:
_gnuplot_processes = []

def plot(*items, **kw):
    """plot data using gnuplot through Gnuplot.

    This command is roughly compatible with old Gnuplot plot command.
    It is provided for backwards compatibility with the old functional
    interface only.  It is recommended that you use the new
    object-oriented Gnuplot interface, which is much more flexible.

    It can only plot Numeric array data.  In this routine an NxM array
    is plotted as M-1 separate datasets, using columns 1:2, 1:3, ...,
    1:M.

    Limitations:
    - If persist is not available, the temporary files are not
      deleted until final python cleanup."""

    newitems = []
    for item in items:
        # assume data is an array:
        item = Numeric.asarray(item, Numeric.Float)
        dim = len(item.shape)
        if dim == 1:
            newitems.append(Data(item[:, Numeric.NewAxis], with='lines'))
        elif dim == 2:
            if item.shape[1] == 1:
                # one column; just store one item for tempfile:
                newitems.append(Data(item, with='lines'))
            else:
                # more than one column; store item for each 1:2, 1:3, etc.
                tempf = TempArrayFile(item)
                for col in range(1, item.shape[1]):
                    newitems.append(File(tempf, using=(1,col+1), with='lines'))
        else:
            raise DataException("Data array must be 1 or 2 dimensional")
    items = tuple(newitems)
    del newitems

    if kw.has_key('file'):
        g = Gnuplot()
        # setup plot without actually plotting (so data don't appear
        # on the screen):
        g._add_to_queue(items)
        g.hardcopy(kw['file'])
        # process will be closed automatically
    elif test_persist():
        g = Gnuplot(persist=1)
        apply(g.plot, items)
        # process will be closed automatically
    else:
        g = Gnuplot()
        apply(g.plot, items)
        # prevent process from being deleted:
        _gnuplot_processes.append(g)


# Demo code
if __name__ == '__main__':
    from Numeric import *
    import sys

    # a straightforward use of gnuplot:
    g1 = Gnuplot(debug=1)
    g1.title('A simple example') # (optional)
    g1('set data style linespoints') # give gnuplot an arbitrary command
    # Plot a list of (x, y) pairs (tuples or a Numeric array would
    # also be OK):
    g1.plot([[0.,1.1], [1.,5.8], [2.,3.3], [3.,4.2]])

    # Plot one dataset from an array and one via a gnuplot function;
    # also demonstrate the use of item-specific options:
    g2 = Gnuplot(debug=1)
    x = arange(10)
    y1 = x**2
    d = Data(transpose((x, y1)),
             title="calculated by python",
             with="points 1 1")
    g2.title('Data can be computed by python or gnuplot')
    g2.xlabel('x')
    g2.ylabel('x squared')
    g2.plot(d, Func("x**2", title="calculated by gnuplot"))

    # Save what we just plotted as a color postscript file:
    print "\n            Generating postscript file 'gnuplot_test1.ps'\n"
    g2.hardcopy('gnuplot_test1.ps', color=1)

    sys.stderr.write("Press return to continue...\n")
    sys.stdin.readline()

    # ensure processes and temporary files are cleaned up:
    del g1, g2, d

    if 0:
        # Test old-style gnuplot interface

	# List of (x, y) pairs
	plot([(0.,1),(1.,5),(2.,3),(3.,4)])

	# List of y values, file output
        print "\n            Generating postscript file 'gnuplot_test2.ps'\n"
	plot([1, 5, 3, 4], file='gnuplot_test2.ps')

	# Two plots; each given by a 2d array
	from Numeric import *
	x = arange(10)
	y1 = x**2
	y2 = (10-x)**2
	plot(transpose(array([x, y1])), transpose(array([x, y2])))

