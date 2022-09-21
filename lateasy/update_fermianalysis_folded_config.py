# *****************************************************************************
# Copyright (C) 2022 INAF
# This software is distributed under the terms of the BSD-3-Clause license
#
# This software is intended to update the fermipy configuration to run a  
# folded analysis 
# *****************************************************************************

import yaml
import sys
import os
import pandas as pd
import argparse

def load_data(filename):
    try:
        data = pd.read_csv(filename, sep=" ", header=0)
    except:
        raise ValueError(filename, 'is empty')
    return data

# ---------------------------------------------------------------------------- !

parser = argparse.ArgumentParser()
parser.add_argument('--infile', help='file YAML to read the configuration from', type=str, default='M13B_381196803_383788803.yaml')
parser.add_argument('--indir', help='folder in LC containin the infile', type=str, default='YEARS5j')
parser.add_argument('-N', '--nbins', help='number of time interval to pass to filter selection', default='all')
parser.add_argument('--outname', help='root name for output yaml and dir', type=str, default='TEST')
parser.add_argument('--filters', help='file in folded8 containing the good time intervals of the period', type=str, default='period1_kept.txt')
parser.add_argument('--test', help='by chosing test mode the new yaml configuration will use the reduced source model', type=bool, default=False)
parser.add_argument('--inpath', help='path hosting the "indir" variable', type=str, default='/data01/projects/IGRJ17354-3255/FERMI/LC/')
parser.add_argument('--outpath', help='path hosting the output dir', type=str, default='/data01/projects/IGRJ17354-3255/FERMI/LC/TEST/')
parser.add_argument('--folded', help='chose if folded analysis', type=str, default='False')
parser.add_argument('--skipsed', help='chose if folded analysis', type=str, default='True')
parser.add_argument('--skiplc', help='chose if folded analysis', type=str, default='True')
args = parser.parse_args()

#print(args)

# compose file path
filename = os.path.join(args.inpath, args.indir, args.infile)
timetable = os.path.join(args.outpath, 'periods', args.filters)
if not os.path.isfile(filename):
    raise ValueError('yaml file not found')
# load yaml
with open(filename) as f:
    config = yaml.load(f)

# folded  
if args.folded.capitalize() == 'True': 
    if not os.path.isfile(timetable):
        raise ValueError('times table not found') 
    # load times
    times = load_data(timetable)
    tstart = times['tstart']
    tstop = times['tstop']

    if args.nbins == 'all':
        args.nbins = int(len(times) - 1)
    else:
        args.nbins = int(args.nbins)
    # (START>=XX && STOP<=XX) || ... || (START>=XX && STOP<=XX) 
    filters = str(config['selection']['filter']).strip()
    filters += '&&'
    #filters += '('
    for i in range(args.nbins):
        filters += '(START>=' + str(tstart[i]).strip() + '&&STOP<=' + str(tstop[i]).strip() + ')'
        if i+1 == args.nbins:
            break
        else:
            filters += '||'
    #filters += ')'
    config['selection']['filter'] = "%s" %filters
    config['selection']['tmin'] = 239557417 #float(tstart[0])
    config['selection']['tmax'] = 620454098 #float(tstop[args.nbins])
    del config['selection']['tmax']
    del config['selection']['tmin']

# month
if args.test:
    config['model']['catalogs'] = ['/data01/projects/IGRJ17354-3255/FERMI/FERMI_MODELS/4FGL22_IGR_inputmodel.red.xml']

# output
config['fileio']['outdir'] = args.outname

# save new gonfig
new_filename = os.path.join(args.outpath, args.outname + '.yaml')
with open(new_filename, 'w+') as f:
    new_config = yaml.dump(config, f, default_flow_style=False)

# write bash
new_filename = os.path.join(args.outpath, args.outname + '.sh')
with open(new_filename, 'w+') as f:
    f. write('#!/bin/bash\n\n')
    f.write('source activate fermipy2')
    f.write('\n\texport FERMITOOLS=/data01/projects/IGRJ17354-3255/FERMI/code/IGRJ17354-3255/pycode/')
    f.write('\n\texport FERMIDATA=/data01/projects/IGRJ17354-3255/FERMI/FERMI_DATA/')
    f.write('\n\texport FERMI_DIFFUSE_DIR=$CONDA_PREFIX/share/fermitools/refdata/fermi/galdiffuse/')
    f.write('\n\tpython $FERMITOOLS/cmd5fix.py -f ' + args.outname + '.yaml --skiplc ' + args.skiplc + ' --skipsed ' + args.skipsed + '\n')

# write job
runjob = os.path.join(args.outpath, 'job_' + args.outname + '.sh')
with open(runjob, 'w+') as f:
    f.write('#!/bin/bash')
    f.write('\n\n#SBATCH --job-name=' + args.outname)
    f.write('\n#SBATCH --output=slurm-' + args.outname + '.out')
    f.write('\n#SBATCH --account=rt')
    f.write('\n#SBATCH --ntasks=1')
    f.write('\n#SBATCH --nodes=1')
    f.write('\n#SBATCH --cpus-per-task=1')
    f.write('\n\nexec sh ' + args.outname + '.sh\n')

