#!/bin/sh
    # Please creare your own slurm template based on your configuration.
    # The pipeline only requires the keyword $BASH_NAME$ representing the execution bash script for the analysis.
    # The $BASH_NAME$ will be automatically generated and replaced based on the values specified by the user in the pipe.yml configuration file.
    #
    #@ shell = /bin/bash
    #@ job_name = test
    #@ job_type = serial
    #@ environment= COPY_ALL
    #@ class    = large
    # MORE THAN 1 CPU CAN BE REQUIRED
    #@ resources = ConsumableCpus(1) ConsumableMemory(2000Mb)
    #@ error   = job.$(jobid).err
    #@ output  = job.$(jobid).out
    #@ notify_user = user@email
    #@ queue

    exec sh $BASH_NAME$