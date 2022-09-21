import numpy as np


filename = '/data01/projects/IGRJ17354-3255/FERMI/folded8/2020/100-10000/BIN4/SUM/roi2.npy'
data = np.load(filename, allow_pickle=True, encoding='latin1', fix_imports=True).flat[0]
print(sorted(data.keys()))


for src in data['sources'].keys():
    if src == 'IGRJ17354-3255':
        print('-----')
        print(src)
        print('TS = ', data['sources'][src]['ts'])
        print('FLUX = ', data['sources'][src]['flux'])
        print('FLUX_ERR = ', data['sources'][src]['flux_err'])
        print('FLUX_UL95 = ', data['sources'][src]['flux_ul95'])
        #print(sorted(data['sources'][src].keys()))
        print(data['sources'][src]['param_names'])
        print(data['sources'][src]['param_values'])
        print(data['sources'][src]['param_errors'])

print(sorted(data['sources']['gll_iem_v07'].keys()))
print(data['sources']['iso_P8R3_SOURCE_V2_v1']['param_errors'][0])
print(data['sources']['iso_P8R3_SOURCE_V2_v1']['spectral_pars']['Normalization']['error'])
