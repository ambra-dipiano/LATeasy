# *****************************************************************************
# Copyright (C) 2022 INAF
# This software is distributed under the terms of the BSD-3-Clause license
#
# This software is intended to rename slurm outputs as directory logging
# *****************************************************************************

import yaml
import argparse
from os import listdir, system
from os.path import isfile, join, basename
from lateasy.utils.functions import set_logger

parser = argparse.ArgumentParser(description='Rename slurm jobs')
parser.add_argument('--pipeconf',  type=str, required=True, help='configuration file')
args = parser.parse_args()

# load yaml configurations
with open(args.pipeconf) as f:
    pipeconf = yaml.safe_load(f)

# logging
logname = join(pipeconf['path']['output'], basename(__file__).replace('.py','.log'))
log = set_logger(filename=logname, level=pipeconf['execute']['loglevel'])
log.info('Logging: ' + logname)


path = pipeconf['path']['output']
logs = [f for f in listdir(path) if 'slurm' in f and 'index' not in f and pipeconf['slurm']['name'] not in f and isfile(join(path, f))]

# write index
indexfile = join(path, 'slurm-index.txt')
print(indexfile)
hdr = 'slurm-id.out month tstart tstop\n'
with open(indexfile, 'w+') as f:
    f.write(hdr)
for f in logs:
    line = open(join(path,f), 'r').readlines()[0]
    month = line[31:-7]
    tstart = month[5:14]
    tstop = month[15:]
    print(f, month, tstart, tstop)
    with open(indexfile, 'a') as index:
        index.write(str(str(f) + ' ' + month + ' ' + tstart + ' ' + tstop + '\n'))

# rename slurm
for i, f in enumerate(logs):
    if i == len(logs)-1:
        break
    else:
        line = open(join(path,f), 'r').readlines()[0]
        month = line[31:-7]
        system('mv ' + str(join(path,f)) + ' ' + str(join(path, 'slurm-%s.out' %month)))

logs = [f for f in listdir(path) if 'slurm' in f and 'index' not in f and 'M' in f and isfile(join(path, f))]
# write index
indexfile = join(path, 'igrMonthsIndex.out')
print(indexfile)
hdr = 'slurm-id.out month tstart tstop\n'
with open(indexfile, 'w+') as f:
    f.write(hdr)
for f in logs:
    line = open(join(path,f), 'r').readlines()[0]
    month = line[31:-7]
    tstart = month[5:14]
    tstop = month[15:]
    print(f, month, tstart, tstop)
    with open(indexfile, 'a') as index:
        index.write(str(str(f) + ' ' + month + ' ' + tstart + ' ' + tstop + '\n'))
