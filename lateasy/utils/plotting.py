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
from lateasy.utils.functions import set_logger, met_to_mjd
from astropy.io import fits

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

    def plot_lc(self, data, filename='lightcurve.png', fontsize=20):
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

    def compare_lc_full_range(self, data_lc, data_fermi, filename='lightcurve_comparison.png', fontsize=15):

        # get data_lc
        ts = np.array(data_lc['ts'])
        t = (np.array(data_lc['tmin_mjd']) + np.array(data_lc['tmax_mjd'])) / 2
        terr = (np.array(data_lc['tmax_mjd']) - np.array(data_lc['tmin_mjd'])) / 2
        f = np.array(data_lc['flux'])
        ferr = np.array(data_lc['flux_err'])

        # get upper limits in data_lc
        upl = []
        for idx, (v, e, tv) in enumerate(zip(f, ferr, ts)):
            if e > 2*v or tv < self.pipeconf['postprocessing']['mints']:
                upl.append(True)
                ferr[idx] = v/2
            else:
                upl.append(False)
        
        # get detections in data_lc
        detection = [f[i] for i in range(len(f)) if not upl[i]]
        detection_err = [ferr[i] for i in range(len(ferr)) if not upl[i]]
        detection_time = [t[i] for i in range(len(t)) if not upl[i]]
        detection_ts = [ts[i] for i in range(len(ts)) if not upl[i]]
        self.log.debug('Number of detection above TS=' + str(self.pipeconf['postprocessing']['mints']) + ' : ' + str(len(detection)))

        # filter fermi data
        self.log.debug('Min LAT time: ' + str(min(met_to_mjd(data_fermi['START']))))
        self.log.debug('Min DATA time: ' + str(min(t)))
        self.log.info('Filter LAT data for time > ' + str(min(t)))
        self.log.debug('Max LAT time: ' + str(max(met_to_mjd(data_fermi['STOP']))))
        self.log.debug('Max DATA time: ' + str(max(t)))
        self.log.info('Filter LAT data for time < ' + str(max(t)))
        data_fermi['START'] = met_to_mjd(data_fermi['START'])
        data_fermi['STOP'] = met_to_mjd(data_fermi['STOP'])
        data_fermi = data_fermi[((data_fermi['START']) >= np.min(t)) & (data_fermi['STOP'] <= np.max(t))]
        self.log.info('Length of intersection:' + str(len(data_fermi)))

        # get data_fermi
        fermi_time = (np.array(data_fermi['START']) + np.array(data_fermi['STOP'])) / 2
        fermi_time_err = np.array(data_fermi['STOP'] - np.array(data_fermi['START'])) / 2
        fermi_flux = np.array(data_fermi['FLUX_100_300000'])
        fermi_flux_err = np.array(data_fermi['ERROR_100_300000'])
        fermi_upl = np.array(data_fermi['UL_100_300000'])
        fermi_ts = np.array(data_fermi['TEST_STATISTIC'])

        # plot flux
        fig, (ax1, ax2) = matplotlib.pyplot.subplots(2, 1, sharex=True, figsize=(10,8))
        ax1.set_title(self.pipeconf['target']['name'] + ' lightcurve', fontsize=fontsize)
        ax1.errorbar(t, f, xerr=terr, yerr=ferr, ls=' ', marker='o', markeredgecolor='k', uplims=upl, color='b', zorder=0, label='Fermi/LAT local analysis')
        ax1.errorbar(fermi_time, fermi_flux, xerr=fermi_time_err, yerr=fermi_flux_err, ls=' ', marker='P', markeredgecolor='k', uplims=fermi_upl, color='g', zorder=5, label='Fermi/LAT data repository')
        ax1.set_ylabel('flux (ph/cm2/s)', fontsize=fontsize)
        ax1.set_yscale('log')
        # plot ts
        ax2.errorbar(t, ts, xerr=terr, ls=' ', marker='o', markeredgecolor='k', color='b', label='Fermi/LAT local analysis')
        ax2.errorbar(fermi_time, fermi_ts, xerr=fermi_time_err, ls=' ', marker='P', markeredgecolor='k', color='g', label='Fermi/LAT data repository')
        ax2.axhline(self.pipeconf['postprocessing']['mints'], ls='-.', color='r')
        ax2.set_xlabel('time (MJD)', fontsize=fontsize)
        ax2.set_ylabel('TS', fontsize=fontsize)
        matplotlib.pyplot.legend(loc=0, fontsize=fontsize, bbox_to_anchor=(0.4, 0.9))
        matplotlib.pyplot.tight_layout()
        fig.savefig(filename)
        matplotlib.pyplot.close()
        self.log.info('plotting' + filename)
        return self

    def load_data_lc_from_fits(self, filename):
        with fits.open(filename) as h:
            lc = h['LIGHTCURVES'].data
        return lc


