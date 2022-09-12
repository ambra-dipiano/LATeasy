
import numpy as np
import os
import sys

def check_colnames(filename):
    data = np.load(filename, allow_pickle=True, encoding='latin1', fix_imports=True).flat[0]
    print(sorted(data.keys()))
    return data


filename = 'igrj17354-3255_lightcurve.npy'
if len(sys.argv) > 1:
    folder = str(sys.argv[1])
else:
    folder = 'M10B_294278402_296870402'
if len(sys.argv) > 2:
    abspath = str(sys.argv[1])
else:
    abspath = '/data01/projects/IGRJ17354-3255/FERMI/LC/YEARS5g019'
filename = abspath + '/' + folder + '/' + filename
cols = check_colnames(filename)

# print(len(cols['param_names']))
# print(cols['param_values'][:3])
# print(len(cols['param_errors']))
# print(cols['param_values_fixed'])
# print(len(cols['flux']))

# for i in range(len(cols['flux'])):
#     print(cols['param_names'][i][0])

