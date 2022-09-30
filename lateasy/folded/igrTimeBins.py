import yaml
import pandas as pd

cfgfile = '/data01/projects/IGRJ17354-3255/FERMI/LC/YEARS5test/TEST_MONTH.yaml'
with open(cfgfile) as f:
    cfg = yaml.safe_load(f)
tmin = cfg['selection']['tmin']
tmax = cfg['selection']['tmax']

daysfile = '/data01/projects/IGRJ17354-3255/FERMI/LC/igrDaysMET_filtered.out'
days = pd.read_csv(daysfile, sep=' ')

bins = days[days['start_met'] >= tmin]
bins = bins[bins['stop_met'] <= tmax]
last = [t for t in bins['stop_met']][-1]
print(last)
time_bins = list(t for t in bins['start_met'])
time_bins.append(last)
print(len(bins), len(time_bins))


