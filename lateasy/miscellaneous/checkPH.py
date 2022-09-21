from astropy.io import fits

path = '/data01/projects/IGRJ17354-3255/FERMI/FERMI_DATA/'
files = list()
for i in range(9):
    files.append('L20083004141749F5D3C158_PH%02d.fits' %i)

for f in files:
    hdul = fits.open(path + f)
    print(f)
    try: 
        key = hdul[1].header['NDSKEYS']
    except:
        print(f, 'does not have "NDSKEYS" keyword in "EVENTS" header')