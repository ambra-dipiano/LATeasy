# *****************************************************************************
# Copyright (C) 2022 INAF
# This software is distributed under the terms of the BSD-3-Clause license
#
# This software is intended to generate the fermipy configuration and 
# other execution scripts to run the analysis
# *****************************************************************************


import argparse
import yaml
import pandas as pd
from os import system
from os.path import join, abspath, isfile, basename
from lateasy.utils.functions import set_logger

parser = argparse.ArgumentParser(description='Fermi/LAT data analysis pipeline')
parser.add_argument('--pipeconf',  type=str, required=True, help='configuration file')
parser.add_argument('--fermiconf',  type=str, required=True, help='configuration file')
args = parser.parse_args()

# load yaml configurations
with open(args.pipeconf) as f:
    pipeconf = yaml.safe_load(f)
with open(args.fermiconf) as f:
    fermiconf = yaml.safe_load(f)

# logging
logname = join(pipeconf['path']['output'], basename(__file__).replace('.py','.log'))
log = set_logger(filename=logname, level=pipeconf['execute']['loglevel'])
log.info('Logging: ' + logname)

# generate all execution scripts and configuration
def generate(name, tmin, tmax, emax, queue, data):
    # define file names
    dirname = join(pipeconf['path']['output'], name+"_"+str(tmin)+"_"+str(tmax))
    ymlname = join(pipeconf['path']['output'], name+"_"+str(tmin)+"_"+str(tmax)+"_fermiconf.yml")
    ymlpipe = join(pipeconf['path']['output'], name+"_"+str(tmin)+"_"+str(tmax)+"_pipeconf.yml")
    llname = join(pipeconf['path']['output'], name+"_"+str(tmin)+"_"+str(tmax)+".ll")
    shname = join(pipeconf['path']['output'], name+"_"+str(tmin)+"_"+str(tmax)+".sh")
    log.debug('Job directory: ' + dirname)
    log.debug('Job pipe configuration: ' + ymlpipe)
    log.debug('Job fermipy configuration: ' + ymlname)
    log.debug('Job bash executable: ' + shname)
    log.debug('Job slurm script: ' + llname)
    
    # complete fermipy configuration
    fermiconf['selection']['emax'] = emax
    fermiconf['selection']['tmin'] = tmin
    fermiconf['selection']['tmax'] = tmax
    fermiconf['fileio']['outdir'] = dirname
    fermiconf['model']['galdiff'] = join(pipeconf['path']['galdir'], pipeconf['background']['galmodel'] + '.fits')
    fermiconf['model']['isodiff'] = pipeconf['background']['isomodel'] + '.txt'
    fermiconf['model']['catalogs'] = join(pipeconf['path']['models'], pipeconf['file']['inputmodel'])

    # write fermipy yaml configuration
    with open(ymlname, "w+") as f:
        yaml.dump(fermiconf, f, default_flow_style=False)

    # define background values
    if not data.empty:
        log.info('Initialise background from "bkgresults" data.')

        # log info on free/fix background
        if pipeconf['background']['isofree']:
            log.info('Isotropic background configuration: free')
        else:
            log.info('Isotropic background configuration: fix')
        if pipeconf['background']['galfree']:
            log.info('Galactic background configuration: free')
        else:
            log.info('Galactic background configuration: fix')

        # get background from previous results
        for index, row in data.iterrows():
            if tmin >= row["tmin"] and tmin <= row["tmax"]:
                pipeconf['background']['isonorm'] = row["iso_Normalization_value"]
                pipeconf['background']['galnorm'] =  row["gal_Prefactor_value"]
                pipeconf['background']['galindex'] = row["gal_Index_value"]
                log.info('Background from precomputed lightcurve results')
    
    # get background from configuration
    elif all([pipeconf['background']['isonorm'], pipeconf['background']['galnorm'], pipeconf['background']['galindex']]) is not None:
        # from configuration
        log.info('Background from "background" section of the pipe.yml configuration file')

    # set background to default
    else:
        # from default values
        pipeconf['background']['isonorm'] = 1
        pipeconf['background']['galnorm'] = 1
        pipeconf['background']['galindex'] = 0
        log.info('Background values set to default (isonorm=1, galnorm=1, galindex=0)')

    # write fermipy yaml configuration
    with open(ymlpipe, "w+") as f:
        yaml.dump(pipeconf, f, default_flow_style=False)

    # compose bash executable script
    job = [
    '#!/bin/bash\n\n',
    #'source /opt/module/anaconda-3.7\n',
    pipeconf['slurm']['activation'] + ' activate ' + pipeconf['slurm']['envname'],
    '\nexport FERMIDATA=' + pipeconf['path']['data'],
    '\nexport FERMI_DIFFUSE_DIR=' + pipeconf['path']['galdir'],
    '\npython ' + join(abspath(__file__).replace(basename(__file__), ''), 'run_fermianalysis.py') + ' --fermiconf ' + ymlname + ' --pipeconf ' + ymlpipe, 
    '\ncp ' + dirname + '.* ' + dirname,
    '\ncd ' + dirname,
    '\npython ' + join(abspath(__file__).replace(basename(__file__), ''), 'run_sensitivity.py'),
    '\nmv ' + join(dirname, 'ltcube_00.fits') + ' ' + join(dirname, 'ltcube_00.fits.tmp'),
    '\nrm ' + join(dirname, '*.fits'),
    '\nmv ' + join(dirname, 'ltcube_00.fits.tmp') + ' ' + join(dirname, 'ltcube_00.fits'),
    '\nrm ' + join(dirname, '*.par'),
    ]

    # write bash executable script
    with open(shname, "w+") as sh:
        sh.writelines(job)

    # load slurm job submission template
    with open(pipeconf['slurm']['template']) as ll:
        job = ll.read()

    # replace executable bash filename 
    job = job.replace('$BASH_NAME$', shname)
    job = job.replace('$OUTPUT$', pipeconf['path']['output'])

    # write job submission script
    with open(llname, "w+") as ll:
        ll.write(job)

    # submit job to slurm
    if pipeconf['slurm']['sbatch']:
        system("sbatch --partition=" + queue + " " + llname)

# verify file with result to extract isomodel and galmodel parameters 
if pipeconf['slurm']['bkgresults'] is not None:
    log.info('Verify "bkgresults" input file.')
    if not isfile(pipeconf['slurm']['bkgresults']):
        log.warning(f"File {pipeconf['slurm']['bkgresults']} not found. \nTrying in output folder default path.")
        if not isfile(join(pipeconf['path']['output'], pipeconf['slurm']['bkgresults'])):
            log.error(f"File {pipeconf['slurm']['bkgresults']} not found. Revert to background default setting.")
            pipeconf['slurm']['bkgresults'] = None
        else: 
            log.info(f"File {pipeconf['slurm']['bkgresults']} found in {pipeconf['path']['output']}.")
            pipeconf['slurm']['bkgresults'] = join(pipeconf['path']['output'], pipeconf['slurm']['bkgresults'])
    else: 
        log.info(f"File {pipeconf['slurm']['bkgresults']} found.")
else:
    log.info('No "bkgresults" file provided as input, using set values.')

# load background lightcurve if provided (if absent take then compute from default)
if pipeconf['slurm']['bkgresults'] is not None and isfile(pipeconf['slurm']['bkgresults']):
    f = pipeconf['slurm']['bkgresults']
    data = pd.read_csv(f, header=0, sep=" ")
    log.info(f"Background data loaded from {pipeconf['slurm']['bkgresults']}")
else:
    # create empty data
    log.info('Creating empty background DataFrame.')
    column_names = ["a", "b", "c"]
    data = pd.DataFrame(columns = column_names)

# assign variables
name = pipeconf['slurm']['name']
tmin =  pipeconf['slurm']['tmin']
tmax =  pipeconf['slurm']['tmax']
mode =  pipeconf['slurm']['mode']
binsize = pipeconf['slurm']['timebin']
emax = pipeconf['slurm']['emax']
queue = pipeconf['slurm']['queue']

# submitt jobs based on "mode"
log.info('Slurm job generator mode: ' + mode)
if mode.lower() == 'hours':
    # compute at hours timescale from 1 day prior tmin to 1 day after tmax
    for i in range(tmin-86400, tmax+86400, 3600):
        log.info('Time interval ' + str(i) + ' - ' + str(i+binsize))
        generate(name, i, i+binsize, emax, queue, data)
elif mode.lower() == 'fix':
    # compute at given timescale from tmin to tmax
    for i in range(tmin, tmax, binsize):
        log.info('Time interval ' + str(i) + ' - ' + str(i+binsize))
        generate(name, i, i+binsize, emax, queue, data)
elif mode.lower() == 'integral':
    # compute integral from tmin to tmax
    log.info('Time interval ' + str(tmin) + ' - ' + str(tmax))
    generate(name, tmin, tmax, emax, queue, data)
else:
    # invalid "mode" configuration
    log.error('Invalid submission mode: ' + mode.lower())
    raise ValueError('Invalid submission mode: ' + mode.lower())

log.info('Copy pipeline configuration in output folder.')
system('cp ' + args.pipeconf + ' ' + pipeconf['path']['output'])
