import os
import pandas as pd
import numpy as np

dayspath = '/data01/projects/IGRJ17354-3255/FERMI/LC/'
daysfile = os.path.join(dayspath, 'igrDaysMET_removed.out')

days = pd.read_csv(daysfile, sep=' ')

foldedpath = dayspath.replace('LC', 'folded8/periods')
files = ['period%d.txt' %(i+1) for i in range(8)]

for f in files:
    infile = os.path.join(foldedpath, f)
    bins = pd.read_csv(infile, sep=' ', names=['tstart', 'tstop'])

    # ------------------------------------ bad days

    print((days['stop_met']-days['start_met'])[0])
    print((bins['tstop']-bins['tstart'])[0])

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

    print(len(days), len(bins), len(tstart))

    data_dict = {'tstart': tstart, 'tstop': tstop} 
    data = pd.DataFrame(data_dict)
    data.drop_duplicates(inplace=True)

    outfile = os.path.join(foldedpath, f.replace('.txt', '_removed.txt'))
    data.to_csv(outfile, sep=' ', header=True, index=False)
    print('rows in dropped data:', len(data))

    keep = pd.concat([bins, data]).drop_duplicates(keep=False)
    outfile = os.path.join(foldedpath, f.replace('.txt', '_kept.txt'))
    keep.to_csv(outfile, sep=' ', header=True, index=False)
    print('rows in keep data:', len(keep))
    print('\n\n------------\n\n')
