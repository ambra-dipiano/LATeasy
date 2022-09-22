# *****************************************************************************
# Copyright (C) 2022 INAF
# This software is distributed under the terms of the BSD-3-Clause license
#
# This software is intended to generate the fermipy configuration and 
# other execution scripts to run the analysis
# *****************************************************************************


import sys
import argparse
import yaml
import pandas as pd
from os import system
from os.path import join, abspath, isfile
from lateasy.utils.functions import set_logger

parser = argparse.ArgumentParser(description='Fermi/LAT data analysis pipeline')
parser.add_argument('--pipeconf',  type=str, required=True, help='configuration file')
parser.add_argument('--fermiconf',  type=str, required=True, help='configuration file')
args = parser.parse_args()

# load yaml configurations
with open(args.pipeconf) as f:
    pipeconf = yaml.load(f)
with open(args.fermiconf) as f:
    fermiconf = yaml.load(f)

# logging
logname = join(pipeconf['path']['output'], str(__file__).replace('.py','.log'))
log = set_logger(filename=logname, level=pipeconf['execute']['loglevel'])

# generate all execution scripts and configuration
def generate(name, tmin, tmax, emax, queue, data):
    # complete fermipy configuration
    fermiconf['selection']['emax'] = emax
    fermiconf['selection']['tmin'] = tmin
    fermiconf['selection']['tmax'] = tmax
    fermiconf['fileio']['outdir'] = str(name) + "_" + str(tmin) + "_" + str(tmax)

    # define file names
    dirname = name+"_"+str(tmin)+"_"+str(tmax)
    ymlname = name+"_"+str(tmin)+"_"+str(tmax)+".yml"
    llname = name+"_"+str(tmin)+"_"+str(tmax)+".ll"
    shname = name+"_"+str(tmin)+"_"+str(tmax)+".sh"
    
    # write fermipy yaml configuration
    with open(ymlname, 'w') as f:
        yaml.dump(fermiconf, f)
    
    if pipeconf['background']['isonorm'] is None:
        pipeconf['background']['isonorm'] = 1
    if pipeconf['background']['galnorm'] is None:
        pipeconf['background']['galnorm'] = 1
    if pipeconf['background']['galindex'] is None:
        pipeconf['background']['galindex'] = 0

    if not data.empty:
        for index, row in data.iterrows():
            if tmin >= row["tmin"] and tmin <= row["tmax"]:
                pipeconf['background']['isonorm'] = row["iso_P8R3_SOURCE_V2_v1_Normalization_value"]
                pipeconf['background']['galnorm'] =  row["gll_iem_v07_Prefactor_value"]
                pipeconf['background']['galindex'] = row["gll_iem_v07_Index_value"]

    # write bash executable script
    job = f"""source activate {pipeconf['slurm']['envname']}
    export FERMIDATA={pipeconf['path']['data']}
    export FERMI_DIFFUSE_DIR={pipeconf['path']['galdir']}
    python {abspath(__file__)}/run_fermianalysis.py --fermiconf {ymlname} --pipeconf {args.pipeconf}
    cp {dirname}.* {dirname}
    cd {dirname}
    python {abspath(__file__)}/run_fermipy_sensitivity.py
    mv ltcube_00.fits ltcube_00.fits.tmp
    rm *.fits
    mv ltcube_00.fits.tmp ltcube_00.fits
    rm *.par
    cd .."""
     
    with open(shname, "w") as sh:
        sh.write(job)

    # load slurm job submission template
    with open(pipeconf['slurm']['template']) as ll:
        job = ll.read()

    # replace executable bash filename to launch
    job.replace('$BASH_NAME$', shname)
    with open(llname, "w") as ll:
        ll.write(job)

    system("sbatch --partition="+queue+" " + llname)

name = pipeconf['slurm']['name']
tmin =  pipeconf['slurm']['tmin']
tmax =  pipeconf['slurm']['tmax']
mode =  pipeconf['slurm']['mode']
timebinsize = pipeconf['slurm']['timebinsize']
emax = pipeconf['slurm']['emax']
queue = pipeconf['slurm']['queue']

# file with result to extract isomodel and galmodel parameters (if absent take then compute from default)
if pipeconf['slurm']['bkgresults'] is not None and isfile(join(pipeconf['path']['output'], pipeconf['slurm']['bkgresults'])):
    f = pipeconf['slurm']['bkgresults']
    data = pd.read_csv(f, header=0, sep=" ")
else:
    column_names = ["a", "b", "c"]
    data = pd.DataFrame(columns = column_names)

if mode == 0:
    # compute at hours timescale from 1 day prior tmin to 1 day after tmax
    for i in range(tmin-86400, tmax+86400, 3600):
        generate(name, i, i+timebinsize, emax, queue, data)
if mode == 1:
    # compute at given timescale from tmin to tmax
    for i in range(tmin, tmax, timebinsize):
        generate(name, i, i+timebinsize, emax, queue, data)
if mode == 2:
    # compute integral from tmin to tmax
    generate(name, tmin, tmax, emax, queue, data)


