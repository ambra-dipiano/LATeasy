
import numpy as np
import os
import sys

def check_colnames(filename):
    data = np.load(filename, allow_pickle=True, encoding='latin1', fix_imports=True).flat[0]
    print(sorted(data.keys()))

if __name__ == "__main__":

    filename = 'igrj17354-3255_loc.npy'
    if len(sys.argv) > 1:
        folder = str(sys.argv[1])
    else:
        folder = 'M13B_381196803_383788803'
    if len(sys.argv) > 2:
        abspath = str(sys.argv[1])
    else:
        abspath = '/data01/projects/IGRJ17354-3255/FERMI/LC/YEARS5g019'
    filename = abspath + '/' + folder + '/' + filename
    check_colnames(filename)