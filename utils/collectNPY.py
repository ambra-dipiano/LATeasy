
import os
import sys
from os.path import abspath
import argparse
import numpy as np
import pandas as pd
from os.path import join, isdir, isfile
from utils.functions import met_to_mjd

parser = argparse.ArgumentParser(description='Collect data from multiple NPY outputs')
parser.add_argument('-f', '--folder', type=str, required=True, help='of the NPY file with path')
parser.add_argument('-t', '--type', type=str, default='LC', help='collect by type: ROI, LC, SED, LOC')
parser.add_argument('--source', type=str, default='IGRJ17354-3255', help='source name')
parser.add_argument('--ts', type=float, default=9, help='minimum ts threshold')
args = parser.parse_args()

def get_sens(file, relpath):
    if os.path.exists(join('.', relpath, file)):
        f = open(join('.', relpath, file), 'r')
        sens = f.read().strip()
    else:
        sens = np.nan
    return sens

def get_phase(tmin, tmax):
    t0 = 54260.974
    p = 8.4474
    timebinsize = tmax - tmin
    ta = tmin + timebinsize / 2
    ph1 = (ta-t0) / p
    ph = ph1 - int(ph1)
    return ph

# lightcurves
def collect_lc(filename, outputfile, roiname, keys, source, relpath):
    if os.path.isfile(outputfile):
        os.remove(outputfile)
    lc = np.load(filename, allow_pickle=True, encoding='latin1', fix_imports=True).flat[0]
    roi = np.load(roiname, allow_pickle=True, encoding='latin1', fix_imports=True).flat[0]
    rows = len(lc['tmin'])
    cols_lc = lc.keys()
    cols_roi = lc.keys()
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
                hdr += ' ' + str(key)
                if 'Prefactor_value' in key:
                    line += ' ' + str(roi['sources']['gll_iem_v07']['param_values'][0])
                if 'Prefactor_error' in key:
                    line += ' ' + str(roi['sources']['gll_iem_v07']['param_errors'][0])
                if 'Index_value' in key:
                    line += ' ' + str(roi['sources']['gll_iem_v07']['param_values'][1])
                if 'Index_error' in key:
                    line += ' ' + str(roi['sources']['gll_iem_v07']['param_errors'][1])
                if 'Normalization_value' in key:
                    line += ' ' + str(roi['sources']['iso_P8R3_SOURCE_V2_v1']['param_values'][0])
                if 'Normalization_error' in key:
                    line += ' ' + str(roi['sources']['iso_P8R3_SOURCE_V2_v1']['param_errors'][0])
            # source params from lc and from roi
            elif 'source' in key:
                hdr += ' ' + str(key)
                # from lc
                if 'Prefactor_value' in key:
                    line += ' ' + str(lc['param_values'][i][0]) 
                elif 'Prefacotr_error' in key:
                    line += ' ' + str(lc['param_errors'][i][0]) 
                elif 'Index_value' in key:
                    line += ' ' + str(lc['param_values'][i][1]) 
                elif 'Index_error' in key:
                    line += ' ' + str(lc['param_errors'][i][1]) 
                # from roi
                elif 'RA_value' in key:
                    line += ' ' + str(roi['sources'][source]['ra'])
                elif 'RA_error' in key:
                    line += ' ' + str(roi['sources'][source]['ra_err'])
                elif 'DEC_value' in key:
                    line += ' ' + str(roi['sources'][source]['dec'])
                elif 'DEC_error' in key:
                    line += ' ' + str(roi['sources'][source]['dec_err'])
            elif 'sens' in key:
                hdr += ' ' + str(key)
                line += ' ' + str(get_sens(str(key)+'.txt', relpath))
            elif key == 'phase':
                hdr += ' ' + str(key)
                line += ' ' + str(get_phase(lc['tmin'][i], lc['tmax'][i]))
        # add filename
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

# localisations
def collect_loc(filename, columns=('ra', 'ra_err', 'dec', 'dec_err', 'ra_preloc', 'dec_preloc', 'pos_offset', 'pos_r95'), outputfile=None):

    if outputfile is None:
        outputfile = filename.replace('.npy', '_collected.txt')
    if os.path.isfile(outputfile):
        os.remove(outputfile)
    print('Data will be saved in ', outputfile)

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
    line += str(filename)
    with open(outputfile, 'a') as f:
        f.write(line + '\n')
        f.close()

# sed
def collect_sed(filename, columns=('e_min', 'e_max', 'ts', 'flux', 'flux_err', 'flux_ul95', 'Prefactor', 'Index', 'Scale'), par_names = ('Prefactor', 'Index', 'Scale'), outputfile=None):

    if outputfile is None:
        outputfile = filename.replace('.npy', '_collected.txt')
    if os.path.isfile(outputfile):
        os.remove(outputfile)
    print('Data will be saved in ', outputfile)

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
        line += str(filename)
        with open(outputfile, 'a') as f:
            f.write(line + '\n')
            f.close()

# roi
def collect_roi(filename, src='IGRJ17354-3255', columns=('ts', 'flux', 'flux_err', 'flux_ul95', 'Prefactor', 'Index', 'Scale'), par_names = ('Prefactor', 'Index', 'Scale'), outputfile=None):

    if outputfile is None:
        outputfile = filename.replace('.npy', '_collected.txt')
    if os.path.isfile(outputfile):
        os.remove(outputfile)
    print('Data will be saved in ', outputfile)

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
    line += str(filename)
    with open(outputfile, 'a') as f:
        f.write(line + '\n')
        f.close()

# merge output 
def merge_data(bins, filename, mergefile, folder):
    if len(bins) == 0:
        raise IndexError(f'The analysis did not produce any output of the kind: {filename}')
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

if __name__ == "__main__":

    folder = args.folder
    source = args.source
    print('collect from ', args.type.upper())
    # check folder existance
    if not os.path.isdir(folder):
        raise ValueError('directory', folder, 'not found')
    # all keys
    keys = ('tmin', 'tmax', 'tmin_mjd', 'tmax_mjd', 'phase', 'e_min', 'e_max', 'ts', 'npred', 'flux', 'flux_err', 'flux_ul95', 'flux100_ul95', 'eflux', 'eflux_err', 'eflux100', 'eflux100_err', 'eflux_ul95', 'sens3', 'sens35', 'sens4', 'sens5', 'gal_Prefactor_value', 'gal_Prefactor_error','gal_Index_value', 'gal_Index_error', 'iso_Normalization_value', 'iso_Normalization_error', 'source_Prefactor_value', 'source_Prefactor_error', 'source_Index_value', 'source_Index_error', 'source_RA_value', 'source_RA_error', 'source_DEC_value', 'source_DEC_error', 'filename')
    # list of subdir in abspath
    bins = []
    for d in os.listdir(folder):
        if isdir(join(folder, d)):
            bins.append(d)
    bins = sorted(bins)
    # sort files
    if args.type.upper() not in ('LC', 'SED', 'ROI', 'LOC'):
        raise ValueError('Invalid "type" parameter. Please chose between: roi, sed, lc. Default is ROI.')
    # check type
    roiname = 'roi2_fit_model.npy'
    output = str(args.source.upper()) + '_' + str(args.type.lower()) + '.txt'
    if args.type.upper() == 'ROI':
        filename = roiname
        #raise ValueError('Option not implemented yet.')
    elif args.type.upper() == 'SED':
        filename = 'sed.npy'
        #raise ValueError('Option not implemented yet.')
    elif args.type.upper() == 'LC':
        filename = f'{args.source.lower()}_lightcurve.npy'
    elif args.type.upper() == 'LOC':
        filename = f'{args.source.lower()}_loc.npy'
    # collect single LC bins data
    binfiles = []
    for b in bins:
        binfilename = join('.', folder, b, filename)
        outputfile = join('.', folder, b, output)
        roi = join('.', folder, b, roiname)
        if isfile(binfilename):
            binfiles.append(b)
            if args.type.upper() == 'LC':
                collect_lc(binfilename, outputfile, roi, keys, source, relpath=join(folder, b))
            elif args.type.upper() == 'SED':
                collect_sed(binfilename, outputfile=outputfile)
            elif args.type.upper() == 'LOC':
                collect_loc(binfilename, outputfile=outputfile)
            elif args.type.upper() == 'ROI':
                collect_roi(binfilename, outputfile=outputfile)
        else:
            print(binfilename, 'not found.')

    print(len(binfiles), len(bins))
    # merge single LC bins data
    mergefile = folder + '_' + str(args.type.upper()) + '.txt'
    merge_data(binfiles, output, mergefile, folder)
    print('merge output ', mergefile)

    # keep only ts >= 9
    ts = args.ts
    outfile = mergefile.replace('.txt', '_ts%s.txt' %str(ts))
    data = pd.read_csv(mergefile, sep=' ')
    data9 = data[data['ts'] >= float(ts)]
    print('detections above ts=', ts, ':', len(data9))
    data9.to_csv(outfile, sep=' ', header=True, index=False)
    print('output above ts threshold ', outfile)
