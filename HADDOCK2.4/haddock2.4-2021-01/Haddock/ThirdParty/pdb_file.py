# This module handles input and output of PDB files.
#
# Written by Konrad Hinsen <hinsen@cnrs-orleans.fr>
# Last revision: 1999-11-12
#
# This module has been modified by Elmar.Krieger@cmbi.kun.nl and
# Sander.Nabuurs@cmbi.kun.nl to deal with
# messy PDB files that would otherwise cause trouble...
# It must be used with WHAT_MODELBASE to get correct results.
#
# Last revision at CMBI: 2002-08-02
# List of changes:
# - Do not skip residues whose alternate location indicators are not characters
#   but numbers (e.g.1AAC.PDB)
# - Do not crash if ANISOU format deviates (e.g.1DXD.PDB)
# - Do not split amino acids in two parts just because the line counter (columns
#   77 to 80 of old fashioned PDB files) overflows to column 76.
# - Do not split amino acids in multiple parts just because the segment_id[73:76]
#   field was filled with "ALT" to indicate an alternate location like in 1AQM
# - Treat the three letter code "UNK" as unknown amino acid (e.g.1B8D.PDB)
# - Do not skip residues whose alternate location indicators are >"A" or >"1" if
#   the PDB file uses a sequential numbering scheme (e.g.1BS0.PDB)
# - Do not crash when writing a PDB file containing non-standard amino acids (2CAE)
# - Detect and delete alternate location residues with missing alternate location
#   indicator by calculating the CA distances (e.g.1DIN.PDB,residue 123)
# - Store chain_id for every atom (to allow PDBFINDER alignments)
# - Do not start a new chain if someone mixed up segment_id and alternate location
#   indicator(like HIS 34 of 1TGJ). (Only if the atom and residue name is different).
# - Stop parsing as soon as the requested model has been read (this heavily speeds
#   up reading NMR files)
# - Added Structure.delobject method. Structure.molecules was removed for consistency
# - Removed caps "ACE" and "NME" from list of amino acids.
# - Cleaned up the inconsistencies of addResidue and insertResidue methods.
#   Previously these modified the residues in the chain but forgot to update the
#   residues in the structure.
# - Added a detection of unusual amino acids (contain all backbone atoms but have
#   an unknown name). These are now included in the peptide chain, instead of
#   splitting the chain.
# - Amino acids without CA are ignored and not read.
# - Added code to convert non-standard to standard amino acids (makestdamacs method)
# - Added support for CRYST1 record
# - Added support for SCALEn record
# - Added support for reading temperature and pH remarks
# - Added support for reading REMARK 250 - BIOMT transformations
# - SN: Added support for multi-model files. It is now possible to define a range of
#       models to read.
# - Removed requirement for Scientific+Numeric Python so that the module can
#   be used by non-pythoneers.
# - Added support for reading SEQRES record (no writing for now)
# - Added chainseq1 method to get the sequence of an entire chain as a string in one
#   letter code.

"""This module provides classes that represent PDB (Protein Data Bank)
files and configurations contained in PDB files. It provides access to
PDB files on two levels: low-level (line by line) and high-level
(chains, residues, and atoms).

Caution: The PDB file format has been heavily abused, and it is
probably impossible to write code that can deal with all variants
correctly. This modules tries to read the widest possible range of PDB
files, but gives priority to a correct interpretation of the PDB
format as defined by the Brookhaven National Laboratory.

A special problem are atom names. The PDB file format specifies that
the first two letters contain the right-justified chemical element
name. A later modification allowed the initial space in hydrogen names
to be replaced by a digit. Many programs ignore all this and treat the
name as an arbitrary left-justified four-character name. This makes it
difficult to extract the chemical element accurately; most programs
write the '"CA"' for C_alpha in such a way that it actually stands for
a calcium atom! For this reason a special element field has been added
later, but only few files use it.

The low-level routines in this module do not try to deal with the atom
name problem; they return and expect four-character atom names
including spaces in the correct positions. The high-level routines use
atom names without leading or trailing spaces, but provide and use the
element field whenever possible. For output, they use the element
field to place the atom name correctly, and for input, they construct
the element field content from the atom name if no explicit element
field is found in the file.

Except where indicated, numerical values use the same units and
conventions as specified in the PDB format description.

Example:

  >>>conf = Structure('example.pdb')
1  >>>print conf
  >>>for residue in conf.residues:
  >>>    for atom in residue:
  >>>        print atom
"""

import copy, string, math

# This module defines a class that handles I/O using
# Fortran-compatible format specifications.
#
#
# Warning: Fortran formatting is a complex business and I don't
# claim that this module works for anything complicated. It knows
# only the most frequent formatting options. Known limitations:
#
# 1) Only A, D, E, F, G, I, and X formats are supported (plus string constants
#    for output).
# 2) No direct support for complex numbers. You have to split them into
#    real and imaginary parts before output, and for input you get
#    two float numbers anyway.
# 3) No overflow check. If an output field gets too large, it will
#    take more space, instead of being replaced by stars.
#

"""Fortran-compatible input/output

This module provides two classes that aid in reading and writing
Fortran-formatted text files.

Examples:

  Input:

  >>>s = '   59999'
  >>>format = FortranFormat('2I4')
  >>>line = FortranLine(s, format)
  >>>print line[0]
  >>>print line[1]

  prints

  >>>5
  >>>9999


  Output:

  >>>format = FortranFormat('2D15.5')
  >>>line = FortranLine([3.1415926, 2.71828], format)
  >>>print str(line)

  prints

  '3.14159D+00    2.71828D+00'
"""

#
# The class FortranLine represents a single line of input/output,
# which can be accessed as text or as a list of items.
#
class FortranLine:

    """Fortran-style record in formatted files

    FortranLine objects represent the content of one record of a
    Fortran-style formatted file. Indexing yields the contents as
    Python objects, whereas transformation to a string (using the
    built-in function 'str') yields the text representation.

    Constructor: FortranLine(|data|, |format|, |length|='80')

    Arguments:

    |data| -- either a sequence of Python objects, or a string
              formatted according to Fortran rules

    |format| -- either a Fortran-style format string, or a
                FortranFormat object. A FortranFormat should
                be used when the same format string is used repeatedly,
                because then the rather slow parsing of the string
                is performed only once.

    |length| -- the length of the Fortran record. This is relevant
                only when |data| is a string; this string is then
                extended by spaces to have the indicated length.
                The default value of 80 is almost always correct.

    Restrictions:

    1) Only A, D, E, F, G, I, and X formats are supported (plus string
       constants for output).

    2) No direct support for complex numbers; they must be split into
       real and imaginary parts before output.

    3) No overflow check. If an output field gets too large, it will
       take more space, instead of being replaced by stars according
       to Fortran conventions.
    """

    def __init__(self, line, format, length = 80):
	if type(line) == type(''):
	    self.text = line
	    self.data = None
	else:
	    self.text = None
	    self.data = line
	if type(format) == type(''):
	    self.format = FortranFormat(format)
	else:
	    self.format = format
	self.length = length
	if self.text is None:
	    self._output()
	if self.data is None:
	    self._input()

    def __len__(self):
	return len(self.data)

    def __getitem__(self, i):
	return self.data[i]

    def __getslice__(self, i, j):
	return self.data[i:j]

    def __str__(self):
	return self.text

    def isBlank(self):
	return len(string.strip(self.text)) == 0

    def _input(self):
	text = self.text
	if len(text) < self.length: text = text + (self.length-len(text))*' '
	self.data = []
	for field in self.format:
	    l = field[1]
	    s = text[:l]
	    text = text[l:]
	    type = field[0]
	    value = None
	    if type == 'A':
		value = s
	    elif type == 'I':
		s = string.strip(s)
		if len(s) == 0:
		    value = 0
		else:
		    value = int(s)
	    elif type == 'D' or type == 'E' or type == 'F' or type == 'G':
		s = string.lower(string.strip(s))
		n = string.find(s, 'd')
		if n >= 0:
		    s = s[:n] + 'e' + s[n+1:]
		if len(s) == 0:
		    value = 0.
		else:
		    value = float(s)
	    if value is not None:
		self.data.append(value)

    def _output(self):
	data = self.data
	self.text = ''
	for field in self.format:
	    type = field[0]
	    if type == "'":
		self.text = self.text + field[1]
	    elif type == 'X':
		self.text = self.text + field[1]*' '
	    else: # fields that use input data
		length = field[1]
		if len(field) > 2: fraction = field[2]
		value = data[0]
		data = data[1:]
		if type == 'A':
		    self.text = self.text + (value+length*' ')[:length]
		else: # numeric fields
                    if value is None:
                        s = ''
		    elif type == 'I':
			s = `value`
		    elif type == 'D':
			s = ('%'+`length`+'.'+`fraction`+'e') % value
			n = string.find(s, 'e')
			s = s[:n] + 'D' + s[n+1:]
		    elif type == 'E':
			s = ('%'+`length`+'.'+`fraction`+'e') % value
		    elif type == 'F':
			s = ('%'+`length`+'.'+`fraction`+'f') % value
		    elif type == 'G':
			s = ('%'+`length`+'.'+`fraction`+'g') % value
		    else:
			raise ValueError, 'Not yet implemented'
		    s = string.upper(s)
		    self.text = self.text + ((length*' ')+s)[-length:]
        self.text = string.rstrip(self.text)

#
# The class FortranFormat represents a format specification.
# It ought to work for correct specifications, but there is
# little error checking.
#
class FortranFormat:

    """Parsed fortran-style format string

    Constructor: FortranFormat(|format|), where |format| is a
    format specification according to Fortran rules.
    """

    def __init__(self, format, nested = 0):
	fields = []
	format = string.strip(format)
	while format and format[0] != ')':
	    n = 0
	    while format[0] in string.digits:
		n = 10*n + int(format[0])
		format = format[1:]
	    if n == 0: n = 1
	    type = string.upper(format[0])
	    if type == "'":
		eof = string.find(format, "'", 1)
		text = format[1:eof]
		format = format[eof+1:]
	    else:
		format = string.strip(format[1:])
	    if type == '(':
		subformat = FortranFormat(format, 1)
		fields = fields + n*subformat.fields
		format = subformat.rest
		eof = string.find(format, ',')
		if eof >= 0:
		    format = format[eof+1:]
	    else:
		eof = string.find(format, ',')
		if eof >= 0:
		    field = format[:eof]
		    format = format[eof+1:]
		else:
		    eof = string.find(format, ')')
		    if eof >= 0:
			field = format[:eof]
			format = format[eof+1:]
		    else:
			field = format
			format = ''
		if type == "'":
		    field = (type, text)
		else:
		    dot = string.find(field, '.')
		    if dot > 0:
			length = int(field[:dot])
			fraction = int(field[dot+1:])
			field = (type, length, fraction)
		    else:
			if field:
			    length = int(field)
			else:
			    length = 1
			field = (type, length)
		fields = fields + n*[field]
	self.fields = fields
	if nested:
	    self.rest = format

    def __len__(self):
	return len(self.fields)

    def __getitem__(self, i):
	return self.fields[i]

#
# A convenient base class...
#
class PDBExportFilter:

    def processLine(self, type, data):
        return type, data

    def processResidue(self, name, number, terminus):
        return name, number

    def processChain(self, chain_id, segment_id):
        return chain_id, segment_id

    def terminateChain(self):
        pass

#
# XPlor export filter
class XPlorExportFilter(PDBExportFilter):

    xplor_atom_names = {' OXT': 'OT2'}

    def processLine(self, type, data):
        if type == 'TER':
            return None, data
        if type == 'ATOM' or type == 'HETATM' or type == 'ANISOU':
            name = self.xplor_atom_names.get(data['name'], data['name'])
            data['name'] = name
        return type, data


export_filters = {'xplor': XPlorExportFilter}

#
# Fortran formats for PDB entries
#
atom_format = FortranFormat('A6,I5,1X,A4,A1,A4,A1,I4,A1,3X,3F8.3,2F6.2,' +
                            '6X,A4,2A2')
anisou_format = FortranFormat('A6,I5,1X,A4,A1,A4,A1,I4,A1,1X,6I7,2X,A4,2A2')
conect_format = FortranFormat('A6,11I5')
ter_format = FortranFormat('A6,I5,6X,A4,A1,I4,A1')
model_format = FortranFormat('A6,4X,I4')
header_format = FortranFormat('A6,4X,A40,A9,3X,A4')
cryst1_format = FortranFormat('A6,3F9.3,3F7.2,1X,A11,I4')
scale_format = FortranFormat('A6,4X,3F10.6,5X,1F10.5')
generic_format = FortranFormat('A6,A74')

#
# Amino acid and nucleic acid residues
#
amino_acids3 = ['ALA', 'ARG', 'ASN', 'ASP', 'CYS', 'CYX', 'GLN', 'GLU', 'GLY',
               'HIS', 'HID', 'HIE', 'HIP', 'HSD', 'HSE', 'HSP', 'ILE', 'LEU',
               'LYS', 'MET', 'PHE', 'PRO', 'SER', 'THR', 'TRP', 'TYR', 'VAL',
               'MSE', 'NME', 'UNK']
amino_acids1 = ['A',   'R',   'N',   'D',   'C',   'C',   'Q',   'E',   'G',
                'H',   'H',   'H',   'H',   'H',   'H',   'H',   'I',   'L',
                'K',   'M',   'F',   'P',   'S',   'T',   'W',   'Y',   'V',
                'M',   'X',   'X']

nucleic_acids = [ 'A',  'C',  'G',  'I',  'T',  'U',
                 '+A', '+C', '+G', '+I', '+T', '+U']

stdamacatoms={"CYS":["N","H","CA","HA","C","O","OXT","CB","HB","SG","HG"],
              "MET":["N","H","CA","HA","C","O","OXT","CB","HB","CG","HG","SD","CE","HE"],
              }
stdamaclist=["CYS","MET"]
nstamaclist=["CSS","MSE"]
nstrenamelist={"MSE":["SE","SD"]}

# REPLACEMENTS FOR EXOTIC IONS
exoticionlist=["HO"]
normalionlist=["CA"]

# N- AND C-TERMINAL CAPS
capdict={"FOR":["C","O"],"ACE":["C","O","CH3"],"NH2":["N"]}

# ELEMENT MASS IN ATOMIC UNITS
elementmass=\
[ 0,1.0079,4.00260,6.941,9.01218,10.811,12.011,14.0067,15.9994,18.998403,
  20.179,22.98977,24.305,26.98154,28.0855,30.97376,32.06,35.453,39.948,
  39.0983,40.078,44.9559,47.88,50.9415,51.9961,54.9380,55.847,58.9332,
  58.6934,63.546,65.39,69.723,72.61,74.9216,78.96,79.904,83.80,
  85.468,87.62,88.906,91.224,92.906,95.94,98.906,101.07,102.91,
  106.42,107.87,112.41,114.82,118.71,121.75,127.60,126.90,131.29,# Xe
  132.905,137.328,138.906,140.116,140.908,144.24,145.0,150.36,151.964,
  157.25,158.925,162.50,164.930,167.26,168.934,173.04,174.967,178.49,180.948,183.84,186.207,190.23,192.217,195.078,196.967,
  200.59,204.383,207.2,208.980,209.0,210.0,222.0,223.0,226.0,227.0,232.038,231.036,238.029,237.0,244.0,243.0,
  247.0,247.0,251.0,252.0,257.0,258.0,259.0,262.0,261.0,262.0,263.0,264.0,265.0,268.0,269.0 ]

# ABBREVIATIONS OF THE CHEMICAL ELEMENTS
elementabbr=\
["BB",
 "H","He",
 "Li","Be","B","C","N","O","F","Ne",
 "Na","Mg","Al","Si","P","S","Cl","Ar",
 "K","Ca","Sc","Ti","V","Cr","Mn","Fe","Co","Ni","Cu","Zn","Ga","Ge","As","Se","Br","Kr",
 "Rb","Sr","Y","Zr","Nb","Mo","Tc","Ru","Rh","Pd","Ag","Cd","In","Sn","Sb","Te","I","Xe",
 "Cs","Ba","La","Ce","Pr","Nd","Pm","Sm","Eu",
 "Gd","Tb","Dy","Ho","Er","Tm","Yb","Lu","Hf","Ta","W","Re","Os","Ir","Pt","Au",
 "Hg","Tl","Pb","Bi","Po","At","Rn","Fr","Ra","Ac","Th","Pa","U","Np","Pu","Am",
 "Cm","Bk","Cf","Es","Fm","Md","No","Lr","Rf","Db","Sg","Bh","Hs","Mt"]

def defineAminoAcidResidue(symbol):
    amino_acids3.append(string.upper(symbol))

def defineNucleicAcidResidue(symbol):
    nucleic_acids.append(string.upper(symbol))


# CHECK IF TWO ALTERNATE LOCATION INDICATORS ARE THE SAME
# =======================================================
def issamealtloc(a,b):
  if (a==""):
    if ('A' in b or '1' in b): return(1)
    return(0)
  if (a in b): return(1)
  for i in range(2):
    if ((a=="A" and b=="1") or (a=="B" and b=="2") or (a=="C" and b=="3") or
        (a=="D" and b=="4") or (a=="E" and b=="5") or (a=="F" and b=="6") or
        (a=="G" and b=="7") or (a=="H" and b=="8") or (a=="I" and b=="9")):
      return(1)
    c=a
    a=b
    b=c
  return(0)

#
# Low-level file object. It represents line contents as Python dictionaries.
# For output, there are additional methods that generate sequence numbers
# for everything.
#
class PDBFile:

    """PDB file with access at the record level

    Constructor: PDBFile(|filename|, |mode|='"r"'), where |filename|
    is the file name and |mode| is '"r"' for reading and '"w"' for writing,
    """

    def __init__(self, filename, mode = 'r', subformat = None):
	self.file = open(filename, mode)
	self.output = string.lower(mode[0]) == 'w'
        self.export_filter = None
        if subformat is not None:
             export = export_filters.get(subformat, None)
             if export is not None:
                 self.export_filter = export()
        self.open = 1
        # EK: NUMBER OF LAST RESIDUE READ, USED TO GUESS IF A RESIDUE WITH ALTERNATE
        #   LOCATION INDICATOR >"A" SHOULD BE RENAMED TO "A", BECAUSE THE AUTHOR
        #   USED A SEQUENTIAL NAMING SCHEME (SEE 1BS0.PDB)
        self.lastresno = -1
        self.lastchain = ""
        # EK: ALTERNATE LOCATION INDICATOR THAT WILL BE TRANSFORMED TO "A"
        self.altrename = ""
        if self.output:
            self.data = {'serial_number': 0,
                         'residue_number': 0,
                         'chain_id': '',
                         'segment_id': ''}
            self.het_flag = 0
            self.chain_number = -1

    def readLine(self):
        """Returns the contents of the next non-blank line (= record).
        The return value is a tuple whose first element (a string)
        contains the record type. For supported record types (HEADER,
        ATOM, HETATM, ANISOU, TERM, MODEL, CONECT), the items from the
        remaining fields are put into a dictionary which is returned
        as the second tuple element. Most dictionary elements are
        strings or numbers; atom positions are returned as a vector,
        and anisotropic temperature factors are returned as a rank-2
        tensor, already multiplied by 1.e-4. White space is stripped
        from all strings except for atom names, whose correct
        interpretation can depend on an initial space. For unsupported
        record types, the second tuple element is a string containing
        the remaining part of the record.
        """
	while 1:
	    line = self.file.readline()
	    # UNTIL THE RCSB HAS TIME TO CORRECT 1HC8
	    if (string.strip(line)=="ATOM    252  N   ARG A   37      70.647  91.305  23.399  1.00 80.75           N"):
	      line="ATOM    252  N   ARG A  37      70.647  91.305  23.399  1.00 80.75           N"
	    if (string.strip(line)=="HETATM14371  O   HOH B1188   32.660  40.759  61.083  0.50 12.14           O"):
	      line="HETATM14371  O   HOH B1188      32.660  40.759  61.083  0.50 12.14           O"
	    if not line: return ('END','')
	    if line[-1] == '\n': line = line[:-1]
	    line = string.strip(line)
	    if line: break
	line = string.ljust(line, 80)
	type = string.strip(line[:6])
	if type == 'ATOM' or type == 'HETATM':
	    # EK: CHECK IF STRING.ATOI IN SCIENTIFIC PYTHON MIGHT CRASH
	    for i in range(22,26):
	      if (line[i]!=' ' and line[i] not in string.digits and i==25):
	        line=line[:22]+' '+line[22:26]+line[27:]
	        break
	    line = FortranLine(line, atom_format)
	    data = {'serial_number': line[1],
		    'name': line[2],
		    'alternate': string.strip(line[3]),
		    'residue_name': string.strip(line[4]),
		    'chain_id': string.strip(line[5]),
		    'residue_number': line[6],
        'insertion_code': string.strip(line[7]),
        'position': line[8:11],
		    'occupancy': line[11],
		    'temperature_factor': line[12],
		    'segment_id': string.strip(line[13]),
		    'element': string.strip(line[14]),
		    'charge': string.strip(line[15])}
	    # EK: A NEW CHAIN FOUND ?
	    if (data['chain_id']!=self.lastchain):
	      self.lastchain=data['chain_id']
              # EK: RESET NUMBER OF LAST RESIDUE AND ALTERNATE LOC. RENAMING
              self.lastresno=-1
	      self.altrename="~"
	    # EK: A RESIDUE WITH HIGHER NUMBER FOUND?
	    if (data['residue_number']>self.lastresno):
	      # EK: A RESIDUE WITH HIGHER NUMBER HAS BEEN FOUND
	      self.lastresno=data['residue_number']
	      # EK: RENAME ALTERNATE LOCATION INDICATOR TO 'A'
	      if (data['alternate']>'A' or
	          (data['alternate']>'1' and data['alternate']<='9')):
	        self.altrename=data['alternate']
	      else:
	        self.altrename="~"
	    # EK: RENAME IF NEEDED
	    if (data['alternate']==self.altrename): data['alternate']='A'
	    return type, data
        elif type == 'ANISOU':
            # EK: SCRIPT CAN CRASH IF ANISOU CONTAINS JUST A "-" (see 1DXD.PDB)
            i=30
            l=min(len(line),70)
            while (i<l):
              # EK: CHECK IF LONELY MINUS AROUND SOMEWHERE
              if (line[i]=="-" and (i==l-1 or line[i+1]<"0" or line[i+1]>"9")):
                line=line[:i]+"0"+line[i+1:]
              i=i+1
            line = FortranLine(line, anisou_format)
	    data = {'serial_number': line[1],
		    'name': line[2],
		    'alternate': string.strip(line[3]),
		    'residue_name': string.strip(line[4]),
		    'chain_id': string.strip(line[5]),
		    'residue_number': line[6],
                    'insertion_code': string.strip(line[7]),
                    'u': [[1e-4*line[8], 1e-4*line[11], 1e-4*line[12]],
                          [1e-4*line[11], 1e-4*line[9] , 1e-4*line[13]],
                          [1e-4*line[12], 1e-4*line[13], 1e-4*line[10]]],
		    'segment_id': string.strip(line[14]),
		    'element': string.strip(line[15]),
		    'charge': string.strip(line[16])}
	    return type, data
        elif type == 'TER':
            line = FortranLine(line, ter_format)
            data = {'serial_number': line[1],
                    'residue_name': string.strip(line[2]),
                    'chain_id': string.strip(line[3]),
                    'residue_number': line[4],
                    'insertion_code': string.strip(line[5])}
	    return type, data
	elif type == 'CONECT':
            line = FortranLine(line, conect_format)
	    data = {'serial_number': line[1],
		    'bonded': filter(lambda i: i > 0, line[2:6]),
		    'hydrogen_bonded': filter(lambda i: i > 0, line[6:10]),
		    'salt_bridged': filter(lambda i: i > 0, line[10:12])}
	    return type, data
        elif type == 'MODEL':
            line = FortranLine(line, model_format)
            data = {'serial_number': line[1]}
	    return type, data
        elif type == 'HEADER':
            line = FortranLine(line, header_format)
            data = {'compound': line[1],
                    'date': line[2],
                    'pdb_code': line[3]}
	    return type, data
	elif type =="CRYST1":
		line=FortranLine(line,cryst1_format)
		data={"a":line[1],
          "b":line[2],
          "c":line[3],
          "alpha":line[4],
          "beta":line[5],
          "gamma":line[6],
          "spacegroup":line[7],
          "chains":line[8]}
		return type,data
	elif type[0:5]=="SCALE" and type[5] in ['1','2','3']:
		line=FortranLine(line,scale_format)
		data={"s1":line[1],
          "s2":line[2],
          "s3":line[3],
          "u":line[4]}
		return type,data
	elif type[0:6]=="REMARK" and line[6:10]==" 200":
		if (line[12:23]=="TEMPERATURE"):
		  try: temp=float(string.split(line)[-1])
		  except: temp=None
		  if (string.find(line,"CELSIUS")!=-1): temp=temp+273.15
		  return "TEMP",temp
		if (line[12:23]=="TEMPERATURE"):
		  try: temp=float(string.split(line)[-1])
		  except: temp=None
		  if (string.find(line,"CELSIUS")!=-1): temp=temp+273.15
		  return "TEMP",temp
		if (line[12:14]=="PH"):
		  try: ph=float(string.split(line)[-1])
		  except: ph=None
		  return "PH",ph
		return type, line[6:]
	elif type[0:6]=="REMARK" and line[6:10]==" 350":
		return("BIOMT",line[10:])
	elif type[0:6]=="SEQRES":
		return("SEQRES",[line[11],string.split(line[19:70])])
	else: return type, line[6:]

    def writeLine(self, type, data):
        """Writes a line using record type and data dictionary in the
        same format as returned by readLine(). Default values are
        provided for non-essential information, so the data dictionary
        need not contain all entries.
        """
        if self.export_filter is not None:
            type, data = self.export_filter.processLine(type, data)
            if type is None:
                return
        line = [type]
        if type == 'ATOM' or type == 'HETATM':
            format = atom_format
            position = data['position']
            line = line + [data.get('serial_number', 1),
                           data.get('name'),
                           data.get('alternate', ''),
                           string.rjust(data.get('residue_name', ''), 3),
                           data.get('chain_id', ''),
                           data.get('residue_number', 1),
                           data.get('insertion_code', ''),
                           position[0], position[1], position[2],
                           data.get('occupancy', 0.),
                           data.get('temperature_factor', 0.),
                           data.get('segment_id', ''),
                           string.rjust(data.get('element', ''), 2),
                           data.get('charge', '')]
        elif type == 'ANISOU':
            format = anisou_format
            u = 1.e4*data['u']
            u = [int(u[0,0]), int(u[1,1]), int(u[2,2]),
                 int(u[0,1]), int(u[0,2]), int(u[1,2])]
            line = line + [data.get('serial_number', 1),
                           data.get('name'),
                           data.get('alternate', ''),
                           string.rjust(data.get('residue_name'), 3),
                           data.get('chain_id', ''),
                           data.get('residue_number', 1),
                           data.get('insertion_code', '')] \
                        + u \
                        + [data.get('segment_id', ''),
                           string.rjust(data.get('element', ''), 2),
                           data.get('charge', '')]
        elif type == 'TER':
            format = ter_format
            line = line + [data.get('serial_number', 1),
                           string.rjust(data.get('residue_name'), 3),
                           data.get('chain_id', ''),
                           data.get('residue_number', 1),
                           data.get('insertion_code', '')]
        elif type == 'CONECT':
            format = conect_format
            line = line + [data.get('serial_number')]
            line = line + (data.get('bonded', [])+4*[None])[:4]
            line = line + (data.get('hydrogen_bonded', [])+4*[None])[:4]
            line = line + (data.get('salt_bridged', [])+2*[None])[:2]
        elif type == 'MODEL':
            format = model_format
            line = line + [data.get('serial_number')]
        elif type == 'HEADER':
            format = header_format
            line = line + [data.get('compound', ''), data.get('date', ''),
                           data.get('pdb_code')]
        elif type == 'CRYST1':
            format = cryst1_format
            line = line +[data["a"],data["b"],data["c"],data["alpha"],data["beta"],
                          data["gamma"],data["spacegroup"],data["chains"]]
        elif type[0:5]=="SCALE" and type[5] in ['1','2','3']:
            format = scale_format
            line = line +[data["s1"],data["s2"],data["s3"],data['u']]
        elif type=="BIOMT":
            format = generic_format
            line = ["REMARK"," 350"+data]
        else:
            format = generic_format
            line = line + [data]
        self.file.write(str(FortranLine(line, format)) + '\n')

    def writeComment(self, text):
        """Writes |text| into one or several comment lines.
        Each line of the text is prefixed with 'REMARK' and written
        to the file.
        """
	while text:
	    eol = string.find(text,'\n')
	    if eol == -1:
		eol = len(text)
	    self.file.write('REMARK %s \n' % text[:eol])
	    text = text[eol+1:]

    def writeAtom(self, name, position, occupancy=0.0, temperature_factor=0.0,
                  element=''):
        """Writes an ATOM or HETATM record using the |name|, |occupancy|,
        |temperature| and |element| information supplied. The residue and
        chain information is taken from the last calls to the methods
        nextResidue() and nextChain().
        """
	if self.het_flag:
	    type = 'HETATM'
	else:
	    type = 'ATOM'
	name = string.upper(name)
        if element != '' and len(element) == 1 and name and len(name)<4 and name[0] == element:
            name = ' ' + name
        self.data['name'] = name
        self.data['position'] = position
        self.data['serial_number'] = (self.data['serial_number'] + 1) % 100000
        self.data['occupancy'] = occupancy
        self.data['temperature_factor'] = temperature_factor
        self.data['element'] = element
        self.writeLine(type, self.data)

    def nextResidue(self, name, number = None, terminus = None):
        """Signals the beginning of a new residue, starting with the
        next call to writeAtom(). The residue name is |name|, and a
        |number| can be supplied optionally; by default residues in a
        chain will be numbered sequentially starting from 1. The
        value of |terminus| can be 'None', '"C"', or '"N"'; it is passed
        to export filters that can use this information in order to
        use different atom or residue names in terminal residues.
        """
        name  = string.upper(name)
        if self.export_filter is not None:
            name, number = self.export_filter.processResidue(name,number,terminus)
        self.het_flag =  not (name in amino_acids3 or name in nucleic_acids)
        self.data['residue_name']=name
        self.data['residue_number']=self.data['residue_number']+1
        if (self.data['residue_number']<0): self.data['residue_number']=-(-self.data['residue_number']%1000)
        else: self.data['residue_number']=self.data['residue_number']%10000
        self.data['insertion_code'] = ''
        if number is not None:
            if type(number) is type(0):
                if (number<0): number=-(-number%1000)
                else: number=number%10000
                self.data['residue_number']=number
            else:
                if (number.number<0): number.number=-(-number.number%1000)
                else: number.number=number.number%10000
                self.data['residue_number'] = number.number
                self.data['insertion_code'] = number.insertion_code

    def nextChain(self, chain_id = None, segment_id = ''):
        """Signals the beginning of a new chain. A chain identifier
        (string of length one) can be supplied as |chain_id|, by
        default consecutive letters from the alphabet are used.
        The equally optional |segment_id| defaults to an empty string.
        """
        if chain_id is None:
            self.chain_number = (self.chain_number + 1) % len(self._chain_ids)
            chain_id = self._chain_ids[self.chain_number]
        if self.export_filter is not None:
            chain_id, segment_id = \
                      self.export_filter.processChain(chain_id, segment_id)
        self.data['chain_id'] = (chain_id+' ')[:1]
        self.data['segment_id'] = (segment_id+'    ')[:4]
        self.data['residue_number'] = 0

    _chain_ids = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

    def terminateChain(self):
        "Signals the end of a chain."
        if self.export_filter is not None:
            self.export_filter.terminateChain()
        self.data['serial_number'] = (self.data['serial_number'] + 1) % 100000
        self.writeLine('TER', self.data)
        self.data['chain_id'] = ''
        self.data['segment_id'] = ''

    def close(self):
        """Closes the file. This method *must* be called for write mode
        because otherwise the file will be incomplete.
        """
        if self.open:
            if self.output:
                self.file.write('END\n')
            self.file.close()
            self.open = 0

    def __del__(self):
        self.close()


#
# High-level object representation of PDB file contents.
#

#
# Representation of objects.
#
class Atom:

    """Atom in a PDB structure

    Constructor: Atom(|name|, |position|, |**properties|),
    where |name| is the PDB atom name (a string),
    |position| is a atom position (a vector), and
    |properties| can include any of the other items that
    can be stored in an atom record.

    The properties can be obtained or modified using
    indexing, as for Python dictionaries.
    """
    
    def __init__(self, name, position, **properties):
	self.position = position
        self.properties = properties
        if self.properties.get('element', '') == '':
           if name[0] == ' ' or name[0] in string.digits:
               self.properties['element'] = name[1]
           elif (len(name)==4 and name[0] in string.uppercase):
               self.properties['element'] = name[0]
           elif name[1] in string.digits:
               self.properties['element'] = name[0]
        self.name = string.strip(name)

    def __getitem__(self, item):
        try:
            return self.properties[item]
        except KeyError:
            if item == 'name':
                return self.name
            elif item == 'position':
                return self.position
            else:
                raise KeyError, "Undefined atom property: " + repr(item)

    def __setitem__(self, item, value):
        self.properties[item] = value

    def __str__(self):
	return self.__class__.__name__ + ' ' + self.name + \
               ' at ' + str(self.position)
    __repr__ = __str__

    def type(self):
        "Returns the six-letter record type, ATOM or HETATM."
	return 'ATOM  '

    def save(self, file):
        """Writes an atom record to |file| (a PDBFile object or a
        string containing a file name)."""
        close = 0
        if type(file) == type(''):
            file = PDBFile(file, 'w')
            close = 1
        file.writeAtom(self.name, self.position,
                       self.properties.get('occupancy', 0.),
                       self.properties.get('temperature_factor', 0.),
                       self.properties.get('element', ''))
        if close:
            file.close()


class HetAtom(Atom):

    """HetAtom in a PDB structure

    A subclass of Atom, which differs only in the return value
    of the method type().

    Constructor: HetAtom(|name|, |position|, |**properties|).
    """

    def type(self):
	return 'HETATM'


class Group:

  """Atom group (residue or molecule) in a PDB file

  This is an abstract base class. Instances can be created using
  one of the subclasses (Molecule, AminoAcidResidue, NucleotideResidue).

  Group objects permit iteration over atoms with for-loops,
  as well as extraction of atoms by indexing with the
  atom name.
  """

  def __init__(self, name, atoms = None, number = None):
    self.name = name
    self.number = number
    self.atom_list = []
    self.atoms = {}
    if atoms:
      self.atom_list = atoms
      for a in atoms:
        self.atoms[a.name] = a

  def __len__(self):
    return len(self.atom_list)

  def __getitem__(self, item):
    if type(item) == type(0):
      return self.atom_list[item]
    else:
      return self.atoms[item]

  def __str__(self):
    s = self.__class__.__name__ + ' ' + self.name + ':\n'
    for atom in self.atom_list:
      s = s + '  ' + `atom` + '\n'
    return s

  __repr__ = __str__

  def isCompatible(self, residue_data):
    return(residue_data['residue_name']==self.name and
           residue_data['residue_number']==self.number)

  def addAtom(self, atom):
    "Adds |atom| (an Atom object) to the group."
    self.atom_list.append(atom)
    self.atoms[atom.name] = atom

  def delatom(self, atom):
    """Removes |atom| (an Atom object) from the group. An exception
       will be raised if |atom| is not part of the group."""
    self.atom_list.remove(atom)
    del self.atoms[atom.name]

  def renameatom(self,atom,name):
    """Renames |atom| (an Atom object) in the group."""
    if name != atom.name:
      del self.atoms[atom.name]
      atom.name=name
      self.atoms[name]=atom


      #oldname = atom.name
      #atom.name = name
      #self.atoms[atom.name]=copy.deepcopy(self.atoms[oldname])
      #del self.atoms[oldname]

  def deleteHydrogens(self):
    "Removes all hydrogen atoms."
    delete = []
    for a in self.atom_list:
      if a.name[0] == 'H' or (a.name[0] in string.digits and a.name[1] == 'H'):
        delete.append(a)
    for a in delete:
      self.delatom(a)

  def changeName(self, name):
    "Sets the PDB residue name to |name|."
    self.name = name

  def save(self, file):
    """Writes the group to |file| (a PDBFile object or a
       string containing a file name). """
    close = 0
    if type(file) == type(''):
      file = PDBFile(file, 'w')
      close = 1

    # EK: UNUSUAL AMINO ACIDS DO NOT HAVE A TERMINUS TYPE
    if (hasattr(self,"terminusType")):
      file.nextResidue(self.name, self.number, self.terminusType())
    else:
      file.nextResidue(self.name, self.number, None)
    for a in self.atom_list:
      a.save(file)
    if close: file.close()

  # GET MASS OF ATOM GROUP
  # ======================
  # THE CHEMICAL ELEMENT OF EACH ATOM IS DETERMINED VIA THE 'element' PROPERTY
  # WHICH MUST BE PRESENT IN THE PDB FILE.
  def mass(self):
    mass=0.0
    for atom in self.atom_list:
      if (atom.properties.has_key("element")):
        element=atom.properties["element"]
        if (element not in elementabbr):
          print "Group.mass: Ignoring unknown element",element
        else:
          mass=mass+elementmass[elementabbr.index(element)]
      else:
        print "Group.mass: Ignoring atom without element property"
    return(mass)

class Molecule(Group):

  """Molecule in a PDB file

  A subclass of Group.

  Constructor: Molecule(|name|, |atoms|='None', |number|=None, |chain_id|=None),
  where |name| is the PDB residue name. An optional list
  of |atoms| can be specified, otherwise the molecule is initially
  empty. The optional |number| is the PDB residue number.

  Note: In PDB files, non-chain molecules are treated as residues,
  there is no separate molecule definition. This modules defines
  every residue as a molecule that is not an amino acid residue or a
  nucleotide residue.
  """

  is_molecule=1

  def iscap(self):
    "Check if molecule is a terminal cap"
    if (not capdict.has_key(self.name)): return(0)
    atomlist=capdict[self.name]
    for atom in atomlist:
      if (not self.atoms.has_key(atom)): return(0)
    return(1)

class Residue(Group):

    pass

class AminoAcidResidue(Residue):

    """Amino acid residue in a PDB file

    A subclass of Group.

    Constructor: AminoAcidResidue(|name|, |atoms|='None', |number|=None),
    where |name| is the PDB residue name. An optional list
    of |atoms| can be specified, otherwise the residue is initially
    empty. The optional |number| is the PDB residue number.
    """

    is_amino_acid = 1

    def isCTerminus(self):
        """Returns 1 if the residue is in C-terminal configuration,
        i.e. if it has a second oxygen bound to the carbon atom of
        the peptide group.
        """
        return self.atoms.has_key('OXT') or self.atoms.has_key('OT2')

    def isNTerminus(self):
        """Returns 1 if the residue is in N-terminal configuration,
        i.e. if it contains more than one hydrogen bound to be
        nitrogen atom of the peptide group.
        """
        return self.atoms.has_key('1HT') or self.atoms.has_key('2HT') \
               or self.atoms.has_key('3HT')

    def save(self, file):
        close = 0
        if type(file) == type(''):
            file = PDBFile(file, 'w')
            close = 1
        terminus = None
        if self.isCTerminus(): terminus = 'C'
        if self.isNTerminus(): terminus = 'N'
        file.nextResidue(self.name, self.number, terminus)
        for a in self.atom_list:
            a.save(file)
        if close:
            file.close()


class NucleotideResidue(Residue):

    """Nucleotide residue in a PDB file

    A subclass of Group.

    Constructor: NucleotideResidue(|name|, |atoms|='None', |number|=None),
    where |name| is the PDB residue name. An optional list
    of |atoms| can be specified, otherwise the residue is initially
    empty. The optional |number| is the PDB residue number.
    """

    is_nucleotide = 1

    def __init__(self, name, atoms = None, number = None):
        self.pdbname = name
        name = name[:-1] + 'D' + name[-1]
	Residue.__init__(self, name, atoms, number)
        for a in atoms:
            if a.name == 'O2*': # Ribose
                self.name = self.name[:-2] + 'R' + self.name[-1]

    def isCompatible(self, residue_data):
        return (residue_data['residue_name'] == self.name or
                residue_data['residue_name'] == self.pdbname) \
               and residue_data['residue_number'] == self.number

    def addAtom(self, atom):
        Residue.addAtom(self, atom)
        if atom.name == 'O2*': # Ribose
            self.name = self.name[:-2] + 'R' + self.name[-1]

    def hasRibose(self):
        "Returns 1 if the residue has an atom named O2*."
        return self.atoms.has_key('O2*')

    def hasDesoxyribose(self):
        "Returns 1 if the residue has no atom named O2*."
        return not self.hasRibose()

    def hasPhosphate(self):
        "Returns 1 if the residue has a phosphate group."
        return self.atoms.has_key('P')

    def save(self, file):
        close = 0
        if type(file) == type(''):
            file = PDBFile(file, 'w')
            close = 1
        terminus = None
        if not self.hasPhosphate(): terminus = '5'
        file.nextResidue(self.name[:-2]+self.name[-1], self.number, terminus)
        for a in self.atom_list:
            a.save(file)
        if close:
            file.close()

class Chain:

    """Chain of PDB residues

    This is an abstract base class. Instances can be created using
    one of the subclasses (PeptideChain, NucleotideChain).

    Chain objects respond to len() and return their residues
    by indexing with integers.
    """

    def __init__(self, residues = None, chain_id = None, segment_id = None):
        if residues is None:
            self.residues = []
        else:
            self.residues = residues
        self.chain_id = chain_id
        self.segment_id = segment_id

    def __len__(self):
        return len(self.residues)

    def sequence1(self):
      "Returns a string with the chain sequence in one letter code."
      seq=""
      for residue in self.residues:
        if (residue.name in amino_acids3):
          seq=seq+amino_acids1[amino_acids3.index(residue.name)]
        else:
          seq=seq+'X'
      return(seq)

    def sequence3(self):
      "Returns a list of residue names in three letter code."
      seqlist=[]
      for residue in self.residues:
        seqlist.append(residue.name)
      return(seqlist)

    def __getitem__(self, index):
        return self.residues[index]

    def addResidue(self, residue):
        "Add |residue| at the end of the chain."
        self.residues.append(residue)

    """
    # EK: METHOD TO INSERT A RESIDUE
    def insertResidue(self, pos, residue):
        "Insert |residue| at the specified position of the chain."
        i=self.structure.objects.index(self)
        self.structure.insertResidue(self.structure.objstart[i]+pos,residue)
        self.residues.insert(pos,residue)

    def delresidues(self, first, last):
        #Remove residues starting from |first| up to (but not
        #including) |last|. If |last| is 'None', remove everything
        #starting from |first|.
        if last is None:
            del self.residues[first:]
        else:
            del self.residues[first:last]
    """

    def deleteHydrogens(self):
        "Removes all hydrogen atoms."
        for r in self.residues:
          r.deleteHydrogens()

    def save(self, file):
        """Writes the chain to |file| (a PDBFile object or a
        string containing a file name).
        """
        close = 0
        if type(file) == type(''):
            file = PDBFile(file, 'w')
            close = 1
        file.nextChain(self.chain_id, self.segment_id)
        for r in self.residues:
            r.save(file)
        file.terminateChain()
        if close:
            file.close()

class PeptideChain(Chain):

    """Peptide chain in a PDB file

    A subclass of Chain.

    Constructor: PeptideChain(|residues|='None', |chain_id|='None',
                              |segment_id|='None'), where |chain_id|
    is a one-letter chain identifier and |segment_id| is
    a multi-character chain identifier, both are optional. A list
    of AminoAcidResidue objects can be passed as |residues|; by
    default a peptide chain is initially empty.
    """

    def __getslice__(self, i1, i2):
	return self.__class__(self.residues[i1:i2])

    def isTerminated(self):
        "Returns 1 if the last residue is in C-terminal configuration."
        return self.residues and self.residues[-1].isCTerminus()

    def isCompatible(self, chain_data, residue_data):
        return chain_data['chain_id'] == self.chain_id and \
               chain_data['segment_id'] == self.segment_id and \
               residue_data['residue_name'] in amino_acids3

    def hasbreak(self):
      "Check if chain is broken"
      for i in range(len(self.residues)-1):
        if (not self.residues[i].atoms.has_key('C') or
            not self.residues[i+1].atoms.has_key('N') or
            not self.residues[i+1].atoms.has_key('CA')):
          return(1)
        d2=0
        for j in range(3):
          d=self.residues[i].atoms['C'].position[j]-\
            self.residues[i+1].atoms['N'].position[j]
          d2=d2+d*d
        if (d2>2.5*2.5): return(1)
      return(0)

class NucleotideChain(Chain):

    """Nucleotide chain in a PDB file

    A subclass of Chain.

    Constructor: NucleotideChain(|residues|='None', |chain_id|='None',
                                 |segment_id|='None'), where |chain_id|
    is a one-letter chain identifier and |segment_id| is
    a multi-character chain identifier, both are optional. A list
    of NucleotideResidue objects can be passed as |residues|; by
    default a nucleotide chain is initially empty.
    """

    def __getslice__(self, i1, i2):
	return self.__class__(self.residues[i1:i2])

    def isTerminated(self):
        return 0

    def isCompatible(self, chain_data, residue_data):
        return chain_data['chain_id'] == self.chain_id and \
               chain_data['segment_id'] == self.segment_id and \
               residue_data['residue_name'] in nucleic_acids

class MoleculeChain(Chain):

    def isTerminated(self):
        return 0

    def isCompatible(self, chain_data, residue_data):
        return chain_data['chain_id'] == self.chain_id and \
               chain_data['segment_id'] == self.segment_id and \
               residue_data['residue_name'] not in amino_acids3 and \
               residue_data['residue_name'] not in nucleic_acids

#
# Residue number class for dealing with insertion codes
#
class ResidueNumber:

    """PDB residue number

    Most PDB residue numbers are simple integers, but when insertion
    codes are used a number can consist of an integer plus a letter.
    Such compound residue numbers are represented by this class.

    Constructor: ResidueNumber(|number|, |insertion_code|)
    """

    def __init__(self, number, insertion_code):
        self.number = number
        self.insertion_code = insertion_code

    def __cmp__(self, other):
        if type(other) == type(0):
            if self.number == other:
                return 1
            else:
                return cmp(self.number, other)
        if self.number == other.number:
            return cmp(self.insertion_code, other.insertion_code)
        else:
            return cmp(self.number, other.number)

    def __str__(self):
        return str(self.number) + self.insertion_code
    __repr__ = __str__

#
# The configuration class.
#
class Structure:

  """A high-level representation of the contents of a PDB file

  Constructor: Structure(|filename|, |model|='0', |alternate_code|='"A"'),
  where |filename| is the name of the PDB file. Compressed files
  and URLs are accepted, as for class PDBFile. The two optional
  arguments specify which data should be read in case of a
  multiple-model file or in case of a file that contains alternative
  positions for some atoms.

  The components of a system can be accessed in several ways
  ('s' is an instance of this class):

  - 's.residues' is a list of all PDB residues, in the order in
    which they occurred in the file.

  - 's.peptide_chains' is a list of PeptideChain objects, containing
    all peptide chains in the file in their original order.

  - 's.nucleotide_chains' is a list of NucleotideChain objects, containing
    all nucleotide chains in the file in their original order.

  - 's.molecules' is a list of all PDB residues that are neither
    amino acid residues nor nucleotide residues, in their original
    order.

  - 's.objects' is a list of all high-level objects (peptide chains,
    nucleotide chains, and molecules) in their original order.

  An iteration over a Structure instance by a for-loop is equivalent
  to an iteration over the residue list.
  """
  # SN: ADDED ENDMODEL TO SELECT A RANGE OF MODELS TO BE READ.
  def __init__(self, filename, model = 0, endmodel = None, alternate_code = 'A'):
    self.filename = filename
    self.model = model
    # SET ENDMODEL
    if endmodel == None: self.endmodel = model+1
    else: self.endmodel = endmodel
    self.alternate = alternate_code
    self.pdb_code = ''
    self.residues = []
    self.objects = []
    self.objstart = []
    self.modelstart = []
    self.peptide_chains = []
    self.nucleotide_chains = []
    # READ PDB FILE
    self.parseFile(PDBFile(filename))

  #peptide_chain_constructor = PeptideChain
  #nucleotide_chain_constructor = NucleotideChain
  #molecule_constructor = Molecule

  def __len__(self):
    return len(self.residues)

  def __getitem__(self, item):
    return self.residues[item]

  def deleteHydrogens(self):
    "Removes all hydrogen atoms."
    for r in self.residues:
      r.deleteHydrogens()

  def delobject(self,obj):
    "Deletes an object"
    if (self.objects[obj] in self.peptide_chains):
      del self.peptide_chains[self.peptide_chains.index(self.objects[obj])]
    elif (self.objects[obj] in self.nucleotide_chains):
      del self.nucleotide_chains[self.nucleotide_chains.index(self.objects[obj])]
    if (obj==len(self.objects)-1): del self.residues[self.objstart[obj]:]
    else:
      dellen=self.objstart[obj+1]-self.objstart[obj]
      del self.residues[self.objstart[obj]:self.objstart[obj+1]]
      for i in range(obj+1,len(self.objects)):
        self.objstart[i]=self.objstart[i]-dellen
    del self.objects[obj]
    del self.objstart[obj]

  def splitPeptideChain(self, number, position):
    """Splits the peptide chain indicated by |number| (0 being
    the first peptide chain in the PDB file) after the residue indicated
    by |position| (0 being the first residue of the chain).
    The two chain fragments remain adjacent in the peptide chain
    list, i.e. the numbers of all following nucleotide chains increase
    by one.
    """
    self._splitChain(PeptideChain, self.peptide_chains, number, position)

  def splitNucleotideChain(self, number, position):
    """Splits the nucleotide chain indicated by |number| (0 being
    the first nucleotide chain in the PDB file) after the residue indicated
    by |position| (0 being the first residue of the chain).
    The two chain fragments remain adjacent in the nucleotide chain
    list, i.e. the numbers of all following nucleotide chains increase
    by one.
    """
    self._splitChain(NucleotideChain, self.nucleotide_chains, number, position)

  def _splitChain(self, constructor, chain_list, number, position):
    chain = chain_list[number]
    part1 = constructor(self, chain.residues[:position], chain.chain_id, chain.segment_id)
    part2 = constructor(self, chain.residues[position:])
    chain_list[number:number+1] = [part1, part2]
    index = self.objects.index(chain)
    self.objects[index:index+1] = [part1, part2]
    self.objstart[index:index+1] = [self.objstart[index],self.objstart[index]+position]

  def joinPeptideChains(self, first, second):
    """Join the two peptide chains indicated by |first| and |second|
    into one peptide chain. The new chain occupies the position
    |first|; the chain at |second| is removed from the peptide
    chain list.
    """
    self._joinChains(PeptideChain, self.peptide_chains, first, second)

  def joinNucleotideChains(self, first, second):
    """Join the two nucleotide chains indicated by |first| and |second|
    into one nucleotide chain. The new chain occupies the position
    |first|; the chain at |second| is removed from the nucleotide
    chain list.
    """
    self._joinChains(NucleotideChain, self.nucleotide_chains, first, second)

  def _joinChains(self, constructor, chain_list, first, second):
    chain1 = chain_list[first]
    chain2 = chain_list[second]
    total = constructor(chain1.residues+chain2.residues,
                        chain1.chain_id, chain1.segment_id)
    chain_list[first] = total
    del chain_list[second]
    index = self.objects.index(chain1)
    self.objects[index] = total
    index = self.objects.index(chain2)
    del self.objects[index]
    del self.objstart[index]

  def addResidue(self,residue):
    self.residues.append(residue)
    self.objects[-1].addResidue(residue)

  def insertResidue(self,pos,residue):
    self.residues.insert(pos,residue)
    for i in range(len(self.objects)):
      if (self.objstart[i]>pos): self.objstart[i]=self.objstart[i]+1

  def delresidues(self,start,end):
    "Delete a stretch of residues"
    if (start<0): start=len(self.residues)+start
    if (end==None): end=len(self.residues)
    elif (end<0): end=len(self.residues)+end
    del self.residues[start:end]
    i=0
    while (i<len(self.objects)):
      residues=len(self.objects[i].residues)
      if (self.objstart[i]>=start):
        if (self.objstart[i]+residues<=end):
          # DELETE ENTIRE OBJECT
          #print "DelOBJ!",start,end,residues,self.objstart[i]
          self.objects[i].residues=[]
          self.delobject(i)
          continue
        if (self.objstart[i]<end):
          # DELETE START OF OBJECT
          del self.objects[i].residues[:end-self.objstart[i]]
          self.objstart[i]=start
        else:
          # SHIFT NUMBER
          self.objstart[i]=self.objstart[i]-(end-start)
      else:
        if (self.objstart[i]+residues<=end):
          # DELETE END OF OBJECT
          del self.objects[i].residues[start-self.objstart[i]:]
        else:
          # DELETE MIDDLE OF OBJECT
          del self.objects[i].residues[start-self.objstart[i]:end-self.objstart[i]]
      i=i+1

  def extractData(self, data):
    atom_data = {}
    # EK: ADDED chain_id
    for name in ['serial_number', 'name', 'position',
                 'occupancy', 'temperature_factor', 'chain_id']:
      atom_data[name] = data[name]
    for name in ['alternate', 'charge']:
      value = data[name]
      if value:
        atom_data[name] = value
    element = data['element']
    if element != '':
      try:
        int(element)
      except ValueError:
        atom_data['element'] = element
    residue_data = {'residue_name': data['residue_name']}
    number = data['residue_number']
    insertion = data['insertion_code']
    if insertion == '':
      residue_data['residue_number'] = number
    else:
      residue_data['residue_number'] = ResidueNumber(number, insertion)
    chain_data = {}
    for name in ['chain_id', 'segment_id']:
      chain_data[name] = data[name]
    # EK: THE STRING SLICER [0:3] HAD TO BE ADDED TO COPE WITH THOSE PDB FILES
    #   THAT USE COLUMNS 77-80 TO STORE LINE NUMBERS. IF THE LINE NUMBER
    #   OVERFLOWS FROM 9999 TO 10000, THE SEGMENT_ID IN COLUMN 76 CHANGES,
    #   CAUSING THIS SCRIPT TO SPLIT THE AMINO ACID RESIDUE IN TWO PARTS.
    #   (SEE FOR EXAMPLE LINE 10006 OF 1ABB)
    if  (chain_data['segment_id'][0:3] == self.pdb_code[0:3] or
    # THE FOLLOWING TEST MAKES SURE THAT USING THE SEGMENT_ID FIELD TO
    # SPECIFY ALTERNATE LOCATIONS (SEE 1AQM.PDB) DOESN'T SPLIT THE RESIDUE
         chain_data['segment_id'][0:3] == 'ALT'):
      chain_data['segment_id'] = ''
    return atom_data, residue_data, chain_data

  # ADD A NEW RESIDUE
  def newResidue(self, residue_data):
    name = residue_data['residue_name']
    residue_number = residue_data['residue_number']
    if name in amino_acids3:
      residue = AminoAcidResidue(name, [], residue_number)
    elif name in nucleic_acids:
      residue = NucleotideResidue(name, [], residue_number)
    else:
      residue = Molecule(name, [], residue_number)
    return residue

  # ADD A NEW CHAIN TO DATA STRUCTURES
  def newChain(self, residue, chain_data):
    if hasattr(residue, 'is_amino_acid'):
      chain = PeptideChain(None,chain_data['chain_id'],chain_data['segment_id'])
      self.peptide_chains.append(chain)
      self.objects.append(chain)
      self.objstart.append(len(self.residues))

    elif hasattr(residue, 'is_nucleotide'):
      chain = NucleotideChain(None,chain_data['chain_id'],chain_data['segment_id'])
      self.nucleotide_chains.append(chain)
      self.objects.append(chain)
      self.objstart.append(len(self.residues))

    else:
      chain = MoleculeChain(None,chain_data['chain_id'],chain_data['segment_id'])
      self.objects.append(chain)
      self.objstart.append(len(self.residues))
    return(chain)

  # CHECK LAST RESIDUE
  # ==================
  # THE LAST RESIDUE IS ANALYZED WITH RESPECT TO THE PRECEDING ONES,
  # AND POSSIBLY DELETED (ALTLOC, NO CA-ATOM)
  def lastrescheck(self,new_chain,chain,highresid):
    # A NEW RESIDUE HAS BEEN FOUND, NOW IT'S TIME TO CHECK
    #   IF THE LAST ONE SHOULD BE KEPT (IS NOT ON TOP
    #   OF ANOTHER ONE)
    if (chain!=None and len(self.residues)):
      residue=self.residues[-1]
      if (hasattr(residue,"is_amino_acid") and not residue.atoms.has_key("CA")):
        # AMINO ACIDS WITHOUT A CA ARE IGNORED
        if (len(chain.residues)==1): new_chain=1
        self.delresidues(-1,None)
      if (len(chain.residues)>1 and residue.atoms.has_key("CA")):
        # NOT THE FIRST RESIDUE, CA IS PRESENT
        # GET CA COORDINATES
        (cax,cay,caz)=residue.atoms["CA"].position
        # GET NUMBER OF HIGHEST RESIDUE SO FAR
        hnum=highresid
        if (hasattr(hnum,"insertion_code")): hnum=hnum.number
        # IS INSERTION CODE OR ALTLOC PRESENT?
        rnum=residue.number
        if (hasattr(rnum,"insertion_code")):
          # YES, CHECK ALL RESIDUES FOR OVERLAP
          overlapchk=0
          rnum=rnum.number
        else:
          # NO, CHECK ONLY THE LAST RESIDUE FOR OVERLAP
          overlapchk=len(chain.residues)-2
        while (overlapchk<len(chain.residues)-1):
          if (chain.residues[overlapchk].atoms.has_key("CA")):
            pos=chain.residues[overlapchk].atoms["CA"].position
            dx=cax-pos[0]
            dy=cay-pos[1]
            dz=caz-pos[2]
            d=math.sqrt(dx*dx+dy*dy+dz*dz)
            if (d<1.0 and rnum<=hnum):
              # BUMP DETECTED AND
              # ALTERNATE LOCATION FOUND, DELETE RESIDUE
              if (len(chain.residues)==1): new_chain=1
              self.delresidues(-1,None)
              break
          overlapchk=overlapchk+1
      if (len(chain.residues)==1):
        # TRY TO JOIN LAST RESIDUE WITH PREVIOUS CHAIN (UNUSUAL AMINO ACIDS)
        chain=self.unusualamacjoined(chain)
    return(new_chain,chain,highresid)

  # PARSE PDB FILE
  # ==============
  def parseFile(self,file):
    atom=None
    residue=None
    chain=None
    new_chain=0
    read=(self.model==0)
    speedup=0
    # SN: THE MODEL CURRENTLY UNDER INVESTIGATION
    currentmodel = 0
    self.cryst1=None
    self.scale=[None,None,None]
    self.ph=None
    self.temperature=None
    self.biomt=[]
    self.seqres={}
    # EK: HIGHEST RESIDUE ID IN CHAIN
    highresid = ResidueNumber(0,None)
    while (1):
      type, data = file.readLine()
      if (type=='END'):
        (new_chain,chain,highresid)=self.lastrescheck(new_chain,chain,highresid)
        break
      elif (type=='HEADER'):
        self.pdb_code = string.upper(data['pdb_code'])
      elif (type=='MODEL'):
        # SN: DECIDE TO READ IF WE ARE IN THE RANGE OF
        #     DESIRED MODELS
        currentmodel = data['serial_number']
        read = (currentmodel >= self.model and currentmodel < self.endmodel)
        if (self.model == 0 and len(self.residues) == 0):
          read = 1
      elif type == 'CRYST1': self.cryst1=data
      elif type[0:5] == 'SCALE' and type[5] in ['1','2','3']:
        self.scale[int(type[5])-1]=data
      elif type=="PH": self.ph=data
      elif type=="TEMP": self.temperature=data
      elif type=="BIOMT": self.biomt.append(data)
      elif type=="SEQRES":
        chain2=data[0]
        if (chain2==' '): chain2='_'
        if (self.seqres.has_key(chain2)):
          self.seqres[chain2]=self.seqres[chain2]+data[1]
        else:
          self.seqres[chain2]=data[1]
      elif type == 'ENDMDL':
        # CHECK LAST RESIDUE OF PREVIOUS MODEL
        (new_chain,chain,highresid)=self.lastrescheck(new_chain,chain,highresid)
        # SN: TO SPEED UP MULTI MODEL FILES, WE
        # READ MORE THEN ONE MODEL PER FILE, IF
        # ALL MODELS ARE READ WE STOP READING
        if (read) and currentmodel == (self.endmodel-1): break
        # SN: ADD THE STARTING POSITION OF THE FOLLOWING MODEL
        if (read): self.modelstart.append(len(self.residues))
        read = 0
      elif read:
        # READ DATA
        if type == 'ATOM' or type == 'HETATM':
          alt = data['alternate']
          # EK: THE ISSAMEALTLOC FUNCTION COMPARES THE ALTERNATE LOCATION
          #       INDICATORS IN A WAY THAT ALSO WORKS WITH MESSY PDB FILES
          #       LIKE 1AAC
          if issamealtloc(alt,self.alternate):
            atom_data, residue_data, chain_data = self.extractData(data)
            if type == 'ATOM': atom = apply(Atom, (), atom_data)
            else: atom = apply(HetAtom, (), atom_data)
            # EK: THIS IS THE LAST CHANCE TO PREVENT STARTING A NEW CHAIN
            # IF THE PDB FILE IS BUGGY.
            # TEST 1: IF CURRENT RESIDUE NAME AND RESIDUE NUMBER ARE THE SAME
            #         AS THE PREVIOUS ONE, THE segment_id
            #         IS COPIED FROM PREVIOUS ATOM (SEE FOR EXAMPLE 1TGJ,HIS 34
            #         OR 2ILK, LYS 88)
            if (chain!=None and residue!=None and residue.isCompatible(residue_data)):
              chain_data['segment_id']=chain.segment_id
            # START A NEW CHAIN?
            new_chain = chain is None or not chain.isCompatible(chain_data,residue_data)
            # SET FLAG IF RESIDUE IS INCOMPATIBLE WITH NEW DATA
            new_residue = new_chain or residue is None or not residue.isCompatible(residue_data)
            if new_residue and chain is not None and chain.isTerminated():
              new_chain = 1

            if new_residue:
              # START A NEW RESIDUE
              # ADD UNUSUAL AMINO ACIDS TO PRECEDING CHAIN
              (new_chain,chain,highresid)=self.lastrescheck(new_chain,chain,highresid)
              # CHAINS MAY HAVE BEEN JOINED ABOVE
              if (chain): new_chain=not chain.isCompatible(chain_data,residue_data)
              residue=self.newResidue(residue_data)
              if new_chain:
                chain=self.newChain(residue, chain_data)
                highresid = ResidueNumber(0,None)
                # SN: SET MODELSTART IF THIS IS THE FIRST MODEL
                if (len(self.modelstart)==0):
                    self.modelstart.append(0)
              self.addResidue(residue)
              # UPDATE ID OF HIGHEST RESIDUE SO FAR
              if (highresid<residue.number):
                highresid=residue.number
            # EK: SOME DUMMY FILES LIKE 1DBW SER 78 USE ' ' AND 'A' AS ALTLOCS.
            # MAKE SURE NO ATOM IS EVER ADDED TWICE TO THE RESIDUE
            if (not residue.atoms.has_key(atom.name)): residue.addAtom(atom)

        elif type == 'ANISOU':
          alt = data['alternate']
          if issamealtloc(alt,self.alternate):
            if atom is None:
              raise ValueError, "ANISOU record before ATOM record"
            atom['u'] = data['u']
        elif type == 'TER':
          # FINAL CHECKS
          (new_chain,chain,highresid)=self.lastrescheck(new_chain,chain,highresid)
          chain=None
    # MANY PDB FILES HAVE pH AND TEMPERATURE INFO MISSING
    # A FEW IMPORTANT ONES FROM THE LITERATURE ARE ADDED HERE
    phtemp={"1CDP":[None,4],"2OVO":[7,None],"1PGX":[5.5,18],"1IFC":[7.3,None],
            "1CHN":[6.5,20],"1FUS":[3.5,None],"1PTF":[5,14],"1HYP":[4.7,25],
            "1HOE":[1,25],  "1BBC":[5.5,None],"1MJC":[7.5,None],"2ERL":[3.5,None],
            "1AAC":[6.5,None],"1WFA":[7.3,4],"1G2B":[3.5,None]}
    if (phtemp.has_key(self.pdb_code)):
      self.ph=phtemp[self.pdb_code][0]
      self.temperature=phtemp[self.pdb_code][1]
      if (self.temperature!=None): self.temperature=self.temperature+273.15
    # SOME PDB FILES HAVE A USELESS REMARK 350 (BIOMT) INFO (JUST THE UNIT MATRIX)
    unit=1
    for line in self.biomt:
      if (line[13:18]=="BIOMT"):
        valuelist=string.split(line[25:])
        for i in range(4):
          value=float(valuelist[i])
          if (value!=0 and (value!=1 or i!=ord(line[18])-1)): unit=0
    if (unit): self.biomt=[]
    if (self.seqres=={}):
      # NO SEQRES FOUND - CREATE IT
      for chain in self.peptide_chains:
        id=chain.chain_id
        if (id=='' or id==' '): id='_'
        self.seqres[id]=self.chainseq3(chain.chain_id)

  def unusualamacjoined(self,chain):
    "Check for unusual AA and add to previous chain"
    if (hasattr(chain.residues[0],"is_molecule") and
        chain.residues[0].atoms.has_key('N') and
        chain.residues[0].atoms.has_key('CA') and
        chain.residues[0].atoms.has_key('C') and
        chain.residues[0].atoms.has_key('O')):
      # UNUSUAL AMINO ACID FOUND
      # TURN INTO PEPTIDE CHAIN
      chain.residues[0].is_molecule=0
      chain.residues[0].is_amino_acid=1
      unusualaa=PeptideChain(chain.residues,chain.chain_id,chain.segment_id)
      self.peptide_chains.append(unusualaa)
      self.objects[-1]=self.peptide_chains[-1]
      #print "Creating new chain"
      #print len(self.objects),len(self.peptide_chains)
      #print self.objects,self.peptide_chains
      # DOES IT FIT TO PRECEDING PEPTIDE CHAIN?
      if (len(self.objects)>1 and len(self.peptide_chains) and
          self.objects[-2]==self.peptide_chains[-2] and
          self.objects[-2].chain_id==chain.chain_id and
          self.objects[-2].segment_id==chain.segment_id):
        # YES, ADD TO PRECEDING PEPTIDE CHAIN
        #print "Joining"
        self._joinChains(PeptideChain,self.peptide_chains,-2,-1)
      # NEW CHAIN
      chain=self.peptide_chains[-1]
    return(chain)

  def hetgrouplist(self):
    "Return list of hetero groups"
    hetgrouplist=[]
    for object in self.objects:
      if (object not in self.peptide_chains and object not in self.nucleotide_chains):
        # HETERO GROUP FOUND
        # DO NOT COUNT IONS AS HETERO GROUPS
        if (len(object.residues)==1 and len(object.residues[0].atom_list)==1): continue
        # DO NOT COUNT WATERS AS HETERO GROUPS
        allwater=1
        for residue in object.residues:
          if (residue.name!="HOH"):
            allwater=0
            break
        if (allwater): continue
        # APPEND TO LIST
        hetgrouplist.append(object)
    return(hetgrouplist)

  def haschainbreaks(self):
    "Determine if structure contains chain breaks"
    for chain in self.peptide_chains:
      if (chain.hasbreak()): return(1)
    return(0)

  def renamechains(self,startchain):
    "Rename all chains sequentially starting with 'startchain'"
    for i in range(len(self.objects)):
      object=self.objects[i]
      if (object in self.peptide_chains or object in self.nucleotide_chains):
        object.chain_id=startchain
        for residue in object.residues:
          for atom in residue.atom_list:
            atom.properties["chain_id"]=startchain
        for residue in self.residues[self.objstart[i]:self.objstart[i]+len(object.residues)]:
          for atom in residue.atom_list:
            atom.properties["chain_id"]=startchain
        if (startchain=='Z'): startchain='A'
        else: startchain=chr(ord(startchain)+1)


  def renumberAtoms(self):
    "Renumber all atoms sequentially starting with 1."
    n = 0
    for residue in self.residues:
      for atom in residue:
        atom['serial_number'] = n
        n = n + 1

  def __repr__(self):
    s = self.__class__.__name__ + "(" + repr(self.filename)
    if self.model != 0:
      s = s + ", model=" + repr(self.model)
    # MODIFIED TO DEAL WITH MESSY PDB FILES
    if self.alternate != 'A' and self.alternate!='1':
      s = s + ", alternate_code = " + repr(self.alternate)
    s = s + "):\n"
    for name, list in [("Peptide", self.peptide_chains),
                       ("Nucleotide", self.nucleotide_chains)]:
      for c in list:
        s = s + "  " + name + " chain "
        if c.segment_id:
          s = s + c.segment_id + " "
        elif c.chain_id:
          s = s + c.chain_id + " "
        s = s + "of length " + repr(len(c)) + "\n"
    return s

  def save(self, file):
    """Writes all objects to |file| (a PDBFile object or a
    string containing a file name).
    """
    close = 0
    if type(file) == type(''):
      file = PDBFile(file, 'w')
      close = 1
    # WRITE CRYSTAL RECORD
    if (self.cryst1): file.writeLine("CRYST1",self.cryst1)
    # WRITE SCALE RECORD
    for i in range(3):
      if (self.scale[i]): file.writeLine("SCALE%d"%(i+1),self.scale[i])
    # WRITE BIOMT RECORD
    for line in self.biomt:
      file.writeLine("BIOMT",line)
    for o in self.objects: o.save(file)
    if close: file.close()

  # MAKE STANDARD AMINO ACIDS
  # =========================
  # ALL UNUSUAL AMINO ACIDS ARE CONVERTED TO THEIR CLOSEST STANDARD ONES.
  def makestdamacs(self):
    """Converts all unusual amino acids to standard ones."""
    for residue in self.residues:
      if (residue.name in nstamaclist):
        # NON-STANDARD AMINO ACID FOUND
        name=stdamaclist[nstamaclist.index(residue.name)]
        newresidue=AminoAcidResidue(name,residue.atom_list,residue.number)
        # RENAME ATOMS
        if (nstrenamelist.has_key(residue.name)):
          renamelist=nstrenamelist[residue.name]
          for atom in newresidue.atom_list:
            for i in range(0,len(renamelist),2):
              if (renamelist[i]==atom.name):
                atom.name=renamelist[i+1]
        # DELETE EXTRA ATOMS
        atoms=stdamacatoms[name]
        l=0
        while (l<len(newresidue.atom_list)):
          atom=newresidue.atom_list[l]
          name=atom.name
          if (name not in atoms):
            newresidue.delatom(atom)
          else:
            l=l+1
        for object in self.objects:
          if (residue in object.residues):
            object.residues[object.residues.index(residue)]=newresidue
            break
        self.residues[self.residues.index(residue)]=newresidue

  # MAKE STANDARD IONS
  # ==================
  # ALL EXOTIC IONS ARE CONVERTED TO THEIR CLOSEST STANDARD ONES.
  def makestdions(self):
    """Converts all exotic ions to standard ones."""
    for residue in self.residues:
      if (residue.name in exoticionlist and len(residue)==1 and residue.atom_list[0].name==residue.name):
        # EXOTIC ION FOUND
        newname=normalionlist[exoticionlist.index(residue.name)]
        residue.name=newname
        residue.atom_list[0].name=newname
        residue.atom_list[0].properties["element"]=newname

  def cbposition(self,res):
    """Get the coordinates of the CB atom and construct them if only N,CA and C (GLY)
       are present"""
    residue=self.residues[res]
    if (residue.atoms.has_key("CB")): return(residue.atoms["CB"].position)
    if (not residue.atoms.has_key("N") or not residue.atoms.has_key("CA") or
        not residue.atoms.has_key("C")): return(None)
    can=[]
    cac=[]
    capos=residue.atoms["CA"].position
    cbpos=[0,0,0]
    for i in range(3):
      can.append(residue.atoms["N"].position[i]-capos[i])
      cac.append(residue.atoms["C"].position[i]-capos[i])
    (s1,s2,s3)=(-0.537,-0.534,0.571)
    cbpos[0]=capos[0]+s1*can[0]+s2*cac[0]+s3*(can[1]*cac[2]-can[2]*cac[1])
    cbpos[1]=capos[1]+s1*can[1]+s2*cac[1]+s3*(can[2]*cac[0]-can[0]*cac[2])
    cbpos[2]=capos[2]+s1*can[2]+s2*cac[2]+s3*(can[0]*cac[1]-can[1]*cac[0])
    return(cbpos)

  def cadistance(self,res1,res2):
    """Measure the CA-CA distance between two residues"""
    if (not self.residues[res1].atoms.has_key("CA") or
        not self.residues[res2].atoms.has_key("CA")): return(None)
    pos1=self.residues[res1].atoms["CA"].position
    pos2=self.residues[res2].atoms["CA"].position
    dis2=0
    for i in range(3): dis2=dis2+(pos1[i]-pos2[i])*(pos1[i]-pos2[i])
    return(math.sqrt(dis2))

  def cbdistance(self,res1,res2):
    """Measure the CB-CB distance between two residues"""
    pos1=self.cbposition(res1)
    pos2=self.cbposition(res2)
    if (pos1==None or pos2==None): return(None)
    dis2=0
    for i in range(3): dis2=dis2+(pos1[i]-pos2[i])*(pos1[i]-pos2[i])
    return(math.sqrt(dis2))

  def distance(self,res1,atom1,res2,atom2):
    """Measure the distance between two atoms in two residues"""
    if (not self.residues[res1].atoms.has_key(atom1) or
        not self.residues[res2].atoms.has_key(atom2)): return(None)
    pos1=self.residues[res1].atoms[atom1].position
    pos2=self.residues[res2].atoms[atom2].position
    dis2=0
    for i in range(3): dis2=dis2+(pos1[i]-pos2[i])*(pos1[i]-pos2[i])
    return(math.sqrt(dis2))

  # GET CHAIN SEQUENCE IN ONE-LETTER CODE
  # =====================================
  # THE AMINO ACID SEQUENCE OF THE REQUESTED CHAIN IS RETURNED AS A STRING
  def chainseq1(self,chain):
    """Get the sequence of the given chain in one letter code"""
    for object in self.peptide_chains:
      if (object.chain_id==chain):
        return(object.sequence1())
    return(None)

  # GET CHAIN SEQUENCE IN THREE-LETTER CODE
  # =======================================
  # THE AMINO ACID SEQUENCE OF THE REQUESTED CHAIN IS RETURNED AS A LIST OF STRINGS
  def chainseq3(self,chain):
    """Get the sequence of the given chain in three letter code"""
    for object in self.peptide_chains:
      if (object.chain_id==chain):
        return(object.sequence3())
    return(None)

  def chainseqcb1(self,chain):
    """Get the sequence of the given chain in one letter code including chain breaks"""
    for object in self.peptide_chains:
      if (object.chain_id==chain):
        seq=object.sequence1()
        for i in range(len(object.residues)-1,0,-1):
          if (object.residues[i-1].atoms.has_key('C') and
              object.residues[i-1].atoms.has_key('CA') and
              object.residues[i].atoms.has_key('N') and
              object.residues[i].atoms.has_key('CA')):
            d2=0
            for j in range(3):
              d=object.residues[i-1].atoms['C'].position[j]-\
                object.residues[i].atoms['N'].position[j]
              d2=d2+d*d
            if (d2>2.5*2.5):
              seq=seq[:i]+'-'+seq[i:]
        return(seq)
    return(None)

  # FIND CLOSEST CHAIN
  # ==================
  # THE NAME OF THE CHAIN THAT MATCHES BEST IS RETURNED. THIS MAINLY SOLVES THE
  # CONFUSION ABOUT CHAINS 'A' AND '_'
  def closestchain(self,chain):
    if (chain=='~'): chain=self.peptide_chains[0].chain_id
    if (self.seqres.has_key(chain)): return(chain)
    if (chain=='_'): chain='A'
    elif (chain=='A' or chain=='0'): chain='_'
    if (self.seqres.has_key(chain)): return(chain)
    if (len(self.peptide_chains)==1): return(self.peptide_chains[0].chain_id)
    return(None)

  def chainstart(self,chain):
    """Get the starting residue of the given chain"""
    for i in range(len(self.objects)):
      if (self.objects[i].chain_id==chain): return(self.objstart[i])
    return(None)

  # GET MASS
  # ========
  # RETURNS THE MOLECULAR WEIGHT IN ATOMIC MASS UNITS (DALTONS).
  def mass(self):
    """Get the mass in daltons"""
    mass=0.0
    for residue in self.residues:
      mass=mass+residue.mass()
    return(mass)

  def multiplicity(self):
    """Get the structural multiplicity, i.e. the number of times each sequence is present.
       Chains must be sorted as identical blocks of different sequences"""
    chains=len(self.peptide_chains)
    if (not chains): return(None)
    firstseq=self.peptide_chains[0].sequence1()
    for i in range(1,chains):
      if (self.peptide_chains[i].sequence1()==firstseq): return(chains/i)
    return(1)

  def setoccupancy(self,start,end,occupancy):
    """Set residue occupancy from residues start till end"""
    for i in range(start,end):
      residue=self.residues[i]
      for atom in residue.atom_list:
        atom.properties["occupancy"]=occupancy


