#!/bin/sh
    # SLURM JOB SUBMISSION
    #
    #@ shell = /bin/bash
    #@ job_name = test
    #@ job_type = serial
    #@ environment= COPY_ALL
    #@ class    = large
    #@ resources = ConsumableCpus(1) ConsumableMemory(2000Mb)
    #@ error   = job.$(jobid).err
    #@ output  = job.$(jobid).out
    #@ queue

    exec sh $BASH_NAME$