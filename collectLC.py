# RUNNING THE SCRIPT:
# $ python collectLC.py YEARS_FOLDER
# example:
# $ python collecLC.py YEARS5g019

import os
import sys
import numpy as np

def collect_data_lc(filename, filename2, columns=('tmin', 'tmax', 'ts', 'flux', 'flux_err', 'flux_ul95'), param=('Prefactor', 'Index', 'Scale')):
    data = np.load(filename, allow_pickle=True, encoding='latin1', fix_imports=True).flat[0]
    if columns == 'all':
        raise ValueError('columns="all" is not implemented yet. Please set the parameter to a list of keys.')
    rows = len(data[columns[0]])
    # header of output file
    hdr = str()
    for key in columns:
        hdr += str(key) + ' '
    for key in param:
        hdr += str(key) + ' ' + str(key) + '_error '
    with open(filename2, 'w+') as f:
        f.write(hdr + '\n')
        f.close()
    for i in range(rows):
        line = str()
        for key in columns:
            line += str(data[key][i]) + ' '
        for key in range(len(param)):
            line += str(data['param_values'][i][key]) + ' ' + str(data['param_errors'][i][key]) + ' '
        with open(filename2, 'a') as f:
            f.write(line + '\n')
            f.close()

def merge_lc(bins, filename_merged, filename_bin, abspath):
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


if __name__ == "__main__":

    filename = 'igrj17354-3255_lightcurve.npy'
    if len(sys.argv) > 1:
        folder = str(sys.argv[1])
    else:
        folder = 'YEARS5h'
    if len(sys.argv) > 2:
        abspath = str(sys.argv[2]) + folder + '/'
    else:
        abspath = '/data01/projects/IGRJ17354-3255/FERMI/LC/' + folder + '/'
    # check folder existance
    if not os.path.isdir(abspath):
        raise ValueError('directory', folder, 'does not exist in', abspath.replace(folder+'/',''))
    # list of subdir in abspath
    logname = abspath.replace(folder+'/','') + folder + '_collectLC.log'
    print('Logging ---> ', logname)
    logfile = open(logname, 'w+')
    logfile.write('### collect lightcurves from ' + str(folder))
    bins = []
    for d in os.listdir(abspath):
        if os.path.isdir(abspath + '/' + d):
            bins.append(d)
    bins = sorted(bins)
    rm_bin = []
    # collect single LC bins data
    keys = ('tmin', 'tmax', 'ts', 'flux', 'flux_err', 'flux_ul95')
    for b in bins:
        filename1 = abspath + b + '/' + filename
        filename2 = filename1.replace('.npy', '_collected.txt')
        if not os.path.exists(filename1):
            logfile.write('\nmissing ' + str(filename1))
            rm_bin.append(b)
            continue
        collect_data_lc(filename1, filename2, columns=keys)
    logfile.write('\n\n# LC data collection will skip the following folders:')
    for b in rm_bin:
        logfile.write('\n' + str(b))
    # remove mising LC bins
    if len(rm_bin) > 0:
        for i, b in enumerate(rm_bin):
            bins.remove(b)
    # merge single LC bins data
    filename_merged = filename.replace('.npy', '_fullLC.txt')
    filename_bin = filename.replace('.npy', '_collected.txt')
    merge_lc(bins, filename_merged, filename_bin, abspath)
    logfile.write('\n\n# merged collected LC in file ' + str(abspath + filename_merged) + '\n')
    logfile.close()