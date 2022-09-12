import numpy as np
import pandas as pd
from astropy.io import fits
from os.path import join

path = '/data01/projects/IGRJ17354-3255/FERMI/LC/YEARS5j'
month = 'M13B_409708803_412300803' #'M11B_315532802_318124802'

path = '/data01/projects/IGRJ17354-3255/FERMI/LC/YEARS5test'
month = 'NAN2'

# path = '/data01/projects/IGRJ17354-3255/FERMI/TEST/'
# month = 'mkn421'

prefit_file = 'roi1_fit_model.npy' #'fit1.npy' 
fit_file = 'roi2_fit_model.npy' #'fit2.npy'  

prefit = np.load(join(path, month, prefit_file), allow_pickle=True, encoding='latin1', fix_imports=True).flat[0]

fit = np.load(join(path, month, fit_file), allow_pickle=True, encoding='latin1', fix_imports=True).flat[0]

print(prefit.keys())
print(prefit['roi'].keys())

def list_nans(data):
    nan_sources = list()
    for src in data['sources'].keys():
        if str(data['sources'][src]['ts']) == 'nan':
            nan_sources.append(data['sources'][src])
    return nan_sources

nans = list_nans(fit)
print(len(nans))

prefit_nan = 0
prefit_drop = 0
prefit_keep = 0
for src in prefit['sources'].keys():
    if str(prefit['sources'][src]['ts']) == 'nan':
        prefit_nan += 1
    elif prefit['sources'][src]['ts'] < 1:
        prefit_drop += 1
    elif prefit['sources'][src]['ts'] > 1:
        prefit_keep += 1
        print('keep', src, fit['sources'][src]['ts'])

fit_nan = 0
fit_drop = 0
fit_keep = 0
for src in fit['sources'].keys():
    if str(fit['sources'][src]['ts']) == 'nan':
        fit_nan += 1
    elif fit['sources'][src]['ts'] < 1:
        fit_drop += 1
    elif fit['sources'][src]['ts'] > 1:
        fit_keep += 1
        print('kept', src, fit['sources'][src]['ts'])

print(len(prefit['sources']), prefit_drop, prefit_nan, len(fit['sources']), fit_drop, fit_nan)


