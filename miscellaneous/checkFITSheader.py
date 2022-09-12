from astropy.io import fits

filename = '/data01/projects/IGRJ17354-3255/FERMI/FERMI_DATA/SC00.fits'

with fits.open(filename) as hdul:
    print(hdul.info())
    print('\n----------------------------\n')
    hdr0 = hdul[0].header
    hdr1 = hdul[1].header
    data0 = hdul[0].data
    data1 = hdul[1].data


keyword = 'NDSKEYS'
print(hdr0.values)
print('\n----------------------------\n')
print(hdr1.values)
print('\n----------------------------\n')
print('\n----------------------------\n')
print(data0)
print('\n----------------------------\n')
print(data1.columns)
print('\n----------------------------\n')
print('\n----------------------------\n')
print('Is', keyword, 'in headers?', keyword in hdr0, keyword in hdr1)
print('Is', keyword, 'in columns?', keyword in data1.columns.names)