# *****************************************************************************
# Copyright (C) 2022 INAF
# This software is distributed under the terms of the BSD-3-Clause license
#
# This software is intended to collect and plot results
# *****************************************************************************

import os
import yaml
import argparse
import pandas as pd
from os.path import join, isdir, isfile, basename
from lateasy.utils.functions import *
from lateasy.utils.plotting import Plotting

parser = argparse.ArgumentParser(description='Collect data from multiple NPY outputs')
parser.add_argument('--pipeconf',  type=str, required=True, help='configuration file')
args = parser.parse_args()

# load yaml configurations
with open(args.pipeconf) as f:
    pipeconf = yaml.safe_load(f)

# logging
logname = join(pipeconf['path']['output'], basename(__file__).replace('.py','.log'))
log = set_logger(filename=logname, level=pipeconf['execute']['loglevel'])
log.info('Logging: ' + logname)

folder = pipeconf['path']['output']
source = pipeconf['target']['4FGLname']
log.info('collect from ' + pipeconf['postprocessing']['collect'].upper())
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
if pipeconf['postprocessing']['collect'].upper() not in ('LC', 'SED', 'ROI', 'LOC'):
    raise ValueError('Invalid "type" parameter. Please chose between <ROI|SED|LC|LOC>')
# check type
roiname = 'roi2_fit_model.npy'
output = str(source.upper()) + '_' + str(pipeconf['postprocessing']['collect'].lower()) + '.txt'
if pipeconf['postprocessing']['collect'].upper() == 'ROI':
    filename = roiname
    #raise ValueError('Option not implemented yet.')
elif pipeconf['postprocessing']['collect'].upper() == 'SED':
    filename = 'sed.npy'
    #raise ValueError('Option not implemented yet.')
elif pipeconf['postprocessing']['collect'].upper() == 'LC':
    filename = source.lower() + '_lightcurve.npy'
elif pipeconf['postprocessing']['collect'].upper() == 'LOC':
    filename = source.lower() +'_loc.npy'
filename = filename.replace(' ', '_')
log.info('Collect from:' + filename)
# collect single LC bins data
binfiles = []
for b in bins:
    binfilename = join(folder, b, filename)
    outputfile = join(folder, b, output)
    roi = join(folder, b, roiname)
    if isfile(binfilename):
        binfiles.append(b)
        if pipeconf['postprocessing']['collect'].upper() == 'LC':
            collect_lc(binfilename, outputfile, roi, keys, source, relpath=join(folder, b))
        elif pipeconf['postprocessing']['collect'].upper() == 'SED':
            collect_sed(binfilename, outputfile=outputfile)
        elif pipeconf['postprocessing']['collect'].upper() == 'LOC':
            collect_loc(binfilename, outputfile=outputfile)
        elif pipeconf['postprocessing']['collect'].upper() == 'ROI':
            collect_roi(binfilename, outputfile=outputfile)
    else:
        log.warning(binfilename + ' not found.')

# merge single LC bins data
mergefile = join(folder, basename(folder) + '_' + str(pipeconf['postprocessing']['collect'].upper()) + '.txt')
merge_data(binfiles, output, mergefile, folder)
log.info('merge output: ' + mergefile)

# keep only ts >= 9
ts = pipeconf['postprocessing']['mints']
detfile = mergefile.replace('.txt', '_ts%s.txt' %str(ts))
data = pd.read_csv(mergefile, sep=' ')
data_above = data[data['ts'] >= float(ts)]
log.info('detections above ts=' + str(ts) + ': ' + str(len(data_above)))
data_above.to_csv(detfile, sep=' ', header=True, index=False)
log.info('output above ts threshold: ' + detfile)

if pipeconf['postprocessing']['collect'].lower() == 'lc' and pipeconf['postprocessing']['plot']:
    filename_full = mergefile
    filename_bin = pipeconf['target']['4FGLname'] + '_lightcurve_collected.txt'
    path = pipeconf['path']['output']

    # list of subdir in path
    bins = []
    for d in os.listdir(path):
        if os.path.isdir(path + '/' + d):
            bins.append(d)
    bins = sorted(bins)

    # plot monthly
    log.info('Plot single lc')
    plotname_bin = filename_bin.replace('.txt', '.png')
    for b in bins:
        filepath = os.path.join(path, b, filename_bin)
        if os.path.exists(filepath):
            png = Plotting(args.pipeconf)
            data = png.load_data(filepath)
            png.plot_lc(data, plotname_bin)
        else:
            print('bin', b, 'missing LC ==> skipped')

    # plot year
    log.info('Plot merged lc')
    plotname_full = filename_full.replace('.txt', '.png')
    filepath = os.path.join(path, filename_full)
    png = Plotting(args.pipeconf)
    data = png.load_data(filepath)
    png.plot_lc(data, plotname_full)

else:
    log.warning('Plotting skipped. Not implemented for ' + pipeconf['postprocessing']['collect'].upper())
