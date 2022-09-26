# *****************************************************************************
# Copyright (C) 2022 INAF
# This software is distributed under the terms of the BSD-3-Clause license
#
# This software contains an ensable of utility functions
# *****************************************************************************

import logging
import pandas as pd
import xml.etree.ElementTree as ET

def mjd_to_met(time):
    """Convert mean julian date to mission elapse time."""
    correction = 0.0006962818548948615
    return (86400. + correction) * (time - 51910) 

def met_to_mjd(time):
    """Convert mean julian date to mission elapse time."""
    correction = 0.0006962818548948615
    return time / (86400. + correction) + 51910

def get_target_coords(model, name):
    mysource = ET.parse(model).getroot().find('source[@name="' + name + '"]')
    ra = float(mysource.find('spatialModel/parameter[@name="RA"]').attrib['value'])
    dec = float(mysource.find('spatialModel/parameter[@name="DEC"]').attrib['value'])
    return ra, dec

def set_logger(filename, level):
    log = logging.getLogger()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fileHandler = logging.FileHandler(filename)
    fileHandler.setFormatter(formatter)
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(formatter)
    log.addHandler(fileHandler)
    log.addHandler(consoleHandler)
    log.setLevel(level)
    return log

def load_data(filename):
    try:
        data = pd.read_csv(filename, sep=" ", header=0)
    except:
        raise ValueError(filename, 'is empty')
    return data