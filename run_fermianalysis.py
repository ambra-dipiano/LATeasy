# *****************************************************************************
# Copyright (C) 2022 INAF
# This software is distributed under the terms of the BSD-3-Clause license
#
# This software is intended to run the fermi analysis 
# *****************************************************************************

import yaml
import argparse
import logging
import matplotlib
import pandas as pd
import matplotlib.pyplot as plt
from fermipy.gtanalysis import GTAnalysis
from os. path import isfile
from matplotlib import streamplot

# switch matplotlib backend
matplotlib.use('agg')
plt.switch_backend('agg')

# -------------------------------------------------------- functions
def list_nans():
    '''Filter out all nan TS sources.'''
    nan_sources = list()
    for src in gta.roi.get_sources():
        if str(src['ts']) == 'nan' and str(src.name) not in (target_source, 'isodiff', 'galdiff'):
            nan_sources.append(str(src.name))
    return nan_sources
    
def manageGalIsoParameters(galmodel, isomodel, keepgalmodelfree=True, keepisomodelfree=True, gal_prefactor_value=1, gal_index_value=0, iso_normalization_value=1):
    '''Update background parameters.'''

    # set the initial value of gal/Index and gal/Prefactor parameter
    gta.set_parameter(galmodel, par='Prefactor', value=gal_prefactor_value, scale=1)
    gta.set_parameter(galmodel, par='Index', value=gal_index_value, scale=1)
    if keepgalmodelfree == True:
        gta.free_source(galmodel, pars='norm', free=True)
    else:
        gta.free_source(galmodel, free=False)

    #set the initial value of iso/Normalization parameter
    gta.set_parameter(isomodel, par='Normalization', value=iso_normalization_value, scale=1)
    if keepisomodelfree == True:
        gta.free_source(isomodel, free=True)
    else:
        gta.free_source(isomodel, free=False)

# ---------------------------------------------------------------- input
parser = argparse.ArgumentParser(description='Fermi/LAT data analysis pipeline')
parser.add_argument('--pipeconf',  type=str, required=True, help='configuration file')
parser.add_argument('--fermiconf', type=str, required=True, help='configuration file')
args = parser.parse_args()

# load yaml configurations
with open(args.pipeconf) as f:
    pipeconf = yaml.load(f)
with open(args.fermiconf) as f:
    fermiconf = yaml.load(f)

# logging
logname = str(args.fermiconf).replace('.yml','.log')
log = logging.getLogger()
fileHandler = logging.FileHandler(logname)
log.addHandler(fileHandler)
consoleHandler = logging.StreamHandler()
log.addHandler(consoleHandler)

# ---------------------------------------------------------------- setup
target_source = pipeconf['target']['name']
log.info('\n#### LOGGING ---> ' + str(logname))

# free the following sources
variable_sources = pipeconf['variable_sources']
extended_sources = pipeconf['extended_sources']

# background parameters
galmodel = pipeconf['background']['galmodel']
isomodel = pipeconf['background']['isomodel']
if pipeconf['background']['galfree']:
    keepgalmodelfree = True
    gal_prefactor_value = 1
    gal_index_value = 0
else:
    gal_prefactor_value = pipeconf['background']['galnorm']
    gal_index_value = pipeconf['background']['galindex']
    keepgalmodelfree = False

if pipeconf['background']['isofree']:
    keepisomodelfree = True
    iso_normalization_value = 1 
else:
    iso_normalization_value = pipeconf['background']['isonorm']
    keepisomodelfree = False

log.info('\n\nSkip SED: ' + args.skipsed.capitalize() + '\nMake LC: ' + str(args.makelc))

# ----------------------------------------------------------------- analysis
gta = GTAnalysis(args.fermiconf, logging={'verbosity' : 3})
log.info('\n\n#### SETUP ---> gta.setup()')
gta.print_roi()
gta.setup()
# 1st optimaze 
opt1 = gta.optimize()
gta.print_roi()
fname = 'roi1_optimize'
gta.write_roi(fname)
log.info('\n\n# 1st optimize saved in ---> ' + str(fname))

# ----------------------------------------------------------------- preliminary fit
log.info('\n\n#### PRELIMINARY FIT')
#manage gal and iso parameters
manageGalIsoParameters(galmodel, isomodel, keepgalmodelfree=keepgalmodelfree, keepisomodelfree=keepisomodelfree, gal_prefactor_value=gal_prefactor_value, gal_index_value=gal_index_value, iso_normalization_value=iso_normalization_value)
log.info('\n# manage gal and iso parameters')
log.info('\n--- galmodel ---')
log.info('\nmodel = ' + str(galmodel) + '\nfree = ' + str(keepgalmodelfree))
log.info('\nprefactor = ' + str(gal_prefactor_value) + '\nindex = ' + str(gal_index_value))
log.info('\n--- isomodel ---')
log.info('\nmodel = ' + str(isomodel) + '\nfree = ' + str(keepisomodelfree))
log.info('\nnormalisation = ' + str(iso_normalization_value))
# get sources
gta.print_roi()
sources = gta.get_sources()
print('target & bkgs before fit1:')
for src in sources:
    if src['name'] in (galmodel, isomodel, target_source):
        print(src)

# execute fit
prefit = gta.fit(update=True)
sources = gta.get_sources()
fname = 'roi1_fit_model'
gta.write_roi(fname)
log.info('\n\n# 1st fit saved in ---> ' + str(fname))

# ------------------------------------------------------------- delete src ts < 1
log.info('\n\n# delete sources with TS < 1 or TS = nan')
#alternative 1 to eliminate sources. Removed minmax_npred=[-1,4]
nan_sources = list_nans()
if len(nan_sources) != 0:
    deleted_sources = gta.delete_sources(names=nan_sources, exclude=[target_source, isomodel, galmodel])
deleted_sources = gta.delete_sources(minmax_ts=[None,1], exclude=[target_source, isomodel, galmodel])

# check bkgs and target_source are kept
for d in deleted_sources:
    if d.name in (isomodel, galmodel, target_source):
        log.info('\n', str(d.name), ' was deleted ---> add back')
        gta.add_source(d.name, d)
        
# 2nd optimaze 
opt1 = gta.optimize()
fname = 'roi2_optimize'
gta.write_roi(fname)
log.info('\n\n# 2nd optimize saved in ---> ' + str(fname))

#manage gal and iso parameters
manageGalIsoParameters(galmodel, isomodel, keepgalmodelfree=keepgalmodelfree, keepisomodelfree=keepisomodelfree, gal_prefactor_value=gal_prefactor_value, gal_index_value=gal_index_value, iso_normalization_value=iso_normalization_value)

print('target & bkgs after optimize2:')
for src in sources:
    if src['name'] in (galmodel, isomodel, target_source):
        print(src)

# ----------------------------------------------------------------------- 1st sed
if args.skipsed.capitalize() == 'False':
    log.info('\n\n#### SED ---> gta.sed()')
    gta.sed(target_source, prefix='sed_cl95', free_background=True, free_radius=None, write_fits=False, write_npy=True, outfile='sed', make_plots=True)

# ------------------------------------------------------------------------ 2nd fit
fit_results = gta.fit(update=True)
print('Fit Quality: ',fit_results['fit_quality'])
print('Fit Status: ',fit_results['fit_status'])
fname = 'roi2_fit_model'
gta.write_roi(fname)
sources = gta.get_sources()
log.info('\n\n# 2nd fit saved in ---> ' + str(fname))
print("### Results of roi2_fit_model")
for src in gta.roi.get_sources():
    print(src.name + " " + str(src['ts']))
    log.info(src.name + " " + str(src['ts']))

print("target & bkgs after fit2:")
for src in sources:
    if src['name'] in (galmodel, isomodel, target_source):
        print(src)

# ------------------------------------------------------------------------ 1st localise
if args.skiploc.capitalize() == 'False':
    log.info('\n\n#### UPDATE TARGET POSITION')
    for src in gta.roi.get_sources():
        if src.name == target_source:
            if src['ts'] > 10:
                log.info('\ntarget TS > 10 ---> gta.localize()')
                loc = gta.localize(target_source, free_background=True, update=True, make_plots=True, write_fits=False, write_npy=True)
                log.info('\n--- check new position ---')
                if loc.pos_offset < loc.pos_r95:
                    log.info('\nwithin 0.95 confidence radius ---> keep new position')
                    src.spatial_pars['RA']['value'] = loc.ra
                    src.spatial_pars['DEC']['value'] = loc.dec
                    fname = 'fit_model_loc1'
                    gta.write_roi(fname)
                    log.info('\n # localisation saved in ---> ' + str(fname))
                    # ------------------------------------------------------- 2nd sed
                    if args.skipsed.capitalize() == 'False':
                        log.info('\n\n#### SED ---> gta.sed()')
                        gta.sed(target_source, prefix='sed2_cl95', free_background=True, free_radius=None, write_fits=False, write_npy=True, make_plots=True)
                else: 
                    log.info('\noutside 0.95 confidence radius ---> revert to previous position')
                    src.spatial_pars['RA']['value'] = loc.ra_preloc
                    src.spatial_pars['DEC']['value'] = loc.dec_preloc
            else:
                log.info('\ntarget TS < 10 ---> keep current position')

# --------------------------------------------------------------------- lightcurve
if args.makelc != 0:
    # change the hypothesis of the sources and put all sources with norm fixed
    log.info('\n\n######## LC')
    log.info('\n\n# freeze all sources')
    gta.free_sources(pars='norm', free=False)

    # Free normalisation of target_source and source within < 2 deg. Could be between 2 and 5
    gta.free_source(target_source, distance=2.0, pars='norm', free=True)
    log.info('\n\n# free "norm" for target and sources within 2 deg')

    # variable and extended sources
    for src in gta.roi.get_sources():
        # for variable srcs, put norm true if ts > 50
        if src.name in variable_sources['Source_Name']:
            # update significance
            variable_sources['Signif_Avg'][variable_sources['Source_Name'].index(src.name)] = float(src['ts'])
            log.info('\n --- variable source ---')
            if src['ts'] > 50:
                log.info('\nname = ' + src.name + ' TS > 50 ---> free "norm"')
                gta.free_source(src.name, pars='norm', free=True)
            else:
                log.info('\nname = ' + src.name + ' TS < 50 ---> keep frozen')
        # for extended srcs (<ROI), if the difference of the parameters with respect to the catalog value is too much, fix the parameter source at 4FGL value
        if src.name in extended_sources['Extended_Source_Name']:
            index = extended_sources['Extended_Source_Name'].index(src.name)
            norm4fgl = extended_sources['Normalisation'][index]
            norm_error4fgl =  extended_sources['Normalisation_Error'][index]
            norm = float(src.spectral_pars['Prefactor']['value'])
            norm_error = float(src.spectral_pars['Prefactor']['error'])
            log.info('\n --- extended source ---')
            if src['ts'] > 10:
                log.info('\nname = ' + src.name + ' TS > 10 ---> check "norm" errors')
                if norm > (norm4fgl + 2.0 * norm_error4fgl) or norm < (norm4fgl - 2.0 * norm_error4fgl):
                    log.info('\nerrors outside range ---> revert to 4FGL value')
                    src.spectral_pars['Prefactor']['value'] = norm4fgl
                    gta.free_source(src.name, pars='norm', free=False)
                else:
                    log.info('\nerrors within range ---> keep at current value')
            else:
                log.info('\nname = ' + src.name + ' TS < 10 ---> keep frozen')
        # get backgrounds values 
        if src.name == galmodel:
            log.info('\n--- update galmodel ---' )
            gal_prefactor_value = float(src.spectral_pars['Prefactor']['value'])
            gal_index_value = float(src.spectral_pars['Index']['value'])
            log.info('\nprefactor = ' + str(gal_prefactor_value) + '\nindex = ' + str(gal_index_value))
        if src.name ==  isomodel:
            log.info('\n--- update isomodel ---' )
            iso_normalization_value = float(src.spectral_pars['Normalization']['value'])
            log.info('\nnormalisation = ' + str(iso_normalization_value))

    # keep gal and iso model parameters fixed
    log.info('\n\n# freeze background parameters')
    keepgalmodelfree = False
    keepisomodelfree = False
    manageGalIsoParameters(galmodel, isomodel, keepgalmodelfree=keepgalmodelfree, keepisomodelfree=keepisomodelfree, gal_prefactor_value=gal_prefactor_value, gal_index_value=gal_index_value, iso_normalization_value=iso_normalization_value)

    #fix spectral parameters of target_source
    #gta.free_source(target_source, free=False)
    #gta.free_source(target_source, free=True, pars='norm')

    if args.makelc == 1:
        # prepare time_bins
        log.info('\n\n# prepare time bins')
        with open(args.fermiconf) as f:
            cfg = yaml.load(f)
        tmin = cfg['selection']['tmin']
        tmax = cfg['selection']['tmax']
        log.info('\ntime interval from ' + str(tmin) + ' to ' + str(tmax))
        daysfile = args.apfile
        # verify the file exists
        if not isfile(daysfile):
            log.info(str(daysfile), 'not found.')
            raise FileNotFoundError(streamplot(daysfile), 'not found.')
        # find time bins
        days = pd.read_csv(daysfile, sep=' ')
        # be carreful on this selection
        bins = days[days['start_met'] >= tmin]
        bins = bins[bins['stop_met'] <= tmax]
        log.info('\nnumber of "good" time bins: ' + str(len(bins)))
        first = [t for t in bins['start_met']][0]
        last = [t for t in bins['stop_met']][-1]
        log.info('\nfirst bin starts at --->' + str(first))
        log.info('\nlast bin ends at --->' + str(last))
        time_bins = list(t for t in bins['start_met'])
        time_bins.append(last)

        # LIGHTCURVE (bin 1 year-31535000)(1 week- 604800)
        log.info('\n\n#### LIGHTCURVE w/ selected time bins ---> gta.lightcurve()')
        lc = gta.lightcurve(target_source, time_bins=time_bins, write_fits=False, write_npy=True, make_plots=True, save_bin_data=False)

    elif args.makelc == 2:
        log.info('\n\n#### LIGHTCURVE w/ fixed binsize = ' + str(args.binsize) + ' ---> gta.lightcurve()')
        lc = gta.lightcurve(target_source, binsz=int(args.binsize), write_fits=False, write_npy=True, make_plots=True, save_bin_data=False)
    elif args.makelc == 3:
        log.info('\n\n#### LIGHTCURVE w/ selected interval time bin between tmin and tmax ---> gta.lightcurve()')
	# prepare time_bins
        log.info('\n\n# prepare time bins')
        with open(args.fermiconf) as f:
            cfg = yaml.load(f)
        tmin = cfg['selection']['tmin']
        tmax = cfg['selection']['tmax']
        log.info('\ntime interval from ' + str(tmin) + ' to ' + str(tmax))
        time_bins = [tmin, tmax]
        lc = gta.lightcurve(target_source, time_bins=time_bins, write_fits=False, write_npy=True, make_plots=True, save_bin_data=False)	

log.info('\n\n#### END ---> run completed, closing logfile\n')
