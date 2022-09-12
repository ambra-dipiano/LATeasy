# *****************************************************************************
# Copyright (C) 2022 INAF
# This software is distributed under the terms of the BSD-3-Clause license
#
# This software contains an ensable of utility functions
# *****************************************************************************

def mjd_to_met(time):
    """Convert mean julian date to mission elapse time."""
    correction = 0.0006962818548948615
    return (86400. + correction) * (time - 51910) 

def met_to_mjd(time):
    """Convert mean julian date to mission elapse time."""
    correction = 0.0006962818548948615
    return time / (86400. + correction) + 51910