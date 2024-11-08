# *****************************************************************************
# Copyright (C) 2022 INAF
# This software is distributed under the terms of the BSD-3-Clause license
#
# This software is intended to run the fermi analysis 
# *****************************************************************************

import yaml
import argparse
import matplotlib
import pandas as pd
from os.path import isfile, join
from matplotlib import streamplot
from lateasy.utils.functions import set_logger

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
        gta.free_source(galmodel, free=True)
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
    pipeconf = yaml.safe_load(f)
with open(args.fermiconf) as f:
    fermiconf = yaml.safe_load(f)

# switch matplotlib backend and complete imports
if pipeconf['execute']['agg_backend']:
    matplotlib.use('agg')
import matplotlib.pyplot as plt
plt.switch_backend('agg')
from fermipy.gtanalysis import GTAnalysis


# logging
if pipeconf['slurm']['name'] is None:
    logname = join(pipeconf['path']['output'], pipeconf['target']['name'] + '_' + str(fermiconf['selection']['tmin']) + '_' + str(fermiconf['selection']['tmax']) + '.log')
else:
    logname = join(pipeconf['path']['output'], pipeconf['slurm']['name'] + '_' + str(fermiconf['selection']['tmin']) + '_' + str(fermiconf['selection']['tmax']) + '.log')

log = set_logger(filename=logname, level=pipeconf['execute']['loglevel'])

# ---------------------------------------------------------------- setup
target_source = pipeconf['target']['4FGLname']
log.info('\n#### LOGGING ---> ' + str(logname))

# free the following sources
variable_sources = pipeconf['variable_sources']
extended_sources = pipeconf['extended_sources']
# variables
if variable_sources is None:
    variable_names = []
else:
    variable_names = [variable_sources[name] for name in variable_sources.keys()]
    log.debug('variable sources:')
    for var in variable_names:
        log.debug(var)
# extended
if extended_sources is None:
    extended_names = []
else:
    extended_names = [extended_sources[name] for name in extended_sources.keys()]
    log.debug('extended sources:')
    for ext in extended_names:
        log.debug(ext)

# background parameters
galmodel = pipeconf['background']['galmodel']
isomodel = pipeconf['background']['isomodel']
keepgalmodelfree = pipeconf['background']['galfree']
keepisomodelfree = pipeconf['background']['isofree']
# set starting values or defaults
if pipeconf['background']['galnorm'] is None:
    gal_prefactor_value = 1
else:
    gal_prefactor_value = pipeconf['background']['galnorm']
if pipeconf['background']['galindex'] is None:
    gal_index_value = 0
else:
    gal_index_value = pipeconf['background']['galindex']
if pipeconf['background']['isonorm'] is None:
    iso_normalization_value = 1 
else:
    iso_normalization_value = pipeconf['background']['isonorm']

log.info('\n# initial gal and iso parameters')
log.info('\n--- galmodel ---')
log.info('\nmodel = ' + str(galmodel) + '\nfree = ' + str(keepgalmodelfree))
log.info('\nprefactor = ' + str(gal_prefactor_value) + '\nindex = ' + str(gal_index_value))
log.info('\n--- isomodel ---')
log.info('\nmodel = ' + str(isomodel) + '\nfree = ' + str(keepisomodelfree))
log.info('\nnormalisation = ' + str(iso_normalization_value))

log.info('\n\n# execution setting')
log.info("\nExecute SED: " + str(pipeconf['execute']['sed']))
log.info("Execute LOC: " + str(pipeconf['execute']['localise']))
log.info("Execute LC: " + str(pipeconf['execute']['lc']))


# ----------------------------------------------------------------- analysis
gta = GTAnalysis(args.fermiconf, logging={'verbosity' : pipeconf['execute']['verbose']})
log.info('\n\n#### SETUP ---> gta.setup()')
gta.print_roi()
gta.setup()
# 1st optimaze m,,mmjn
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
log.debug('target & bkgs before fit1:')
for src in sources:
    if src['name'] in (galmodel, isomodel, target_source):
        log.debug(src)

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

log.debug('target & bkgs after optimize2:')
for src in sources:
    if src['name'] in (galmodel, isomodel, target_source):
        log.debug(src)

# ----------------------------------------------------------------------- 1st sed
if pipeconf['execute']['sed']:
    log.info('\n\n#### SED ---> gta.sed()')
    gta.sed(target_source, prefix='sed_cl95', free_background=True, free_radius=None, write_fits=False, write_npy=True, outfile='sed', make_plots=True)

# ------------------------------------------------------------------------ 2nd fit
fit_results = gta.fit(update=True)
log.debug('Fit Quality: ' + str(fit_results['fit_quality']))
log.debug('Fit Status: ' + str(fit_results['fit_status']))
fname = 'roi2_fit_model'
gta.write_roi(fname)
sources = gta.get_sources()
log.info('\n\n# 2nd fit saved in ---> ' + str(fname))
log.debug("### Results of roi2_fit_model")
for src in gta.roi.get_sources():
    log.info(src.name + " " + str(src['ts']))

log.debug("target & bkgs after fit2:")
for src in sources:
    if src['name'] in (galmodel, isomodel, target_source):
        log.debug(src)

# ------------------------------------------------------------------------ 1st localise
if pipeconf['execute']['localise']:
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
                    if pipeconf['execute']['sed']:
                        log.info('\n\n#### SED ---> gta.sed()')
                        gta.sed(target_source, prefix='sed2_cl95', free_background=True, free_radius=None, write_fits=False, write_npy=True, make_plots=True)
                else: 
                    log.info('\noutside 0.95 confidence radius ---> revert to previous position')
                    src.spatial_pars['RA']['value'] = loc.ra_preloc
                    src.spatial_pars['DEC']['value'] = loc.dec_preloc
            else:
                log.info('\ntarget TS < 10 ---> keep current position')

# --------------------------------------------------------------------- lightcurve
if pipeconf['execute']['lc']:
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
        if src.name in variable_names:
            # update significance
            variable_sources[src.name]['Signif_Avg'] = float(src['ts'])
            log.info('\n --- variable source ---')
            if src['ts'] > 50:
                log.info('\nname = ' + src.name + ' TS > 50 ---> free "norm"')
                gta.free_source(src.name, pars='norm', free=True)
            else:
                log.info('\nname = ' + src.name + ' TS < 50 ---> keep frozen')
        # for extended srcs (<ROI), if the difference of the parameters with respect to the catalog value is too much, fix the parameter source at 4FGL value
        if src.name in extended_names:
            norm4fgl = extended_sources[src.name]['Normalisation']
            norm_error4fgl =  extended_sources[src.names]['Normalisation_Error']
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

    if pipeconf['lightcurve']['bintype'].lower() == 'filter':
        # prepare time_bins
        log.info('\n\n# prepare time bins')
        with open(args.fermiconf) as f:
            cfg = yaml.safe_load(f)
        tmin = cfg['selection']['tmin']
        tmax = cfg['selection']['tmax']
        log.info('\ntime interval from ' + str(tmin) + ' to ' + str(tmax))
        daysfile = join(pipeconf['path']['data'], pipeconf['file']['photometry'])
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

    elif pipeconf['lightcurve']['bintype'] == 'fix':
        log.info('\n\n#### LIGHTCURVE w/ fixed binsize = ' + str(pipeconf['lightcurve']['binsize']) + ' ---> gta.lightcurve()')
        lc = gta.lightcurve(target_source, binsz=pipeconf['lightcurve']['binsize'], write_fits=False, write_npy=True, make_plots=True, save_bin_data=False)
    elif pipeconf['lightcurve']['bintype'] == 'integral':
        log.info('\n\n#### LIGHTCURVE w/ selected interval time bin between tmin and tmax ---> gta.lightcurve()')
	# prepare time_bins
        log.info('\n\n# prepare time bins')
        with open(args.fermiconf) as f:
            cfg = yaml.safe_load(f)
        tmin = cfg['selection']['tmin']
        tmax = cfg['selection']['tmax']
        log.info('\ntime interval from ' + str(tmin) + ' to ' + str(tmax))
        time_bins = [tmin, tmax]
        lc = gta.lightcurve(target_source, time_bins=time_bins, write_fits=False, write_npy=True, make_plots=True, save_bin_data=False)	

log.info('\n\n#### END ---> run completed, closing logfile\n')
