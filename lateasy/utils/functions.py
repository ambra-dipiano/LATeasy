# *****************************************************************************
# Copyright (C) 2022 INAF
# This software is distributed under the terms of the BSD-3-Clause license
#
# This software contains an ensable of utility functions
# *****************************************************************************

import os
import logging
import numpy as np
import pandas as pd
from datetime import datetime
from astropy.time import Time
import xml.etree.ElementTree as ET
from os.path import join, exists, isfile, dirname, isdir

def mjd_to_met(time):
    """Convert mean julian date to mission elapse time."""
    correction = 0.0006962818548948615
    return (86400. + correction) * (time - 51910) 

def met_to_mjd(time):
    """Convert mean julian date to mission elapse time."""
    correction = 0.0006962818548948615
    return time / (86400. + correction) + 51910

def mjd_to_tt(time_mjd):
    """Convert MJD to AGILE TT time."""
    t = Time(time_mjd, format="mjd")
    return np.round(t.unix - 1072915200)

def met_to_tt(time):
    """Convert Fermi MET to AGILE TT time."""
    return mjd_to_tt(met_to_mjd(time))

def get_target_coords(model, name):
    mysource = ET.parse(model).getroot().find('source[@name="' + name + '"]')
    ra = float(mysource.find('spatialModel/parameter[@name="RA"]').attrib['value'])
    dec = float(mysource.find('spatialModel/parameter[@name="DEC"]').attrib['value'])
    return ra, dec

def set_logger(filename, level):
    if not isdir(dirname(filename)):
        os.makedirs(dirname(filename))
    log = logging.getLogger()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fileHandler = logging.FileHandler(filename)
    fileHandler.setFormatter(formatter)
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(formatter)
    log.addHandler(fileHandler)
    log.addHandler(consoleHandler)
    log.setLevel(level)
    return log

def load_data(filename):
    try:
        data = pd.read_csv(filename, sep=" ", header=0)
    except:
        raise ValueError(filename, 'is empty')
    return data

# get sensitivity
def get_sens(file, relpath):
    if exists(join('.', relpath, file)):
        f = open(join('.', relpath, file), 'r')
        sens = f.read().strip()
    else:
        sens = np.nan
    return sens

# get phase
def get_phase(tmin, tmax):
    t0 = 54260.974
    p = 8.4474
    timebinsize = tmax - tmin
    ta = tmin + timebinsize / 2
    ph1 = (ta-t0) / p
    ph = ph1 - int(ph1)
    return ph

# get lightcurves
def collect_lc(filename, outputfile, roiname, keys, source, relpath, isomodel, galmodel):
    if isfile(outputfile):
        os.remove(outputfile)
    lc = np.load(filename, allow_pickle=True, encoding='latin1', fix_imports=True).flat[0]
    roi = np.load(roiname, allow_pickle=True, encoding='latin1', fix_imports=True).flat[0]
    rows = len(lc['tmin'])
    cols_lc = lc.keys()
    cols_roi = roi.keys()
    # header of output file
    hdr = str()
    for i in range(rows):
        line = str()
        for j, key in enumerate(keys):
            # from lc
            if key in cols_lc:
                if j == 0:
                    hdr += str(key)
                    line += str(lc[key][i]) 
                else:
                    hdr += ' ' + str(key)
                    line += ' ' + str(lc[key][i])
            # bkg from roi
            elif 'iso' in key or 'gal' in key:
                if 'Prefactor_value' in key:
                    hdr += ' ' + str(key)
                    line += ' ' + str(roi['sources'][galmodel]['param_values'][0])
                if 'Prefactor_error' in key:
                    hdr += ' ' + str(key)
                    line += ' ' + str(roi['sources'][galmodel]['param_errors'][0])
                if 'Index_value' in key:
                    hdr += ' ' + str(key)
                    line += ' ' + str(roi['sources'][galmodel]['param_values'][1])
                if 'Index_error' in key:
                    hdr += ' ' + str(key)
                    line += ' ' + str(roi['sources'][galmodel]['param_errors'][1])
                if 'Normalization_value' in key:
                    try:
                        hdr += ' ' + str(key)
                        line += ' ' + str(roi['sources'][isomodel]['param_values'][0])
                    except KeyError as e:
                        hdr += ' ' + str(key)
                        line += ' ' + str(roi['sources']['isodiff']['param_values'][0])
                        print(f'Isotropic model {isomodel} not found, trying isodiff')
                if 'Normalization_error' in key:
                    try:
                        hdr += ' ' + str(key)
                        line += ' ' + str(roi['sources'][isomodel]['param_errors'][0])
                    except KeyError as e:
                        hdr += ' ' + str(key)
                        line += ' ' + str(roi['sources']['isodiff']['param_errors'][0]) 
                        print(f'Isotropic model {isomodel} not found, trying isodiff')

            # source params from lc and from roi
            elif 'source' in key:
                # from lc
                if 'Prefactor_value' in key:
                    hdr += ' ' + str(key)
                    line += ' ' + str(lc['param_values'][i][0]) 
                elif 'Prefactor_error' in key:
                    hdr += ' ' + str(key)
                    line += ' ' + str(lc['param_errors'][i][0]) 
                elif 'Index_value' in key:
                    hdr += ' ' + str(key)
                    line += ' ' + str(lc['param_values'][i][1]) 
                elif 'Index_error' in key:
                    hdr += ' ' + str(key)
                    line += ' ' + str(lc['param_errors'][i][1]) 
                # from roi
                elif 'RA_value' in key:
                    hdr += ' ' + str(key)
                    line += ' ' + str(roi['sources'][source]['ra'])
                elif 'RA_error' in key:
                    hdr += ' ' + str(key)
                    line += ' ' + str(roi['sources'][source]['ra_err'])
                elif 'DEC_value' in key:
                    hdr += ' ' + str(key)
                    line += ' ' + str(roi['sources'][source]['dec'])
                elif 'DEC_error' in key:
                    hdr += ' ' + str(key)
                    line += ' ' + str(roi['sources'][source]['dec_err'])
            elif 'sens' in key:
                hdr += ' ' + str(key)
                line += ' ' + str(get_sens(str(key)+'.txt', relpath))
            elif key == 'phase':
                hdr += ' ' + str(key)
                line += ' ' + str(get_phase(lc['tmin'][i], lc['tmax'][i]))
        # add filename
        hdr += ' ' + 'lc_file'
        line += ' ' + str(filename)
        # write header
        if i == 0:
            with open(outputfile, 'w+') as f:
                f.write(hdr + '\n')
                f.close()
        # write lines
        with open(outputfile, 'a') as f:
            f.write(line + '\n')
            f.close()

# get localisations
def collect_loc(filename, columns=('ra', 'ra_err', 'dec', 'dec_err', 'ra_preloc', 'dec_preloc', 'pos_offset', 'pos_r95'), outputfile=None):

    if outputfile is None:
        outputfile = filename.replace('.npy', '_collected.txt')
    if isfile(outputfile):
        os.remove(outputfile)

    data = np.load(filename, allow_pickle=True, encoding='latin1', fix_imports=True).flat[0]
    if columns == 'all':
        raise ValueError('columns="all" is not implemented yet. Please set the parameter to a list of keys.')
    # header of output file
    hdr = str()
    hdr += 'month '
    for key in columns:
        hdr += str(key) + ' '
    with open(outputfile, 'w+') as f:
        f.write(hdr + '\n')
        f.close()
    line = str()
    for key in columns:
        line += str(data[key]) + ' '
    # add filename
    hdr += ' ' + 'loc_file'
    line += str(filename)
    with open(outputfile, 'a') as f:
        f.write(line + '\n')
        f.close()

# get sed
def collect_sed(filename, columns=('e_min', 'e_max', 'ts', 'flux', 'flux_err', 'flux_ul95', 'Prefactor', 'Index', 'Scale'), par_names = ('Prefactor', 'Index', 'Scale'), outputfile=None):

    if outputfile is None:
        outputfile = filename.replace('.npy', '_collected.txt')
    if isfile(outputfile):
        os.remove(outputfile)

    data = np.load(filename, allow_pickle=True, encoding='latin1', fix_imports=True).flat[0]
    pars = ('param_values', 'param_errors')
    suffix = ('', '_err')
    hdr = str()
    for key in columns:
        if key in par_names:
            for i, p in enumerate(pars):
                hdr += str(key) + str(p.replace('param', '')) + ' '
        else:
            hdr += str(key) + ' '
    with open(outputfile, 'w+') as f:
        f.write(hdr + '\n')
        f.close()
    for n in range(len(data[columns[0]])):
        line = str()
        for key in columns:
            if key in par_names:
                for p in pars:
                    index = par_names.index(key)
                    line += str(data[p][index]) + ' '
            else:
                line += str(data[key][n]) + ' '
        # add filename
        hdr += ' ' + 'sed_file'
        line += str(filename)
        with open(outputfile, 'a') as f:
            f.write(line + '\n')
            f.close()

# get roi
def collect_roi(filename, src='IGRJ17354-3255', columns=('ts', 'flux', 'flux_err', 'flux_ul95', 'Prefactor', 'Index', 'Scale'), par_names = ('Prefactor', 'Index', 'Scale'), outputfile=None):

    if outputfile is None:
        outputfile = filename.replace('.npy', '_collected.txt')
    if isfile(outputfile):
        os.remove(outputfile)

    data = np.load(filename, allow_pickle=True, encoding='latin1', fix_imports=True).flat[0]
    pars = ('param_values', 'param_errors')
    suffix = ('', '_err')
    hdr = str()
    for key in columns:
        if key in par_names:
            for p in pars:
                hdr += str(key) + str(p.replace('param', '')) + ' '
        else:
            hdr += str(key) + ' '
    with open(outputfile, 'w+') as f:
        f.write(hdr + '\n')
        f.close()
    line = str()
    for key in columns:
        if key in par_names:
            for p in pars:
                index = par_names.index(key)
                line += str(data['sources'][src][p][index]) + ' '
        else:
            line += str(data['sources'][src][key]) + ' '
    # add filename
    hdr += ' ' + 'roi_file'
    line += str(filename)
    with open(outputfile, 'a') as f:
        f.write(line + '\n')
        f.close()

# merge output 
def merge_data(bins, filename, mergefile, folder):
    if len(bins) == 0:
        raise Exception(f'The post-processing did not produce any output of the kind: {filename}\nIf you did not submit your analyses to Slurm jobs you may be required to manually open your results. If you did submit to Slurm check your logs for futher information.')
    mf = open(join('.', mergefile), 'w+') 
    for i, b in enumerate(bins):
        with open(join('.', folder, b, filename)) as f:
            if i == 0:
                lines = f.readlines()
            else:
                lines = f.readlines()[1:]
            for line in lines:
                mf.write(line)
    mf.close()

