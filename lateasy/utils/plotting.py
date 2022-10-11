# *****************************************************************************
# Copyright (C) 2022 INAF
# This software is distributed under the terms of the BSD-3-Clause license
#
# This software is intended to plot the fermipy collected lightcurve data
# *****************************************************************************

import yaml
import numpy as np
import matplotlib
import pandas as pd
from os.path import join, basename
from lateasy.utils.functions import set_logger

class Plotting():
    def __init__(self, pipeconf):
        # load yaml configurations
        with open(pipeconf) as f:
            self.pipeconf = yaml.safe_load(f)

        # logging
        logname = join(self.pipeconf['path']['output'], basename(__file__).replace('.py','.log'))
        self.log = set_logger(filename=logname, level=self.pipeconf['execute']['loglevel'])
        self.log.info('Logging: ' + logname)

        # switch matplotlib backend and complete imports
        if self.pipeconf['execute']['agg_backend']:
            matplotlib.use('agg')
        import matplotlib.pyplot as plt
        plt.switch_backend('agg')
        self.log.info('Switch to AGG backend')

    def load_data(self, filename):
        data = pd.read_csv(filename, sep=" ", header=0)
        return data

    def plot_lc(self, data, filename, fontsize=20):
        # get data
        ts = np.array(data['ts'])
        t = (((np.array(data['tmin_mjd']) + np.array(data['tmax_mjd'])) / 2)) 
        terr = ((np.array(data['tmax_mjd']) - np.array(data['tmin_mjd'])) / 2) 
        f = np.array(data['flux'])
        ferr = np.array(data['flux_err'])

        # get upper limits
        upl = []
        for idx, (v, e, tv) in enumerate(zip(f, ferr, ts)):
            if e > 2*v or tv < self.pipeconf['postprocessing']['mints']:
                upl.append(True)
                ferr[idx] = v/2
            else:
                upl.append(False)
        
        # get detections
        detection = [f[i] for i in range(len(f)) if not upl[i]]
        detection_err = [ferr[i] for i in range(len(ferr)) if not upl[i]]
        detection_time = [t[i] for i in range(len(t)) if not upl[i]]
        detection_ts = [ts[i] for i in range(len(ts)) if not upl[i]]
        self.log.debug('Number of detection above TS=' + str(self.pipeconf['postprocessing']['mints']) + ' : ' + str(len(detection)))

        # plot
        fig, (ax1, ax2) = matplotlib.pyplot.subplots(2, 1, sharex=True, figsize=(10,8))
        ax1.set_title(self.pipeconf['target']['name'] + ' lightcurve', fontsize=fontsize)
        ax1.errorbar(t, f, xerr=terr, yerr=ferr, ls=' ', marker='o', markeredgecolor='k', uplims=upl, color='b', zorder=0)
        ax1.errorbar(detection_time, detection, xerr=0, yerr=detection_err, ls=' ', marker='o', markeredgecolor='k', color='r', zorder=10)
        ax1.set_ylabel('flux (ph/cm2/s)', fontsize=fontsize)
        ax1.set_yscale('log')
        ax2.errorbar(t, ts, xerr=terr, ls=' ', marker='o', markeredgecolor='k', color='b')
        ax2.errorbar(detection_time, detection_ts, xerr=0, ls=' ', marker='o', markeredgecolor='k', color='r')
        ax2.axhline(self.pipeconf['postprocessing']['mints'], ls='-.', color='r')
        ax2.set_xlabel('time (MJD)', fontsize=fontsize)
        ax2.set_ylabel('TS', fontsize=fontsize)
        matplotlib.pyplot.tight_layout()
        fig.savefig(filename)
        matplotlib.pyplot.close()
        self.log.info('plotting' + filename)
        return self


