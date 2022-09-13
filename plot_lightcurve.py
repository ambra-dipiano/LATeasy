# *****************************************************************************
# Copyright (C) 2022 INAF
# This software is distributed under the terms of the BSD-3-Clause license
#
# This software is intended to plot the fermipy collected lightcurve data
# *****************************************************************************


import sys
import os
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

def load_data(filename):
    data = pd.read_csv(filename, sep=" ", header=0)
    return data

def plot_lc(data, filename):

    ts = np.array(data['ts'])
    t = (((np.array(data['tmin']) + np.array(data['tmax'])) / 2) - data['tmin'][0]) * 86400
    terr = ((np.array(data['tmax']) - np.array(data['tmin'])) / 2) * 86400
    f = np.array(data['flux'])
    ferr = np.array(data['flux_err'])
    fup = np.array(data['flux_ul95'])

    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
    ax1.errorbar(t, f, xerr=terr, yerr=ferr)
    ax2.plot(t, ts)
    fig.savefig(filename)
    print('plotting', filename)



filename_full = 'igrj17354-3255_lightcurve_fullLC.txt'
filename_bin = 'igrj17354-3255_lightcurve_collected.txt'
if len(sys.argv) > 1:
    folder = str(sys.argv[1])
else:
    folder = 'YEARS5'
if len(sys.argv) > 2:
    abspath = str(sys.argv[2]) + folder + '/'
else:
    abspath = '/data01/projects/IGRJ17354-3255/FERMI/LC/' + folder + '/'
# list of subdir in abspath
bins = []
for d in os.listdir(abspath):
    if os.path.isdir(abspath + '/' + d):
        bins.append(d)
bins = sorted(bins)
# plot monthly
plotname_bin = filename_bin.replace('.txt', '.png')
for b in bins:
    filepath = os.path.join(abspath, b, filename_bin)
    if os.path.exists(filepath):
        data = load_data(filepath)
        plot_lc(data, plotname_bin)
    else:
        print('bin', b, 'missing LC ==> skipped')

# plot year
plotname_full = filename_full.replace('.txt', '.png')
filepath = os.path.join(abspath, filename_full)
data = load_data(filepath)
plot_lc(data, plotname_full)
