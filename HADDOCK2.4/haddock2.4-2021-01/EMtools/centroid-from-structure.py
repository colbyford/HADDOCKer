from argparse import ArgumentParser
from collections import defaultdict

# records
MODEL = 'MODEL '
ATOM = 'ATOM  '
HETATM = 'HETATM'
TER = 'TER   '

MODEL_LINE = 'MODEL ' + ' ' * 4 + '{:>4d}\n'
ENDMDL_LINE = 'ENDMDL\n'
TER_LINE = 'TER   ' + '{:>5d}' + ' ' * 6 + '{:3s}' + ' ' + '{:1s}' + \
        '{:>4d}' + '{:1s}' + ' ' * 53 + '\n'
ATOM_LINE = '{:6s}' + '{:>5d}' + ' ' + '{:4s}' + '{:1s}' + '{:3s}' + ' ' + \
        '{:1s}' + '{:>4d}' + '{:1s}' + ' ' * 3 + '{:8.3f}' * 3 + '{:6.2f}' * 2 + \
        ' ' * 10 + '{:>2s}' + '{:2s}\n'
END_LINE = 'END   \n'

ATOM_DATA = ('record id name alt resn chain resi i x y z q b ' \
        'e charge').split()
TER_DATA = 'id resn chain resi i'.split()


def parse_pdb(infile):
    """Parser for PDB file, returning a defaultdict"""

    if isinstance(infile, file):
        f = infile
    elif isinstance(infile, str):
        f = open(infile)
    else:
        raise TypeError('Input should be either a file or string.')

    pdb = defaultdict(list)
    model_number = 1
    for line in f:
        record = line[:6]
        if record in (ATOM, HETATM):
            pdb['model'].append(model_number)
            pdb['record'].append(record)
            pdb['id'].append(int(line[6:11]))
            pdb['name'].append(line[12:16].strip())
            pdb['alt'].append(line[16])
            pdb['resn'].append(line[17:20].strip())
            pdb['chain'].append(line[21])
            pdb['resi'].append(int(line[22:26]))
            pdb['i'].append(line[26])
            pdb['x'].append(float(line[30:38]))
            pdb['y'].append(float(line[38:46]))
            pdb['z'].append(float(line[46:54]))
            pdb['q'].append(float(line[54:60]))
            pdb['b'].append(float(line[60:66]))
            pdb['e'].append(line[76:78].strip())
            pdb['charge'].append(line[78: 80].strip())
        elif record == MODEL:
            model_number = int(line[10: 14])
    f.close()
    return pdb


def average(sequence):
    return sum(sequence) / len(sequence)


class Arguments(object):
    """Simple wrapper for catching arguments"""

    parser = ArgumentParser()
    parser.add_argument('pdb', type=file, help="PDB-file for which centroid will be determined")

    def __init__(self):
        for arg, value in vars(self.parser.parse_args()).iteritems():
            setattr(self, arg, value)


def main():
    args = Arguments()
    pdb = parse_pdb(args.pdb)
    centroid = [average(pdb[coor]) for coor in 'x y z'.split()]
    print 'Parsed file: ', args.pdb.name
    print 'Corresponding centroid (x, y, z):'
    print ('{:.2f}   ' * 3).format(*centroid)
    # write out a BILD file for Chimera to visualize the centroid
    # see https://www.cgl.ucsf.edu/chimera/docs/UsersGuide/bild.html
    with open('centroid.bld', 'w') as f:
        line = ' '.join(['.sphere'] + ['{:.2f}'] * 3 + ['3\n'])
        f.write(line.format(*centroid))


if __name__ == '__main__':
    main()
