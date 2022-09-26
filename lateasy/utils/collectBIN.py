# RUNNING THE SCRIPT:
# $ python collectLOC.py YEAR/BIN/file.npy -t <LC/SED/ROI/LOC>


import os
import argparse
import numpy as np
from os.path import abspath

parser = argparse.ArgumentParser(description='Collect data from a single NPY output')
parser.add_argument('-f', '--file', type=str, required=True, help='the NPY file completed with path')
parser.add_argument('-t', '--type', type=str, required=True, help='type of the NPY: roi, sed, lc, loc, fit')
parser.add_argument('--source', type=str, default='IGRJ17354-3255', help='source name')
args = parser.parse_args()

# lightcurves
def collect_lc(filename, columns=('tmin', 'tmax', 'ts', 'flux', 'flux_err', 'flux_ul95')):
    filename2 = filename.replace('.npy', '_collected.txt')
    if os.path.isfile(filename2):
        os.remove(filename2)
    print('Data will be saved in ', filename2)
    data = np.load(filename, allow_pickle=True, encoding='latin1', fix_imports=True).flat[0]
    if len(columns) == 0:
        raise ValueError('Please set columns to a list of keys.')
    rows = len(data[columns[0]])
    # header of output file
    hdr = str()
    for key in columns:
        hdr += str(key) + ' '
    with open(filename2, 'w+') as f:
        f.write(hdr + '\n')
        f.close()
    for i in range(rows):
        line = str()
        for key in columns:
            line += str(data[key][i]) + ' '
        with open(filename2, 'a') as f:
            f.write(line + '\n')
            f.close()

# localisations
def collect_loc(filename, columns=('ra', 'ra_err', 'dec', 'dec_err', 'ra_preloc', 'dec_preloc', 'pos_offset', 'pos_r95')):
    filename2 = filename.replace('.npy', '_collected.txt')
    if os.path.isfile(filename2):
        os.remove(filename2)
    print('Data will be saved in ', filename2)
    data = np.load(filename, allow_pickle=True, encoding='latin1', fix_imports=True).flat[0]
    if columns == 'all':
        raise ValueError('columns="all" is not implemented yet. Please set the parameter to a list of keys.')
    # header of output file
    hdr = str()
    hdr += 'month '
    for key in columns:
        hdr += str(key) + ' '
    with open(filename2, 'w+') as f:
        f.write(hdr + '\n')
        f.close()
    line = str()
    for key in columns:
        line += str(data[key]) + ' '
    with open(filename2, 'a') as f:
        f.write(line + '\n')
        f.close()

# sed
def collect_sed(filename, columns=('e_min', 'e_max', 'ts', 'flux', 'flux_err', 'flux_ul95', 'Prefactor', 'Index', 'Scale'), par_names = ('Prefactor', 'Index', 'Scale')):
    filename2 = filename.replace('.npy', '_collected.txt')
    if os.path.isfile(filename2):
        os.remove(filename2)
    print('Data will be saved in ', filename2)
    data = np.load(filename, allow_pickle=True, encoding='latin1', fix_imports=True).flat[0]
    pars = ('param_values', 'param_errors')
    suffix = ('', '_err')
    hdr = str()
    for key in columns:
        if key in par_names:
            for i, p in enumerate(pars):
                hdr += str(key) + str(p.replace('param', '')) + ' '
        else:
            hdr += str(key) + ' '
    with open(filename2, 'w+') as f:
        f.write(hdr + '\n')
        f.close()
    for n in range(len(data[columns[0]])):
        line = str()
        for key in columns:
            if key in par_names:
                for p in pars:
                    index = par_names.index(key)
                    line += str(data[p][index]) + ' '
            else:
                line += str(data[key][n]) + ' '
        with open(filename2, 'a') as f:
            f.write(line + '\n')
            f.close()

# roi
def collect_roi(filename, src='IGRJ17354-3255', columns=('ts', 'flux', 'flux_err', 'flux_ul95', 'Prefactor', 'Index', 'Scale'), par_names = ('Prefactor', 'Index', 'Scale')):
    filename2 = filename.replace('.npy', '_collected.txt')
    if os.path.isfile(filename2):
        os.remove(filename2)
    print('Data will be saved in ', filename2)
    data = np.load(filename, allow_pickle=True, encoding='latin1', fix_imports=True).flat[0]
    pars = ('param_values', 'param_errors')
    suffix = ('', '_err')
    hdr = str()
    for key in columns:
        if key in par_names:
            for p in pars:
                hdr += str(key) + str(p.replace('param', '')) + ' '
        else:
            hdr += str(key) + ' '
    with open(filename2, 'w+') as f:
        f.write(hdr + '\n')
        f.close()
    line = str()
    for key in columns:
        if key in par_names:
            for p in pars:
                index = par_names.index(key)
                line += str(data['sources'][src][p][index]) + ' '
        else:
            line += str(data['sources'][src][key]) + ' '
    with open(filename2, 'a') as f:
        f.write(line + '\n')
        f.close()


filename = args.file
if not os.path.isfile(abspath(filename)):
    raise ValueError(f'File not found: {filename}')

if args.type == 'sed':
    collect_sed(filename)
elif args.type == 'lc':
    collect_lc(filename)
elif args.type == 'loc':
    collect_loc(filename)
elif args.type in ('roi', 'fit'):
    collect_roi(filename, src=args.source)

filename2 = filename.replace('.npy', '_collected.txt')
os.system('cat ' + filename2)

