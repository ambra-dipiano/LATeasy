# RUNNING THE SCRIPT:
# $ python collectLOC.py YEARS_FOLDER
# example:
# $ python collecLOC.py YEARS5g019

import numpy as np
import os
import sys

def collect_data_loc(filename, filename2, columns=('ra', 'ra_err', 'dec', 'dec_err', 'ra_preloc', 'dec_preloc', 'pos_offset', 'pos_r95')):
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

def merge_loc(bins, filename_merged, filename_bin, abspath):
    mf = open(abspath + filename_merged, 'w+') 
    for i, b in enumerate(bins):
        with open(abspath + '/' + b + '/' + filename_bin) as f:
            if i == 0:
                lines = f.readlines()
            else:
                lines = f.readlines()[1:]
            for line in lines:
                mf.write(line)
    mf.close()

# -------------------------------------------

filename = 'igrj17354-3255_loc.npy'
if len(sys.argv) > 1:
    folder = str(sys.argv[1])
else:
    folder = 'YEARS5k'
if len(sys.argv) > 2:
    abspath = str(sys.argv[2]) + folder + '/'
else:
    abspath = '/data01/projects/IGRJ17354-3255/FERMI/LC/' + folder + '/'
# check folder existance
if not os.path.isdir(abspath):
    raise ValueError('directory', folder, 'does not exist in', abspath.replace(folder+'/',''))
# list of subdir in abspath
logname = abspath.replace(folder+'/','') + folder + '_collectLOC.log'
print('Logging ---> ', logname)
logfile = open(logname, 'w+')
logfile.write('### collect localisation from ' + str(folder))
bins = []
for d in os.listdir(abspath):
    if os.path.isdir(abspath + '/' + d):
        bins.append(d)
bins = sorted(bins)
rm_bin = []
# collect single LC bins data
keys = ('ra', 'ra_err', 'dec', 'dec_err', 'ra_preloc', 'dec_preloc', 'pos_offset', 'pos_r95')
for b in bins:
    filename1 = abspath + b + '/' + filename
    filename2 = filename1.replace('.npy', '_collected.txt')
    if not os.path.exists(filename1):
        # logfile.write('\nmissing ' + str(filename1))
        rm_bin.append(b)
        continue
    collect_data_loc(filename1, filename2, columns=keys, period=folder)
# logfile.write('\n\n# LOC data collection will skip the following folders:')
# for b in rm_bin:
#     logfile.write('\n' + str(b))
# remove mising LC bins
if len(rm_bin) > 0:
    for i, b in enumerate(rm_bin):
        bins.remove(b)
# fonders which have localisation
logfile.write('\n\n# LOC data collection from the following folders:')
for b in bins:
    logfile.write('\n' + str(b))
# merge single LC bins data
filename_merged = filename.replace('.npy', '_fullLOC.txt')
filename_bin = filename.replace('.npy', '_collected.txt')
merge_loc(bins, filename_merged, filename_bin, abspath)
logfile.write('\n\n# merged collected LOC in file ' + str(abspath + filename_merged) + '\n')
logfile.close()