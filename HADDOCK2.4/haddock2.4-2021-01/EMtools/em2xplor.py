from __future__ import division

from struct import unpack
from operator import mul
from argparse import ArgumentParser, FileType
from os.path import splitext


class CCP4Parser(object):
    """Parser for CCP4-formatted density files"""

    HEADER_SIZE = 1024
    HEADER_TYPE = 'i' * 10 + 'f' * 6 + 'i' * 3 + 'f' * 3 + 'i' * 3 +\
        'f' * 27 + 'c' * 8 + 'f' * 1 + 'i' * 1 + 'c' * (800)
    HEADER_FIELDS = ('nc nr ns mode ncstart nrstart nsstart nx ny nz xlength ylength ' \
        'zlength alpha beta gamma mapc mapr maps amin amax amean ispg ' \
        'nsymbt lskflg skwmat skwtrn extra xstart ystart zstart map ' \
        'machst rms nlabel label').split()
    HEADER_CHUNKS = [1] * 25 + [9, 3, 12] + [1] * 3 + [4, 4, 1, 1, 800]

    def __init__(self, fid):

        if isinstance(fid, str):
            fhandle = open(fid)
        elif isinstance(fid, file):
            fhandle = fid
        else:
            raise ValueError("Input should either be a file or filename.")

        self.fhandle = fhandle
        self.fname = fhandle.name

        # first determine the endiannes of the file
        self._get_endiannes()
        # get the header
        self._get_header()
        # determine the voxelspacing and origin
        self.voxelspacing = self.header['xlength'] / self.header['nx']
        self.origin = self._get_origin()
        # generate the density
        shape_fields = 'nz ny nx'.split()
        self.shape = [self.header[field] for field in shape_fields]
        self.size = product(self.shape)
        self._get_density()

    def _get_endiannes(self):
        self.fhandle.seek(212)
        m_stamp = hex(ord(self.fhandle.read(1)))
        if m_stamp == '0x44':
            endian = '<'
        elif m_stamp == '0x11':
            endian = '>'
        else:
            raise IOError('Endiannes is not properly set in file. Check the file format.')
        self._endian = endian
        self.fhandle.seek(0)

    def _get_header(self):
        _header = unpack(self._endian + self.HEADER_TYPE, self.fhandle.read(self.HEADER_SIZE))
        self.header = {}
        index = 0
        for n, field in enumerate(self.HEADER_FIELDS):
            end = index + self.HEADER_CHUNKS[n]
            if self.HEADER_CHUNKS[n] > 1:
                self.header[field] = _header[index: end]
            else:
                self.header[field] = _header[index]
            index = end
        self.header['label'] = ''.join(self.header['label'])

    def _get_origin(self):
        start_fields = 'ncstart nrstart nsstart'.split()
        start = [self.header[field] for field in start_fields]
        return [x * self.voxelspacing for x in start]

    def _get_density(self):
        self.density = unpack(self._endian + 'f' * self.size, self.fhandle.read())


class MRCParser(CCP4Parser):
    """Parser for MRC-formatted density files"""

    def _get_origin(self):
        origin = super(MRCParser, self)._get_origin()
        shift_fields = 'xstart ystart zstart'.split()
        shift = [self.header[field] for field in shift_fields]
        return [o + s for o, s in zip(origin, shift)]


#TODO
class XPLORParser(object):
    pass

def product(sequence):
    """Return the product of a sequence."""
    return reduce(mul, sequence, 1)

def nearest_multiple_235(init):
    """Returns the nearest larger number that is a multiple of 2, 3, and 5"""

    MULTIPLES = (2, 3, 5)
    while True:
        n = init
        divided = True
        while divided:
            divided = False
            for multiple in (MULTIPLES):
                quot, rem = divmod(n, multiple)
                if not rem:
                    n = quot
                    divided = True
        if n != 1:
            init += 1
        else:
            return init


def parse_args():
    """Parse the arguments"""

    _DESCRIPTION = \
"""Convert a cryo-EM density to the CNS/XPLOR-format, while expanding the
number of voxels in each direction to be a multiple of 2, 3 and 5"""
    SUPPORTED_FORMATS = ('ccp4', 'map', 'mrc', 'xplor', 'cns')

    p = ArgumentParser(description=_DESCRIPTION)
    p.add_argument('infile', type=file, help='Cryo-EM file to be converted.')
    p.add_argument('outfile', type=FileType('w'), help='Name of output XPLOR-file')
    p.add_argument(
          '-f', '--format', dest='fmt', type=str, choices=SUPPORTED_FORMATS,
          default=None, help='Format of the input file.'
          )
    args = p.parse_args()
    # determine the filetype from the extension, removing the leading dot
    if args.fmt is None:
        args.fmt = splitext(args.infile.name)[1][1:]
    return args


def choose_parser(fmt):
    """Returns the correct parser for the filetype"""
    if fmt in ('ccp4', 'map'):
        parser = CCP4Parser
    elif fmt == 'mrc':
        parser = MRCParser
    elif fmt in ('xplor', 'cns'):
        parser = XPLORParser
    else:
        raise IOError("File format is not recognized.")
    return parser


def write_to_xplor(fid, data):
    """Write the data to an XPLOR formatted density file"""
    starting_voxels = [x // data.voxelspacing for x in data.origin]
    # write header
    fid.write('\n')
    fid.write('{:>8d} !NTITLE\n'.format(1))
    fid.write('REMARK Converted to XPLOR using em2xplor.py\n')
    line_data = [data.shape[2], starting_voxels[0], starting_voxels[0] + data.shape[2] - 1,
        data.shape[1], starting_voxels[1], starting_voxels[1] + data.shape[1] - 1,
        data.shape[0], starting_voxels[2], starting_voxels[2] + data.shape[0] - 1,]
    line_data = [int(x) for x in line_data]

    fid.write(('{:>8d}' * 9 + '\n').format(*line_data))
    line_data = [data.voxelspacing * x for x in data.shape][::-1] + [90] * 3
    fid.write(('{:12.5E}' * 6 + '\n').format(*line_data))
    fid.write('ZYX\n')

    # write density
    for z in xrange(data.shape[0]):
        fid.write('{:>8d}\n'.format(z))
        n = 0
        ind_z = z * data.shape[1] * data.shape[2]
        for y in xrange(data.shape[1]):
            ind_zy = ind_z + y * data.shape[2]
            for x in xrange(data.shape[2]):
                fid.write('{:12.5E}'.format(data.density[ind_zy + x]))
                n += 1
                if n % 6 == 0:
                    fid.write('\n')
        if data.shape[1] * data.shape[2] % 6 > 0:
            fid.write('\n')
    fid.write('{:>8d}\n'.format(-9999))


def expand_235_multiple(orig):
    """Expand map to a multiple of 2, 3 and 5"""
    exp_shape = [nearest_multiple_235(x) for x in orig.shape]
    exp_density = [0] * product(exp_shape)
    for i in xrange(orig.shape[0]):
        ind_e_z = i * exp_shape[1] * exp_shape[2]
        ind_o_z = i * orig.shape[1] * orig.shape[2]
        for j in xrange(orig.shape[1]):
            ind_e_zy = ind_e_z + j * exp_shape[2]
            ind_o_zy = ind_o_z + j * orig.shape[2]
            for k in xrange(orig.shape[2]):
                exp_density[ind_e_zy + k] = orig.density[ind_o_zy + k]
    orig.shape = exp_shape
    orig.density = exp_density
    return orig


def main():
    """Main function for script"""

    args = parse_args()

    # get parser
    parser = choose_parser(args.fmt)
    # parse the file
    em_data = parser(args.infile)
    # expand the density to be a multiple of 2, 3, and 5
    em_data = expand_235_multiple(em_data)
    # write to XPLOR file
    write_to_xplor(args.outfile, em_data)


if __name__ == '__main__':
    main()
