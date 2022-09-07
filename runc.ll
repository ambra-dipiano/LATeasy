#!/bin/bash
#
# Script per sottomettere un job con root

#@ shell = /bin/bash
#@ job_type = serial
#@ environment= COPY_ALL
#@ wall_clock_limit = 240:00:00
#RISORSE PER OGNI TASK
#@ resources = ConsumableCpus(1) 
#ConsumableMemory(5000Mb)
##@ node = 1
##@ tasks_per_node = 1
# in alternativa a task_per_node
##@ total_tasks = 4
#@ error   = job1.$(jobid).err
#@ output  = job1.$(jobid).out
#@ class    = large
#SBATCH --partition=large
#SBATCH --job-name=FERMI_LC
#@ queue
#SBATCH --share

source activate fermi
date
hostname


ruby /data01/projects/IGRJ17354-3255/FERMI/code/IGRJ17354-3255/FermiTools//fermi.rb run=SUM datalist=/data01/projects/IGRJ17354-3255/FERMI/FERMI_DATA//events.txt scfile=/data01/projects/IGRJ17354-3255/FERMI/FERMI_DATA//L20083004141749F5D3C158_SC00.fits srcmodel=/data01/projects/IGRJ17354-3255/FERMI/FERMI_MODELS/4FGL_IGR_inputmodel_updated.xml events_gti=binned_gti.list ltcube=SUM_binned_ltcube.fits emax=10000 ra=263.85402 dec=-32.938505
