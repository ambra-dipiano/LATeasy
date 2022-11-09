import yaml
import argparse
import pandas as pd
from os.path import join, basename
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

bins = days[days['start_met'] >= tmin]
bins = bins[bins['stop_met'] <= tmax]
last = [t for t in bins['stop_met']][-1]
log.debug('Last time bin: ' + str(last))
time_bins = list(t for t in bins['start_met'])
time_bins.append(last)
log.debug('Number of bins: ' + str(len(bins)))
log.debug('Number of time bins: ' + str(len(time_bins)))


