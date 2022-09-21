# *****************************************************************************
# Copyright (C) 2022 INAF
# This software is distributed under the terms of the BSD-3-Clause license
#
# This software is intended to generate the fermipy configuration and 
# other execution scripts to run the analysis
# *****************************************************************************


import sys
import os
import pandas as pd

def generate(name, tmin, tmax, emax, model, queue, data):
    s = f""" 
    data:
      evfile : /data01/projects/IGRJ17354-3255/FERMI/FERMI_DATA/events.txt
      scfile : /data01/projects/IGRJ17354-3255/FERMI/FERMI_DATA/SC00.fits

    binning:
      roiwidth   : 15.0
      binsz      : 0.1
      binsperdec : 8

    components:
    - selection:
        emin: 1000
        zmax: 105
    - selection:
        emax: 1000
        emin: 300
        evtype: 56
        zmax: 95
    - selection:
        emax: 300
        emin: 100
        evtype: 48
        zmax: 85

    selection :
      emin : 100
      emax : {emax}
      zmax    : 85
      evclass : 128
      evtype  : 3
      filter  : '(DATA_QUAL>0)&&(LAT_CONFIG==1)'
      ra  : 263.854022
      dec : -32.938505
      tmin    : {tmin}
      tmax    : {tmax}

    gtlike:
      edisp : True
      edisp_bins : -2
      irfs : 'P8R3_SOURCE_V2'
      edisp_disable : ['isodiff']

    model:
      galdiff  : '$CONDA_PREFIX/share/fermitools/refdata/fermi/galdiffuse/gll_iem_v07.fits'
      isodiff  : 'iso_P8R3_SOURCE_V2_v1.txt'
      catalogs : 
        - '{model}'

    fileio:
       outdir : {name}_{tmin}_{tmax}"""

    dname = name+"_"+str(tmin)+"_"+str(tmax)
    fname = name+"_"+str(tmin)+"_"+str(tmax)+".yaml"
    fname2 = name+"_"+str(tmin)+"_"+str(tmax)+".ll"
    fname3 = name+"_"+str(tmin)+"_"+str(tmax)+".sh"
    txt = open(fname, "w")
    txt.write(s)
    txt.close()
    
    iso_normalization_value = 1
    gll_prefactor_value =  1
    gll_index_value = 0

    if not data.empty:
        for index, row in data.iterrows():
            if tmin >= row["tmin"] and tmin <= row["tmax"]:
                iso_normalization_value = row["iso_P8R3_SOURCE_V2_v1_Normalization_value"]
                gll_prefactor_value =  row["gll_iem_v07_Prefactor_value"]
                gll_index_value = row["gll_iem_v07_Index_value"]

    #for loadleveler and container - prepare the script to run into the container
    s2 = f"""source activate fermipy2
    export FERMITOOLS=/data01/projects/IGRJ17354-3255/FERMI/code/IGRJ17354-3255/pycode/
    export FERMIDATA=/data01/projects/IGRJ17354-3255/FERMI/FERMI_DATA/
    export FERMI_DIFFUSE_DIR=$CONDA_PREFIX/share/fermitools/refdata/fermi/galdiffuse/
    python $FERMITOOLS/cmd6fermi.py -f {fname} --isofree False --galfree False --makelc 3 --binsize 86400 --skipsed True --iso_normalization {iso_normalization_value} --gal_prefactor {gll_prefactor_value} --gal_index {gll_index_value}
    cp {dname}.* {dname}
    cp cmd6fermi_{dname}.log {dname}
    cd {dname}
    python $FERMITOOLS/run_fermipy_sensitivity.py
    mv ltcube_00.fits ltcube_00.fits.tmp
    rm *.fits
    mv ltcube_00.fits.tmp ltcube_00.fits
    rm *.par
    cd .."""
    
    print(s2)
 
    sh = open(fname3, "w")
    sh.write(s2)
    sh.close()

    #for slurm and container
    #s3 = f"""#!/bin/sh

    #source activate fermi
    #python cmd3.py {fname}"""
    #sh = open(fname2, "w")
    #sh.write(s3)
    #sh.close()


    #for loadleveler without container
    s3 = f"""#!/bin/sh
    # SCRIPT DI SOTTOMISSIONE DI JOB SERIALI
    #

    #@ shell = /bin/bash
    #@ job_name = test
    #@ job_type = serial
    #@ environment= COPY_ALL
    #@ class    = large
    # E' POSSIBILE CHIEDERE PIU' DI UNA CPU
    #@ resources = ConsumableCpus(1) ConsumableMemory(2000Mb)
    #@ error   = job.$(jobid).err
    #@ output  = job.$(jobid).out
    #@ notify_user = bulgarelli@iasfbo.inaf.it
    #@ queue

    #singularity exec -B /data01:/data01 /data01/home_addis/fermi_withconda_layer1_core.simg sh /data01/home_addis/task_morgana/{fname3}
    exec sh {fname3}"""

    sh = open(fname2, "w")
    sh.write(s3)
    sh.close()

    os.system("sbatch --partition="+queue+" " + fname2)
    #os.system("llsubmit " + fname2)

if __name__ == "__main__":
    name = sys.argv[1]
    tmin = int(sys.argv[2])
    tmax = int(sys.argv[3])
    mode = int(sys.argv[4])
    timebinsize = int(sys.argv[5])
    emax = int(sys.argv[6])
    model = sys.argv[7] #/data01/projects/IGRJ17354-3255/FERMI/FERMI_MODELS/4FGL21_IGR_inputmodel.xml
    queue = sys.argv[8]

    #file with result to extract isomodel and galmodel parameters
    if len(sys.argv) == 10:
        result_txt = sys.argv[9]
        data = pd.read_csv(result_txt, header=0, sep=" ")
    else:
        column_names = ["a", "b", "c"]
        data = pd.DataFrame(columns = column_names)

    if mode == 0:
       for i in range(tmin-86400, tmax+86400, 3600):
          generate(name, i, i+timebinsize, emax, model, queue, data)
    if mode == 1:
       for i in range(tmin, tmax, timebinsize):
          generate(name, i, i+timebinsize, emax, model, queue, data)
    if mode == 2:
       generate(name, tmin, tmax, emax, model, queue, data)


