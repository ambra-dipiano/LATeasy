from matplotlib import streamplot
import yaml
import matplotlib
matplotlib.use('agg')
global plt
import matplotlib.pyplot as plt
plt.switch_backend('agg')
import pandas as pd
from fermipy.gtanalysis import GTAnalysis
from os. path import join, isfile
import numpy as np
import argparse

def list_nans():
    nan_sources = list()
    for src in gta.roi.get_sources():
        if str(src['ts']) == 'nan' and str(src.name) not in (mysource, 'isodiff', 'galdiff'):
            nan_sources.append(str(src.name))
    return nan_sources
    
def manageGalIsoParameters(galmodel, isomodel, keepgalmodelfree = False, keepisomodelfree = False, gal_prefactor_value = 1, gal_index_value = 0, iso_normalization_value = 1):

    #set the initial value of gal/Index and gal/Prefactor parameter
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
parser = argparse.ArgumentParser(description='ADD SCRIPT DESCRIPTION HERE')
parser.add_argument('-f', '--fileconfig', type=str, required=True, help='configuration file')
parser.add_argument('--isofree', type=str, default='True', help="set True to keep isomodel free, set False to keep fixed and get values from bkgfile")
parser.add_argument('--galfree', type=str, default='True', help="set True to keep galmodel free, set False to keep fixed and get values from bkgfile")
parser.add_argument('--iso_normalization', type=str, default='1', help="The value of iso_normalization if isofree is False")
parser.add_argument('--gal_prefactor', type=str, default='1', help="The value of gal_prefactor_value if galfree is False")
parser.add_argument('--gal_index', type=str, default='0', help="The value of gal_index_value if galfree is False")
parser.add_argument('--makelc', type=int, default='1', choices=[0, 1, 2, 3], help="set 0 to skip LC; set 1 to perform LC selecting bins from file; set 2 to perform LC with fixed binsize;")
parser.add_argument('--apfile', type=str, default='/data01/projects/IGRJ17354-3255/FERMI/LC/igrDaysMET_filtered.out', help='')
parser.add_argument('--binsize', type=int, default=86400, help='number of bins for LC')
parser.add_argument('--skipsed', type=str, default='False', help="set True to skip SED or set False to compute SED")
parser.add_argument('--skiploc', type=str, default='True', help="set True to skip localisation or set False to compute localisation")
args = parser.parse_args()

print('######### makelc ' + str(args.makelc))

# ---------------------------------------------------------------- setup
print(args.fileconfig)
mysource='IGRJ17354-3255'

logname = 'cmd6fermi_' + str(args.fileconfig).replace('.yaml','') + '.log'
logfile = open(logname, 'w+')
print('#### LOGGING --->', logname)
logfile.write('\n#### LOGGING ---> ' + str(logname))

#gal and iso management - default values
galmodel='gll_iem_v07'
keepgalmodelfree = True

isomodel='iso_P8R3_SOURCE_V2_v1'
keepisomodelfree = True

# list of sources that must be kept free
# variable sources within 10 deg
variable_sources = {'Source_Name': ['4FGL J1802.6-3940'], 'ROI_Center_Distance': [8.682], 'Signif_Avg': [65.025505]}
# extended sources within 5 deg
extended_sources = {'Source_Name': ['4FGL J1745.8-3028e'], 'Extended_Source_Name': ['FGES J1745.8-3028'], 'ROI_Center_Distance': [3.31], 'Signif_Avg': [29.66472816467285], 'Normalisation': [9.332740743411838, 2.2291994], 'Normalisation_Error': [np.nan, np.nan]}

# input parameters
if args.galfree == 'True':
    keepgalmodelfree = True
    gal_prefactor_value = 1
    gal_index_value = 0
elif args.galfree == 'False':
    gal_prefactor_value = float(args.gal_prefactor)
    gal_index_value = float(args.gal_index)
    keepgalmodelfree = False
else:
    logfile.write('\n#### PARAMETERS ERROR ---> galfree')

if args.isofree == 'True':
    keepisomodelfree = True
    iso_normalization_value = 1 
elif args.isofree == 'False':
    iso_normalization_value = float(args.iso_normalization)
    keepisomodelfree = False
else:
    logfile.write('\n#### PARAMETERS ERROR ---> isofree')

logfile.write('\n\nSkip SED: ' + args.skipsed.capitalize() + '\nMake LC: ' + str(args.makelc))

# ----------------------------------------------------------------- analysis
gta = GTAnalysis(args.fileconfig,logging={'verbosity' : 3})
logfile.write('\n\n#### SETUP ---> gta.setup()')
gta.print_roi()
gta.setup()
# 1st optimaze 
opt1 = gta.optimize()
gta.print_roi()
fname = 'roi1_optimize'
gta.write_roi(fname)
logfile.write('\n\n# 1st optimize saved in ---> ' + str(fname))

# ----------------------------------------------------------------- preliminary fit
logfile.write('\n\n#### PRELIMINARY FIT')
#manage gal and iso parameters
manageGalIsoParameters(galmodel, isomodel, keepgalmodelfree=keepgalmodelfree, keepisomodelfree=keepisomodelfree, gal_prefactor_value=gal_prefactor_value, gal_index_value=gal_index_value, iso_normalization_value=iso_normalization_value)
logfile.write('\n# manage gal and iso parameters')
logfile.write('\n--- galmodel ---')
logfile.write('\nmodel = ' + str(galmodel) + '\nfree = ' + str(keepgalmodelfree))
logfile.write('\nprefactor = ' + str(gal_prefactor_value) + '\nindex = ' + str(gal_index_value))
logfile.write('\n--- isomodel ---')
logfile.write('\nmodel = ' + str(isomodel) + '\nfree = ' + str(keepisomodelfree))
logfile.write('\nnormalisation = ' + str(iso_normalization_value))
# get sources
gta.print_roi()
sources = gta.get_sources()
print('target & bkgs before fit1:')
for src in sources:
    if src['name'] in (galmodel, isomodel, mysource):
        print(src)

# execute fit
prefit = gta.fit(update=True)
sources = gta.get_sources()
fname = 'roi1_fit_model'
gta.write_roi(fname)
logfile.write('\n\n# 1st fit saved in ---> ' + str(fname))

# ------------------------------------------------------------- delete src ts < 1
logfile.write('\n\n# delete sources with TS < 1 or TS = nan')
#alternative 1 to eliminate sources. Removed minmax_npred=[-1,4]
nan_sources = list_nans()
if len(nan_sources) != 0:
    deleted_sources = gta.delete_sources(names=nan_sources, exclude=[mysource, isomodel, galmodel])
deleted_sources = gta.delete_sources(minmax_ts=[None,1], exclude=[mysource, isomodel, galmodel])

# check bkgs and mysource are kept
for d in deleted_sources:
    if d.name in (isomodel, galmodel, mysource):
        logfile.write('\n', str(d.name), ' was deleted ---> add back')
        gta.add_source(d.name, d)
        
# 2nd optimaze 
opt1 = gta.optimize()
fname = 'roi2_optimize'
gta.write_roi(fname)
logfile.write('\n\n# 2nd optimize saved in ---> ' + str(fname))

#manage gal and iso parameters
manageGalIsoParameters(galmodel, isomodel, keepgalmodelfree=keepgalmodelfree, keepisomodelfree=keepisomodelfree, gal_prefactor_value=gal_prefactor_value, gal_index_value=gal_index_value, iso_normalization_value=iso_normalization_value)

print('target & bkgs after optimize2:')
for src in sources:
    if src['name'] in (galmodel, isomodel, mysource):
        print(src)

# ----------------------------------------------------------------------- 1st sed
if args.skipsed.capitalize() == 'False':
    logfile.write('\n\n#### SED ---> gta.sed()')
    gta.sed(mysource, prefix='sed_cl95', free_background=True, free_radius=None, write_fits=False, write_npy=True, outfile='sed', make_plots=True)

# ------------------------------------------------------------------------ 2nd fit
fit_results = gta.fit(update=True)
print('Fit Quality: ',fit_results['fit_quality'])
print('Fit Status: ',fit_results['fit_status'])
fname = 'roi2_fit_model'
gta.write_roi(fname)
sources = gta.get_sources()
logfile.write('\n\n# 2nd fit saved in ---> ' + str(fname))
print("### Results of roi2_fit_model")
for src in gta.roi.get_sources():
    print(src.name + " " + str(src['ts']))
    logfile.write(src.name + " " + str(src['ts']))

print("target & bkgs after fit2:")
for src in sources:
    if src['name'] in (galmodel, isomodel, mysource):
        print(src)

# ------------------------------------------------------------------------ 1st localise
if args.skiploc.capitalize() == 'False':
    logfile.write('\n\n#### UPDATE TARGET POSITION')
    for src in gta.roi.get_sources():
        if src.name == mysource:
            if src['ts'] > 10:
                logfile.write('\ntarget TS > 10 ---> gta.localize()')
                loc = gta.localize(mysource, free_background=True, update=True, make_plots=True, write_fits=False, write_npy=True)
                logfile.write('\n--- check new position ---')
                if loc.pos_offset < loc.pos_r95:
                    logfile.write('\nwithin 0.95 confidence radius ---> keep new position')
                    src.spatial_pars['RA']['value'] = loc.ra
                    src.spatial_pars['DEC']['value'] = loc.dec
                    fname = 'fit_model_loc1'
                    gta.write_roi(fname)
                    logfile.write('\n # localisation saved in ---> ' + str(fname))
                    # ------------------------------------------------------- 2nd sed
                    if args.skipsed.capitalize() == 'False':
                        logfile.write('\n\n#### SED ---> gta.sed()')
                        gta.sed(mysource, prefix='sed2_cl95', free_background=True, free_radius=None, write_fits=False, write_npy=True, make_plots=True)
                else: 
                    logfile.write('\noutside 0.95 confidence radius ---> revert to previous position')
                    src.spatial_pars['RA']['value'] = loc.ra_preloc
                    src.spatial_pars['DEC']['value'] = loc.dec_preloc
            else:
                logfile.write('\ntarget TS < 10 ---> keep current position')

# --------------------------------------------------------------------- lightcurve
if args.makelc != 0:
    # change the hypothesis of the sources and put all sources with norm fixed
    logfile.write('\n\n######## LC')
    logfile.write('\n\n# freeze all sources')
    gta.free_sources(pars='norm', free=False)

    # Free normalisation of mysource and source within < 2 deg. Could be between 2 and 5
    gta.free_source(mysource, distance=2.0, pars='norm', free=True)
    logfile.write('\n\n# free "norm" for target and sources within 2 deg')

    # variable and extended sources
    for src in gta.roi.get_sources():
        # for variable srcs, put norm true if ts > 50
        if src.name in variable_sources['Source_Name']:
            # update significance
            variable_sources['Signif_Avg'][variable_sources['Source_Name'].index(src.name)] = float(src['ts'])
            logfile.write('\n --- variable source ---')
            if src['ts'] > 50:
                logfile.write('\nname = ' + src.name + ' TS > 50 ---> free "norm"')
                gta.free_source(src.name, pars='norm', free=True)
            else:
                logfile.write('\nname = ' + src.name + ' TS < 50 ---> keep frozen')
        # for extended srcs (<ROI), if the difference of the parameters with respect to the catalog value is too much, fix the parameter source at 4FGL value
        if src.name in extended_sources['Extended_Source_Name']:
            index = extended_sources['Extended_Source_Name'].index(src.name)
            norm4fgl = extended_sources['Normalisation'][index]
            norm_error4fgl =  extended_sources['Normalisation_Error'][index]
            norm = float(src.spectral_pars['Prefactor']['value'])
            norm_error = float(src.spectral_pars['Prefactor']['error'])
            logfile.write('\n --- extended source ---')
            if src['ts'] > 10:
                logfile.write('\nname = ' + src.name + ' TS > 10 ---> check "norm" errors')
                if norm > (norm4fgl + 2.0 * norm_error4fgl) or norm < (norm4fgl - 2.0 * norm_error4fgl):
                    logfile.write('\nerrors outside range ---> revert to 4FGL value')
                    src.spectral_pars['Prefactor']['value'] = norm4fgl
                    gta.free_source(src.name, pars='norm', free=False)
                else:
                    logfile.write('\nerrors within range ---> keep at current value')
            else:
                logfile.write('\nname = ' + src.name + ' TS < 10 ---> keep frozen')
        # get backgrounds values 
        if src.name == galmodel:
            logfile.write('\n--- update galmodel ---' )
            gal_prefactor_value = float(src.spectral_pars['Prefactor']['value'])
            gal_index_value = float(src.spectral_pars['Index']['value'])
            logfile.write('\nprefactor = ' + str(gal_prefactor_value) + '\nindex = ' + str(gal_index_value))
        if src.name ==  isomodel:
            logfile.write('\n--- update isomodel ---' )
            iso_normalization_value = float(src.spectral_pars['Normalization']['value'])
            logfile.write('\nnormalisation = ' + str(iso_normalization_value))

    # keep gal and iso model parameters fixed
    logfile.write('\n\n# freeze background parameters')
    keepgalmodelfree = False
    keepisomodelfree = False
    manageGalIsoParameters(galmodel, isomodel, keepgalmodelfree=keepgalmodelfree, keepisomodelfree=keepisomodelfree, gal_prefactor_value=gal_prefactor_value, gal_index_value=gal_index_value, iso_normalization_value=iso_normalization_value)

    #fix spectral parameters of mysource
    #gta.free_source(mysource, free=False)
    #gta.free_source(mysource, free=True, pars='norm')

    if args.makelc == 1:
        # prepare time_bins
        logfile.write('\n\n# prepare time bins')
        with open(args.fileconfig) as f:
            cfg = yaml.load(f)
        tmin = cfg['selection']['tmin']
        tmax = cfg['selection']['tmax']
        logfile.write('\ntime interval from ' + str(tmin) + ' to ' + str(tmax))
        daysfile = args.apfile
        # verify the file exists
        if not isfile(daysfile):
            logfile.write(str(daysfile), 'not found.')
            raise FileNotFoundError(streamplot(daysfile), 'not found.')
        # find time bins
        days = pd.read_csv(daysfile, sep=' ')
        # be carreful on this selection
        bins = days[days['start_met'] >= tmin]
        bins = bins[bins['stop_met'] <= tmax]
        logfile.write('\nnumber of "good" time bins: ' + str(len(bins)))
        first = [t for t in bins['start_met']][0]
        last = [t for t in bins['stop_met']][-1]
        logfile.write('\nfirst bin starts at --->' + str(first))
        logfile.write('\nlast bin ends at --->' + str(last))
        time_bins = list(t for t in bins['start_met'])
        time_bins.append(last)

        # LIGHTCURVE (bin 1 year-31535000)(1 week- 604800)
        logfile.write('\n\n#### LIGHTCURVE w/ selected time bins ---> gta.lightcurve()')
        lc = gta.lightcurve(mysource, time_bins=time_bins, write_fits=False, write_npy=True, make_plots=True, save_bin_data=False)

    elif args.makelc == 2:
        logfile.write('\n\n#### LIGHTCURVE w/ fixed binsize = ' + str(args.binsize) + ' ---> gta.lightcurve()')
        lc = gta.lightcurve(mysource, binsz=int(args.binsize), write_fits=False, write_npy=True, make_plots=True, save_bin_data=False)
    elif args.makelc == 3:
        logfile.write('\n\n#### LIGHTCURVE w/ selected interval time bin between tmin and tmax ---> gta.lightcurve()')
	# prepare time_bins
        logfile.write('\n\n# prepare time bins')
        with open(args.fileconfig) as f:
            cfg = yaml.load(f)
        tmin = cfg['selection']['tmin']
        tmax = cfg['selection']['tmax']
        logfile.write('\ntime interval from ' + str(tmin) + ' to ' + str(tmax))
        time_bins = [tmin, tmax]
        lc = gta.lightcurve(mysource, time_bins=time_bins, write_fits=False, write_npy=True, make_plots=True, save_bin_data=False)	

logfile.write('\n\n#### END ---> run completed, closing logfile\n')
logfile.close()
