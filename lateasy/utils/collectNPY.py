
import os
import yaml
import argparse
import numpy as np
import pandas as pd
from os.path import join, isdir, isfile
from lateasy.utils.functions import *

parser = argparse.ArgumentParser(description='Collect data from multiple NPY outputs')
parser.add_argument('--pipeconf',  type=str, required=True, help='configuration file')
parser.add_argument('--type', type=str, default='LC', help='collect by type: ROI, LC, SED, LOC')
parser.add_argument('--ts', type=float, default=9, help='minimum ts threshold')
args = parser.parse_args()

# load yaml configurations
with open(args.pipeconf) as f:
    pipeconf = yaml.load(f)

# logging
logname = join(pipeconf['path']['output'], str(__file__).replace('.py','.log'))
log = set_logger(filename=logname, level=pipeconf['execute']['loglevel'])

folder = args.folder
source = args.source
print('collect from ', args.type.upper())
# check folder existance
if not os.path.isdir(folder):
    raise ValueError('directory', folder, 'not found')
# all keys
keys = ('tmin', 'tmax', 'tmin_mjd', 'tmax_mjd', 'phase', 'e_min', 'e_max', 'ts', 'npred', 'flux', 'flux_err', 'flux_ul95', 'flux100_ul95', 'eflux', 'eflux_err', 'eflux100', 'eflux100_err', 'eflux_ul95', 'sens3', 'sens35', 'sens4', 'sens5', 'gal_Prefactor_value', 'gal_Prefactor_error','gal_Index_value', 'gal_Index_error', 'iso_Normalization_value', 'iso_Normalization_error', 'source_Prefactor_value', 'source_Prefactor_error', 'source_Index_value', 'source_Index_error', 'source_RA_value', 'source_RA_error', 'source_DEC_value', 'source_DEC_error', 'filename')
# list of subdir in abspath
bins = []
for d in os.listdir(folder):
    if isdir(join(folder, d)):
        bins.append(d)
bins = sorted(bins)
# sort files
if args.type.upper() not in ('LC', 'SED', 'ROI', 'LOC'):
    raise ValueError('Invalid "type" parameter. Please chose between: roi, sed, lc. Default is ROI.')
# check type
roiname = 'roi2_fit_model.npy'
output = str(args.source.upper()) + '_' + str(args.type.lower()) + '.txt'
if args.type.upper() == 'ROI':
    filename = roiname
    #raise ValueError('Option not implemented yet.')
elif args.type.upper() == 'SED':
    filename = 'sed.npy'
    #raise ValueError('Option not implemented yet.')
elif args.type.upper() == 'LC':
    filename = f'{args.source.lower()}_lightcurve.npy'
elif args.type.upper() == 'LOC':
    filename = f'{args.source.lower()}_loc.npy'
# collect single LC bins data
binfiles = []
for b in bins:
    binfilename = join('.', folder, b, filename)
    outputfile = join('.', folder, b, output)
    roi = join('.', folder, b, roiname)
    if isfile(binfilename):
        binfiles.append(b)
        if args.type.upper() == 'LC':
            collect_lc(binfilename, outputfile, roi, keys, source, relpath=join(folder, b))
        elif args.type.upper() == 'SED':
            collect_sed(binfilename, outputfile=outputfile)
        elif args.type.upper() == 'LOC':
            collect_loc(binfilename, outputfile=outputfile)
        elif args.type.upper() == 'ROI':
            collect_roi(binfilename, outputfile=outputfile)
    else:
        print(binfilename, 'not found.')

print(len(binfiles), len(bins))
# merge single LC bins data
mergefile = folder + '_' + str(args.type.upper()) + '.txt'
merge_data(binfiles, output, mergefile, folder)
print('merge output ', mergefile)

# keep only ts >= 9
ts = args.ts
outfile = mergefile.replace('.txt', '_ts%s.txt' %str(ts))
data = pd.read_csv(mergefile, sep=' ')
data9 = data[data['ts'] >= float(ts)]
print('detections above ts=', ts, ':', len(data9))
data9.to_csv(outfile, sep=' ', header=True, index=False)
print('output above ts threshold ', outfile)
