# *****************************************************************************
# Copyright (C) 2022 INAF
# This software is distributed under the terms of the BSD-3-Clause license
#
# This software contains an ensable of utility functions
# *****************************************************************************

import logging
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
    ra = mysource.find('spatialModel/parameter[@name=RA]').get('value')
    dec = mysource.find('spatialModel/parameter[@name=DEC]').get('value')
    return ra, dec

def set_logger(filename, level):
    log = logging.getLogger()
    fileHandler = logging.FileHandler(filename)
    log.addHandler(fileHandler)
    consoleHandler = logging.StreamHandler()
    log.addHandler(consoleHandler)
    log.setLevel(level)
    return log