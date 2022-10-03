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
    ymlname = join(pipeconf['path']['output'], name+"_"+str(tmin)+"_"+str(tmax)+".yml")
    llname = join(pipeconf['path']['output'], name+"_"+str(tmin)+"_"+str(tmax)+".ll")
    shname = join(pipeconf['path']['output'], name+"_"+str(tmin)+"_"+str(tmax)+".sh")
    log.debug('Job directory:' + dirname)
    log.debug('Job fermipy configuration:' + ymlname)
    log.debug('Job bash executable:' + shname)
    log.debug('Job slurm script:' + llname)
    
    # complete fermipy configuration
    fermiconf['selection']['emax'] = emax
    fermiconf['selection']['tmin'] = tmin
    fermiconf['selection']['tmax'] = tmax
    fermiconf['fileio']['outdir'] = dirname

    # write fermipy yaml configuration
    with open(ymlname, "w+") as f:
        yaml.dump(fermiconf, f, default_flow_style=False)

    # define background values
    if not data.empty:
        # from previous results
        for index, row in data.iterrows():
            if tmin >= row["tmin"] and tmin <= row["tmax"]:
                pipeconf['background']['isonorm'] = row["iso_P8R3_SOURCE_V2_v1_Normalization_value"]
                pipeconf['background']['galnorm'] =  row["gll_iem_v07_Prefactor_value"]
                pipeconf['background']['galindex'] = row["gll_iem_v07_Index_value"]
                log.info('Background from precomputed lightcurve results')
    elif all([pipeconf['background']['isonorm'], pipeconf['background']['galnorm'], pipeconf['background']['galindex']]) is not None:
        # from configuration
        log.info('Background from configuration file')
    else:
        # from default values
        pipeconf['background']['isonorm'] = 1
        pipeconf['background']['galnorm'] = 1
        pipeconf['background']['galindex'] = 0
        log.info('Background from default values')

    # compose bash executable script
    job = [
    '#!/bin/bash\n\n',
    'source activate ' + pipeconf['slurm']['envname'],
    '\nexport FERMIDATA=' + pipeconf['path']['data'],
    '\nexport FERMI_DIFFUSE_DIR=' + pipeconf['path']['galdir'],
    '\npython ' + join(abspath(__file__).replace(basename(__file__), ''), 'run_fermianalysis.py') + ' --fermiconf ' + ymlname + ' --pipeconf ' + args.pipeconf, 
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

    # write job submission script
    with open(llname, "w+") as ll:
        ll.write(job)

    # submit job to slurm
    if pipeconf['slurm']['sbatch']:
        system("sbatch --partition=" + queue + " " + llname)


# file with result to extract isomodel and galmodel parameters (if absent take then compute from default)
if pipeconf['slurm']['bkgresults'] is not None and isfile(join(pipeconf['path']['output'], pipeconf['slurm']['bkgresults'])):
    f = pipeconf['slurm']['bkgresults']
    data = pd.read_csv(f, header=0, sep=" ")
else:
    # create empty data
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
log.info('Slurm job generator mode:' + mode)
if mode.lower() == 'hours':
    # compute at hours timescale from 1 day prior tmin to 1 day after tmax
    for i in range(tmin-86400, tmax+86400, 3600):
        generate(name, i, i+binsize, emax, queue, data)
elif mode.lower() == 'fix':
    # compute at given timescale from tmin to tmax
    for i in range(tmin, tmax, binsize):
        generate(name, i, i+binsize, emax, queue, data)
elif mode.lower() == 'integral':
    # compute integral from tmin to tmax
    generate(name, tmin, tmax, emax, queue, data)
else:
    # invalid "mode" configuration
    log.error('Invalid "mode" configuration:' + mode.lower())
    raise ValueError('Invalid "mode" configuration:' + mode.lower())


