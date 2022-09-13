# *****************************************************************************
# Copyright (C) 2022 INAF
# This software is distributed under the terms of the BSD-3-Clause license
#
# This software is intended to run the fermi flux sensitivity
# *****************************************************************************

from astropy.table import Table
import os

#os.system("export FERMI_DIFFUSE_DIR=/opt/anaconda3/envs/fermi/share/fermitools/refdata/fermi/galdiffuse/")

os.system("fermipy-flux-sensitivity --output=lat_sensitivity4.fits --ltcube=ltcube_00.fits --event_class=P8R3_SOURCE_V2  --glon=335.447 --glat=-0.2689 --map_type=wcs --wcs_npix=100 --wcs_cdelt=0.5 --wcs_proj=AIT --emin=100 --emax=10000 --galdiff=/opt/anaconda3/envs/fermi/share/fermitools/refdata/fermi/galdiffuse/gll_iem_v07.fits --min_counts=10.0 --ts_thresh=4")

tab = Table.read('lat_sensitivity4.fits','INT_FLUX')
sens_225=tab['flux'][5]
sens_250=tab['flux'][6]
sens_275=tab['flux'][7]
sh=open("sens2all.txt", "w")
sh.write("2.0 2.25 %.2e\n"%sens_225)
sh.write("2.0 2.50 %.2e\n"%sens_250)
sh.write("2.0 2.75 %.2e\n"%sens_275)
sh.close()
sh=open("sens2.txt", "w")
sh.write("%.2e\n"%sens_250)
sh.close()


os.system("fermipy-flux-sensitivity --output=lat_sensitivity9.fits --ltcube=ltcube_00.fits --event_class=P8R3_SOURCE_V2  --glon=335.447 --glat=-0.2689 --map_type=wcs --wcs_npix=100 --wcs_cdelt=0.5 --wcs_proj=AIT --emin=100 --emax=10000 --galdiff=/opt/anaconda3/envs/fermi/share/fermitools/refdata/fermi/galdiffuse/gll_iem_v07.fits --min_counts=10.0 --ts_thresh=9")

tab = Table.read('lat_sensitivity9.fits','INT_FLUX')
sens_225=tab['flux'][5]
sens_250=tab['flux'][6]
sens_275=tab['flux'][7]
sh=open("sens3all.txt", "w")
sh.write("3.0 2.25 %.2e\n"%sens_225)
sh.write("3.0 2.50 %.2e\n"%sens_250)
sh.write("3.0 2.75 %.2e\n"%sens_275)
sh.close()
sh=open("sens3.txt", "w")
sh.write("%.2e\n"%sens_250)
sh.close()

os.system("fermipy-flux-sensitivity --output=lat_sensitivity125.fits --ltcube=ltcube_00.fits --event_class=P8R3_SOURCE_V2  --glon=335.447 --glat=-0.2689 --map_type=wcs --wcs_npix=100 --wcs_cdelt=0.5 --wcs_proj=AIT --emin=100 --emax=10000 --galdiff=/opt/anaconda3/envs/fermi/share/fermitools/refdata/fermi/galdiffuse/gll_iem_v07.fits --min_counts=10.0 --ts_thresh=12.5")

tab = Table.read('lat_sensitivity125.fits','INT_FLUX')
sens_225=tab['flux'][5]
sens_250=tab['flux'][6]
sens_275=tab['flux'][7]
sh=open("sens35all.txt", "w")
sh.write("3.5 2.25 %.2e\n"%sens_225)
sh.write("3.5 2.50 %.2e\n"%sens_250)
sh.write("3.5 2.75 %.2e\n"%sens_275)
sh.close()
sh=open("sens35.txt", "w")
sh.write("%.2e\n"%sens_250)
sh.close()

os.system("fermipy-flux-sensitivity --output=lat_sensitivity16.fits --ltcube=ltcube_00.fits --event_class=P8R3_SOURCE_V2  --glon=335.447 --glat=-0.2689 --map_type=wcs --wcs_npix=100 --wcs_cdelt=0.5 --wcs_proj=AIT --emin=100 --emax=10000 --galdiff=/opt/anaconda3/envs/fermi/share/fermitools/refdata/fermi/galdiffuse/gll_iem_v07.fits --min_counts=10.0 --ts_thresh=16")

tab = Table.read('lat_sensitivity16.fits','INT_FLUX')
sens_225=tab['flux'][5]
sens_250=tab['flux'][6]
sens_275=tab['flux'][7]
sh=open("sens4all.txt", "w")
sh.write("4.0 2.25 %.2e\n"%sens_225)
sh.write("4.0 2.50 %.2e\n"%sens_250)
sh.write("4.0 2.75 %.2e\n"%sens_275)
sh.close()
sh=open("sens4.txt", "w")
sh.write("%.2e\n"%sens_250)
sh.close()

os.system("fermipy-flux-sensitivity --output=lat_sensitivity25.fits --ltcube=ltcube_00.fits --event_class=P8R3_SOURCE_V2  --glon=335.447 --glat=-0.2689 --map_type=wcs --wcs_npix=100 --wcs_cdelt=0.5 --wcs_proj=AIT --emin=100 --emax=10000 --galdiff=/opt/anaconda3/envs/fermi/share/fermitools/refdata/fermi/galdiffuse/gll_iem_v07.fits --min_counts=10.0 --ts_thresh=25.0")

tab = Table.read('lat_sensitivity25.fits','INT_FLUX')
sens_225=tab['flux'][5]
sens_250=tab['flux'][6]
sens_275=tab['flux'][7]
sh=open("sens5all.txt", "w")
sh.write("5.0 2.25 %.2e\n"%sens_225)
sh.write("5.0 2.50 %.2e\n"%sens_250)
sh.write("5.0 2.75 %.2e\n"%sens_275)
sh.close()
sh=open("sens5.txt", "w")
sh.write("%.2e\n"%sens_250)
sh.close()

