# *****************************************************************************
# Copyright (C) 2022 INAF
# This software is distributed under the terms of the BSD-3-Clause license
#
# This software is intended to update the fermipy fermiconfuration to run a  
# folded analysis 
# *****************************************************************************

import argparse
import yaml
from os.path import join, isfile
from lateasy.utils.functions import set_logger, load_data

parser = argparse.ArgumentParser(description='Fermi/LAT data analysis pipeline')
parser.add_argument('--pipeconf',  type=str, required=True, help='fermiconfuration file')
parser.add_argument('--fermiconf',  type=str, required=True, help='fermiconfuration file')
args = parser.parse_args()

# load yaml fermiconfurations
with open(args.pipeconf) as f:
    pipeconf = yaml.load(f)
with open(args.fermiconf) as f:
    fermiconf = yaml.load(f)

# logging
logname = join(pipeconf['path']['output'], str(__file__).replace('.py','.log'))
log = set_logger(filename=logname, level=pipeconf['execute']['loglevel'])

# folded intervals
timetable = join(pipeconf['path']['data'], pipeconf['file']['folded8'])
if not isfile(timetable):
    raise ValueError('times table not found') 
times = load_data(timetable)
tstart = times['tstart']
tstop = times['tstop']

# update fermiconf
if pipeconf['folded']['bins'] == 0:
    pipeconf['folded']['bins'] = int(len(times) - 1)
filters = str(fermiconf['selection']['filter']).strip()
filters += '&&'
for i in range(pipeconf['folded']['bins']):
    filters += '(START>=' + str(tstart[i]).strip() + '&&STOP<=' + str(tstop[i]).strip() + ')'
    if i+1 == pipeconf['folded']['bins']:
        break
    else:
        filters += '||'
fermiconf['selection']['filter'] = "%s" %filters
fermiconf['selection']['tmin'] = pipeconf['slurm']['tmin'] 
fermiconf['selection']['tmax'] = pipeconf['slurm']['tmax'] 
fermiconf['fileio']['outdir'] = pipeconf['path']['output']
del fermiconf['selection']['tmax']
del fermiconf['selection']['tmin']

# save new fermiconfig
with open(args.fermiconf, 'w+') as f:
    yaml.dump(fermiconf, f, default_flow_style=False)

# update pipeconf
pipeconf['execute']['sed'] = False
pipeconf['execute']['loc'] = False

# save new pipeconf
with open(args.fermiconf, 'w+') as f:
    yaml.dump(fermiconf, f, default_flow_style=False)
