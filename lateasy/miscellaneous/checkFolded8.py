import os
from os import listdir, system
from os.path import isdir, join
from astropy.io import fits

path = '/data01/projects/IGRJ17354-3255/FERMI/folded8'
tests = [f for f in listdir(path) if 'BIN5_' in f and isdir(join(path, f))]
tests = sorted(tests)

for test in tests:
    with fits.open(join(path, test, 'ltcube_00.fits')) as hdul:
        print(test)
        print('dstart', hdul[1].header['DATE-OBS'])
        print('dstop', hdul[1].header['DATE-END'])        
        print('tstart', hdul[1].header['TSTART'])
        print('tstop', hdul[1].header['TSTOP'])
        print('exp max', hdul[1].data['COSBINS'].max())
        print('wexp max', hdul[2].data['COSBINS'].max())
        print('\n------------\n')