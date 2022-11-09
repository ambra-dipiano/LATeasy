# *****************************************************************************
# Copyright (C) 2022 INAF
# This software is distributed under the terms of the BSD-3-Clause license
#
# This software is intended to update the sky region model
# *****************************************************************************

import sys
import yaml
import argparse
from os import system
from os.path import join, basename, isfile
from lateasy.utils.functions import set_logger

parser = argparse.ArgumentParser(description='Fermi/LAT data analysis pipeline')
parser.add_argument('--pipeconf',  type=str, required=True, help='configuration file')
args = parser.parse_args()

# load yaml configurations
with open(args.pipeconf) as f:
    pipeconf = yaml.safe_load(f)

# logging
logname = join(pipeconf['path']['output'], basename(__file__).replace('.py','.log'))
log = set_logger(filename=logname, level=pipeconf['execute']['loglevel'])
log.info('Logging: ' + logname)

# remove script if present
if isfile('make4FGLxml.py'):
    system('rm make4FGLxml.py')

# download script
# newest version: https://fermi.gsfc.nasa.gov/ssc/data/analysis/user/make4FGLxml.py [bug]
try:
    if sys.version_info[0] < 3:
        system('wget https://fermi.gsfc.nasa.gov/ssc/data/analysis/user/make4FGLxml_v01r06.py2')
        system('mv make4FGLxml_v01r06.py2 make4FGLxml.py')
        log.info('Download python2 version 1r06')
    elif int(pipeconf['file']['catalogue'][-6:-4]) < 30: 
        system('wget https://fermi.gsfc.nasa.gov/ssc/data/analysis/user/make4FGLxml_v01r06.py')
        system('mv make4FGLxml_v01r06.py make4FGLxml.py')
        log.info('Download python3 version 1r06')
    else: 
        system('wget https://fermi.gsfc.nasa.gov/ssc/data/analysis/user/make4FGLxml.py')
        system('mv make4FGLxml_v01r06.py make4FGLxml.py')
        log.info('Download python3 latest version')
except Exception as e:
    log.error(e)
    raise SystemError(e)

commandline = "python make4FGLxml.py " + join(pipeconf['path']['data'], pipeconf['file']['catalogue']) + " " + join(pipeconf['path']['data'], pipeconf['file']['observation']) + " -o " + join(pipeconf['path']['models'], pipeconf['file']['inputmodel'])

# normalisazione free
if pipeconf['makemodel']['normfree']:
    commandline += " -N"
# radius
if pipeconf['makemodel']['radius'] != None:
    commandline += " -r " + str(pipeconf['makemodel']['radius'])
# significance
if pipeconf['makemodel']['significance'] != None:
    commandline += " -s " + str(pipeconf['makemodel']['significance'])
# ds9 region
if pipeconf['makemodel']['ds9reg']:
    commandline += " -m True"

log.debug(commandline)
system(commandline)
system('mv ROI_*.reg ' + pipeconf['path']['models'])
system('chmod 777 ' + join(pipeconf['path']['models'], pipeconf['file']['inputmodel']))