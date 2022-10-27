import os
import yaml
import argparse
import pandas as pd
from os import listdir
from os.path import join, basename, isfile
from lateasy.utils.functions import set_logger

parser = argparse.ArgumentParser(description='Collect data from multiple NPY outputs')
parser.add_argument('--pipeconf',  type=str, required=True, help='pipeline configuration file')
parser.add_argument('--fermiconf',  type=str, required=True, help='fermipy configuration file')
args = parser.parse_args()

# load yaml configurations
with open(args.pipeconf) as f:
    pipeconf = yaml.safe_load(f)
with open(args.fermiconf) as f:
    fermiconf = yaml.safe_load(f)

# logging
logname = join(pipeconf['path']['output'], basename(__file__).replace('.py','.log'))
log = set_logger(filename=logname, level=pipeconf['execute']['loglevel'])
tmin = fermiconf['selection']['tmin']
tmax = fermiconf['selection']['tmax']

daysfile = join(pipeconf['path']['output'], pipeconf['file']['folded8'])
days = pd.read_csv(daysfile, sep=' ')

dayspath = pipeconf['path']['output']
daysfile = os.path.join(dayspath, 'igrDaysMET_removed.out')

days = pd.read_csv(daysfile, sep=' ')

foldedpath = pipeconf['path']['datafold']
files = [f for f in listdir(foldedpath) if isfile(join(foldedpath, f))] 

for f in files:
    infile = os.path.join(foldedpath, f)
    bins = pd.read_csv(infile, sep=' ', names=['tstart', 'tstop'])

    # ------------------------------------ bad days

    log.debug(str((days['stop_met']-days['start_met'])[0]))
    log.debug(str((bins['tstop']-bins['tstart'])[0]))

    tstart, tstop = list(), list()
    for i, b in bins.iterrows():
        for j, day in days.iterrows():
            if b[0] <= day[0] and b[1] >= day[1] :
                tstart.append(b[0])
                tstop.append(b[1])
                break
            elif b[0] <= day[0] <= b[1] or b[0] <= day[1] <= b[1]:
                tstart.append(b[0])
                tstop.append(b[1])
                break

    log.debug(str(len(days)) + ' ' + str(len(bins)) + str(len(tstart)))

    data_dict = {'tstart': tstart, 'tstop': tstop} 
    data = pd.DataFrame(data_dict)
    data.drop_duplicates(inplace=True)

    outfile = os.path.join(foldedpath, f.replace('.txt', '_removed.txt'))
    data.to_csv(outfile, sep=' ', header=True, index=False)
    log.info('rows in dropped data: ' + str(len(data)))

    keep = pd.concat([bins, data]).drop_duplicates(keep=False)
    outfile = os.path.join(foldedpath, f.replace('.txt', '_kept.txt'))
    keep.to_csv(outfile, sep=' ', header=True, index=False)
    log.info('rows in keep data: ' + str(len(keep)))
