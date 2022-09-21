# *****************************************************************************
# Copyright (C) 2022 INAF
# This software is distributed under the terms of the BSD-3-Clause license
#
# This software is intended to install the library
# *****************************************************************************


import os
import setuptools

with open("requirements.lock", "r", encoding="utf-8") as fh:
   requirements = [] #[d.strip() for d in fh.readlines() if "#" not in d]

scriptsPath = "."
scripts = [scriptsPath+file for file in os.listdir(scriptsPath)]
for script in scripts:
     print(script)

setuptools.setup( 
     name='sagsci',
     author='Andrea Bulgarelli, Nicolo Parmiggiani, Leonardo Baroncelli, Ambra Di Piano, Valentina Fioretti, Antonio Addis, Giovanni De Cesare, Gabriele Panebianco',
     author_email='andrea.bulgarelli@inaf.it, nicolo.parmiggiani@inaf.it, leonardo.baroncelli@inaf.it, ambra.dipiano@inaf.it, valentina.fioretti@inaf.it, antonio.addis@inaf.it, giovanni.decesare@inaf.it, gabriele.panebianco3@unibo.it',
     package_dir={'sagsci': 'sagsci'},
     scripts=scripts,
     include_package_data=True,
     license='BSD-3-Clause',
     python_requires=">=3.6.9",
     install_requirements=[
          requirements
     ]
)

