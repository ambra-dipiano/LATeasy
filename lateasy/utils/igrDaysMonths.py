import pandas as pd
import numpy as np

def mjd_to_met(time):
    """Convert mean julian date to mission elapse time."""
    correction = 0.0006962818548948615
    return (86400. + correction)* (time - 51910) 


path = '/data01/projects/IGRJ17354-3255/FERMI/LC/'

infile = path + 'igrDaysMJD.out'
outfile = path + 'igrDaysMET.out'

time = 51910
ssdc = 0.
print(f'check conversion: {time} MJD = {np.around(mjd_to_met(time))} MET = {ssdc} SSDC') 
print(f'diff: {np.around(mjd_to_met(time))-ssdc}')
time = 54683
ssdc = 239587201.
print(f'check conversion: {time} MJD = {np.around(mjd_to_met(time))} MET = {ssdc} SSDC') 
print(f'diff: {np.around(mjd_to_met(time))-ssdc}')
time = 56426
ssdc = 390182403.
print(f'check conversion: {time} MJD = {np.around(mjd_to_met(time))} MET = {ssdc} SSDC') 
print(f'diff: {np.around(mjd_to_met(time))-ssdc}')
time = 57000
ssdc = 439776003.
print(f'check conversion: {time} MJD = {np.around(mjd_to_met(time))} MET = {ssdc} SSDC') 
print(f'diff: {np.around(mjd_to_met(time))-ssdc}')
time = 58700
ssdc = 586656005.
print(f'check conversion: {time} MJD = {np.around(mjd_to_met(time))} MET = {ssdc} SSDC') 
print(f'diff: {np.around(mjd_to_met(time))-ssdc}')
time = 59091
ssdc = 620438405.
print(f'check conversion: {time} MJD = {np.around(mjd_to_met(time))} MET = {ssdc} SSDC') 
print(f'diff: {np.around(mjd_to_met(time))-ssdc}')

diff_met = 5
diff_mjd = diff_met / (59091 - 51910)
print(diff_mjd)

lc=pd.read_csv(infile, names=['time', 'f1', 'f2', 'f3', 'f4', 'exp', 'cts'], sep=' ')

start_day_mjd = np.array(lc['time'] - 0.5) #- 43200
stop_day_mjd = np.array(lc['time'] + 0.5) #+ 43200

start_day_met = np.around(mjd_to_met(start_day_mjd))#.astype('int')
stop_day_met = np.around(mjd_to_met(stop_day_mjd))#.astype('int')
exp = np.array(lc['exp'])
cts = np.array(lc['cts'])

data_dict = {'start_met': start_day_met, 'stop_met': stop_day_met, 'exposure': exp, 'counts': cts} # {'f1': lc['f1'], 'f2': lc['f2'], 'f3': lc['f3'], 'f4': lc['f4']}
data = pd.DataFrame(data_dict)
data.to_csv(outfile, sep=' ', header=True, index=False)
print(f'rows in data: {len(data)}')

filtered = data[cts > 100]
print(f'rows in filtered: {len(filtered)}')
print(f'delated {len(data)-len(filtered)} rows')
print(f'min exposure in filtered: {filtered["exposure"].min()}')

outfile = path + 'igrDaysMET_filtered.out'
filtered.to_csv(outfile, sep=' ', header=True, index=False)

bad_days = data[cts < 100]
print(f'bad days: {len(bad_days)}')

outfile = path + 'igrDaysMET_removed.out'
bad_days.to_csv(outfile, sep=' ', header=True, index=False)

# --------------------------------------------------- folded periods

print('------------- use folded time intervals -------------')

infile = path + 'igrMonthsMET.out'
outfile = path + 'igrMonthsMET_failed.out'

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
