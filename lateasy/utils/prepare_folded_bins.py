# *****************************************************************************
# Copyright (C) 2022 INAF
# This software is distributed under the terms of the BSD-3-Clause license
#
# This software converts MJD time intervals in MET
# *****************************************************************************

import yaml
import argparse
import pandas as pd
import numpy as np
from os.path import join
from lateasy.utils.functions import mjd_to_met, set_logger

parser = argparse.ArgumentParser(description='Collect data from multiple NPY outputs')
parser.add_argument('--pipeconf',  type=str, required=True, help='configuration file')
parser.add_argument('--data', type=str, required=True, help='basename of MJD data file')
parser.add_argument('--min-cts', type=int, default=100, help='minumum counts in bin')
args = parser.parse_args()

# load yaml configurations
with open(args.pipeconf) as f:
    pipeconf = yaml.load(f)

# logging
logname = join(pipeconf['path']['output'], str(__file__).replace('.py','.log'))
log = set_logger(filename=logname, level=pipeconf['execute']['loglevel'])

# file names
path = pipeconf['path']['data']
infile = join(path, args.data)
outfile = join(path, args.data + '.MET')

# load data
lc=pd.read_csv(infile, names=['time', 'f1', 'f2', 'f3', 'f4', 'exp', 'cts'], sep=' ')
start_day_mjd = np.array(lc['time'] - 0.5) 
stop_day_mjd = np.array(lc['time'] + 0.5)

# round days
start_day_met = np.around(mjd_to_met(start_day_mjd))
stop_day_met = np.around(mjd_to_met(stop_day_mjd))
exp = np.array(lc['exp'])
cts = np.array(lc['cts'])

# save data
data_dict = {'start_met': start_day_met, 'stop_met': stop_day_met, 'exposure': exp, 'counts': cts} 
data = pd.DataFrame(data_dict)
data.to_csv(outfile, sep=' ', header=True, index=False)
log.info('rows in data: ' + (str(len(data))))

# keep only bins above 100 counts
filtered = data[cts > args.min_cts]
log.info('filter days above ' + args.min_cts + ' counts')
log.info('remaining rows: ' + str(len(filtered)))
log.info('min exposure in filtered: ' + str(filtered["exposure"].min()))

outfile = outfile.replace('.MET', '.MET_filtered')
filtered.to_csv(outfile, sep=' ', header=True, index=False)

bad_days = data[cts < args.min_cts]
log.info('remove days below ' + args.min_cts + ' counts')
log.info('removed rows: ' + str(len(bad_days)))

outfile = outfile.replace('.MET', '.MET_removed')
bad_days.to_csv(outfile, sep=' ', header=True, index=False)

# --------------------------------------------------- folded periods

log.info('------------- use folded time intervals -------------')

infile = join(path, args.data + '.MET')
outfile = outfile.replace('.MET', '.MET_failed')

months = pd.read_csv(infile, sep=' ', names=['start', 'stop'])

failed = data[cts < 100]
m_start = list()
m_stop = list()
for j, month in months.iterrows():
    for i, day in failed.iterrows():
        if month[0] <= day[0] <= month[1]:
            m_start.append(month[0])
            m_stop.append(month[1])
        elif day[0] >= month[1]:
            break

failed_dict = {'start': np.array(m_start), 'stop': np.array(m_stop)}
failed_data = pd.DataFrame(failed_dict)
failed_data.drop_duplicates(inplace=True)
print(f'failed months are: {len(failed_data)}')

failed_data.to_csv(outfile, sep=' ', header=True, index=False)

infile = path + 'YEARS5g019_collectLC.log'
runs = open(infile, 'r').readlines()
idx_start = runs.index('FOLDED_TEST_50BIN\n')
idx_stop = runs.index('# merged collected LC in file /data01/projects/IGRJ17354-3255/FERMI/LC/YEARS5g019/igrj17354-3255_lightcurve_fullLC.txt')-1
runs_months = runs[idx_start+1:idx_stop]

m_start, m_stop = list(), list()
for el in runs_months:
    m_start.append(el[5:14])
    m_stop.append(el[15:-1])
failed_dict = {}

print(f'failed runs are: {len(m_start)}')
failed_dict = {'start': np.array(m_start), 'stop': np.array(m_stop)}
failed_runs = pd.DataFrame(failed_dict)
failed_runs.drop_duplicates(inplace=True)
#failed_runs.to_csv(outfile, sep=' ', header=True, index=False)

# ------------------------------------------------------ months dir

print('------------- use M folders time intervals -------------')

infile = path + 'igrMonthsIndex.out'
outfile = path + 'igrMonthsIndex_failed.out'

months = pd.read_csv(infile, sep=' ')

failed = data[cts < 100]
m_start, m_stop, m_name = list(), list(), list()
for j, month in months.iterrows():
    for i, day in failed.iterrows():
        if month[2] <= day[0] <= month[3]:
            m_start.append(month[2])
            m_stop.append(month[3])
            m_name.append(month[1])
        elif day[0] >= month[3]:
            break

failed_dict = {'start': np.array(m_start), 'stop': np.array(m_stop), 'name': m_name}
failed_data = pd.DataFrame(failed_dict)
failed_data.drop_duplicates(inplace=True)
print(f'failed months are: {len(failed_data)}')

failed_data.to_csv(outfile, sep=' ', header=True, index=False)

infile = path + 'YEARS5g019_collectLC.log'
outfile = path + 'igrMonths_YEARS5g019_failed.out'
runs = open(infile, 'r').readlines()
idx_start = runs.index('FOLDED_TEST_50BIN\n')
idx_stop = runs.index('# merged collected LC in file /data01/projects/IGRJ17354-3255/FERMI/LC/YEARS5g019/igrj17354-3255_lightcurve_fullLC.txt')-1
runs_months = runs[idx_start+1:idx_stop]

m_start, m_stop, m_name = list(), list(), list()
for el in runs_months:
    m_start.append(el[5:14])
    m_stop.append(el[15:-1])
    m_name.append(el.replace('\n',''))
failed_dict = {}

print(f'failed runs are: {len(m_start)}')
failed_dict = {'start': np.array(m_start), 'stop': np.array(m_stop), 'name': m_name}
failed_runs = pd.DataFrame(failed_dict)
failed_runs.drop_duplicates(inplace=True)

"""for i, name in enumerate(failed_runs['name']):
    if name not in failed_data['name']:
        print(f'{i+1} check {name}')"""
