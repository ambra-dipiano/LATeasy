# *****************************************************************************
# Copyright (C) 2022 INAF
# This software is distributed under the terms of the BSD-3-Clause license
#
# This software is intended to install the library
# *****************************************************************************


import os
import setuptools

scriptsPath = "lateasy"
scripts = [scriptsPath+file for file in os.listdir(scriptsPath)]
for script in scripts:
     print(script)

setuptools.setup( 
     name='lateasy',
     author='Andrea Bulgarelli, Ambra Di Piano, Antonio Addis',
     package_dir={'lateasy': 'lateasy'},
     include_package_data=True,
     license='BSD-3-Clause',
)

