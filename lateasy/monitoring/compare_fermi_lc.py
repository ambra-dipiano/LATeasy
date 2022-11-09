# *****************************************************************************
# Copyright (C) 2022 INAF
# This software is distributed under the terms of the BSD-3-Clause license
#
# This software is intended to compare lightcurves with the official Fermi ones
# from https://fermi.gsfc.nasa.gov/ssc/data/access/lat/msl_lc/ 
# *****************************************************************************

import yaml
import argparse
from os.path import join, basename
from lateasy.utils.functions import *
from lateasy.utils.plotting import Plotting

parser = argparse.ArgumentParser(description='Collect data from multiple NPY outputs')
parser.add_argument('--pipeconf',  type=str, required=True, help='configuration file')
parser.add_argument('--fermi', type=str, required=True, help='absolute path to fermi official lightcurve FITS file')
args = parser.parse_args()

# load yaml configurations
with open(args.pipeconf) as f:
    pipeconf = yaml.safe_load(f)

# logging
logname = join(pipeconf['path']['output'], basename(__file__).replace('.py','.log'))
log = set_logger(filename=logname, level=pipeconf['execute']['loglevel'])
log.info('Logging: ' + logname)

# get data files
folder = pipeconf['path']['output']
filename = join(folder, basename(folder) + '_' + str(pipeconf['postprocessing']['collect'].upper()) + '.txt')
log.debug('Fermi LC: ' + args.fermi)
log.debug('Comparison with: ' + filename)

# plot
plotname = filename.replace('.txt', '_compareLAT.png')
png = Plotting(args.pipeconf)
data = png.load_data(filename)
fermi_data = png.load_data_lc_from_fits(args.fermi)
png.compare_lc_full_range(data, fermi_data, plotname)

