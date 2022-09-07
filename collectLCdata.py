import os
import sys
import pandas as pd
from convertMJDandMET import met_to_mjd


folder = sys.argv[1]
if len(sys.argv) > 2:
    ts = sys.argv[2]
else: 
    ts = 9

inpath = f'/data01/projects/IGRJ17354-3255/FERMI/LC/{folder}'
outpath = inpath
#inpath = '/data01/projects/IGRJ17354-3255/FERMI/SED'
#outpath = inpath

infile = os.path.join(inpath, 'igrj17354-3255_lightcurve_fullLC.txt')
outfile = os.path.join(inpath, f'igrj17354-3255_lightcurve_above{ts}ts.txt')

lc = pd.read_csv(infile, sep=' ')
print(len(lc.columns))
if 'Unnamed: 6' in lc.columns and len(lc.columns) > 6:
    lc = lc.drop('Unnamed: 6', axis='columns')
    lc.to_csv(infile, sep=' ', header=True, index=False)
print(lc.columns)
print('rows lc: ', len(lc))

# keep only ts >= 9
lc9 = lc[lc['ts'] >= float(ts)]
print('rows lc9: ', len(lc9))

# add mjd tmin tmax
print('add mjd tmin and tmax')
mjdmin = met_to_mjd(lc9['tmin'])
mjdmax = met_to_mjd(lc9['tmax'])
lc9.insert(2, 'mjdmin', round(mjdmin))
lc9.insert(3, 'mjdmax', round(mjdmax))
print(lc9.keys())

print('save to: ', outfile)
lc9.to_csv(outfile, sep=' ', header=True, index=False)
