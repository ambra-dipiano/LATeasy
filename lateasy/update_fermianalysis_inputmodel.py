# *****************************************************************************
# Copyright (C) 2022 INAF
# This software is distributed under the terms of the BSD-3-Clause license
#
# This software is intended to update the input model of the sky region
# *****************************************************************************

import argparse
import yaml
import xml.etree.ElementTree as ET
from astropy.io import fits
from astropy.coordinates import SkyCoord
from os.path import join

parser = argparse.ArgumentParser(description='Fermi/LAT data analysis pipeline')
parser.add_argument('--pipeconf',  type=str, required=True, help='configuration file')
args = parser.parse_args()

# load yaml configurations
with open(args.pipeconf) as f:
    pipeconf = yaml.load(f)
model = join(pipeconf['path']['models'], pipeconf['file']['inputmodel'])
igrmodel = join(pipeconf['path']['models'], pipeconf['file']['target'])
cat = join(pipeconf['path']['data'], pipeconf['file']['catalogue'])

# target coordinates (TO-DO: check frame - negligible difference if iscr <--> fk5)
target = (263.854022, -32.938505)
center_J2000 = SkyCoord(ra=target[0], dec=target[1], frame='fk5', unit='deg')
# thresholds
radius = pipeconf['updatemodel']['radius']  # radius within which all sources are kept free
radius_external = pipeconf['updatemodel']['extradius']  # radius within which all sources are fixed except for variable ones
min_ts = pipeconf['updatemodel']['mints']  # minimum TS srcs < radius to free norm
min_ts_external = pipeconf['updatemodel']['extmints']  # minimum TS srcs < radius_external to free norm
# min_ts_flag = 10  # minimum TS flagged srcs < radius to free norm (10-16)
variability_threshold = pipeconf['updatemodel']['minvariability']  # variability index above which sources have < 1% chance of being steady
# background sources in library
bkgs = pipeconf['updatemodel']['newbkg']
# list of parameters to free
params_name = pipeconf['updatemodel']['freeparams']

# load data from catalogue (point-like and extended)
with fits.open(cat) as hdul:
    point_like = hdul[1].data
    #print(point_like.columns)

# find sources within radius and external radius in catalogue 
positions = SkyCoord(ra=point_like['RAJ2000'], dec=point_like['DEJ2000'], frame='fk5', unit='degree')
r = positions.separation(center_J2000).deg
near_srcs = point_like[r <= radius]
#print('Surces within', radius, ' deg :', len(near_srcs))
external_srcs = point_like[r <= radius_external]
#print('Surces within', radius_external, 'deg :', len(external_srcs))

# find variable sources in catalogue and their source names
variable_srcs = point_like[point_like['Variability_Index'] >= variability_threshold]
# variable srcs and their names < radius_external and TS > 50
variable_external_srcs = external_srcs[external_srcs['Variability_Index'] >= variability_threshold]
variable_external_bright = variable_external_srcs[variable_external_srcs['Signif_Avg'] >= min_ts_external]
variable_external_bright_name = variable_external_bright['Source_Name']
print('Variable d <', radius_external, 'deg and TS >', min_ts_external, ':', len(variable_external_bright_name))

# flagged srcs and their names < radius and TS > min_ts_flag
# near_flag = near_srcs[near_srcs['Flags'] != 0]
# free_flag_name = near_flag[near_flag['Signif_Avg'] > min_ts_flag]['Source_Name']
# print('Flagged d <', radius, 'deg and TS >', min_ts_flag, ':', len(free_flag_name))

# save variable srcs < radius_external and TS > min_ts_external
srcs_variable = {'Source_Name': [], 'ROI_Center_Distance': [], 'Signif_Avg': []}
for src in variable_external_bright:
    srcs_variable['Source_Name'].append(src['Source_Name'])
    srcs_variable['Signif_Avg'].append(src['Signif_Avg'])

# find variable sources match between catalogue and source library and set them free (only norm parameter)
with open(igrmodel, 'rb') as f:
    mysource = ET.parse(f).getroot().find('source[@name="IGRJ17354-3255"]')
with open(model, 'rb') as f:
    src_lib = ET.parse(model)
root = src_lib.getroot()
nsources, near, freed, dof = 0, 0, 0, 0
for src in root.findall('source[@type="PointSource"]'):
    if float(src.attrib['ROI_Center_Distance']) <= radius or src.attrib['name'] in variable_external_bright_name:
        nsources += 1
        # if bright variable than save the distance from roi center
        if src.attrib['name'] in variable_external_bright_name:
            srcs_variable['ROI_Center_Distance'].append(float(src.attrib['ROI_Center_Distance']))
        else:
            near += 1
        # if near or bright variable then free norm and index
        if near_srcs[near_srcs['Source_Name'] == src.attrib['name']]['Signif_Avg'] >= min_ts:
            freed += 1
            for prm in src.findall('spectrum/parameter'):
                if prm.attrib['name'] in params_name:
                    #print(prm.attrib['name'])
                    prm.set('free', '1')
                    dof += 1

# change iso from V3 to V2
iso = root.find('source[@name="iso_P8R3_SOURCE_V3_v1"]')
iso.set('name', 'iso_P8R3_SOURCE_V2_v1')
spc = iso.find('spectrum')
spc.set('file', '$(FERMI_DIR)/refdata/fermi/galdiffuse/iso_P8R3_SOURCE_V2_v1.txt')

# update source library and append mysource model
root.insert(0, mysource)
with open(model, 'wb') as f:
    src_lib.write(model)
print('Freed all sources within', radius, 'deg')
print('Freed variable srcs with TS >', min_ts_external, 'within', radius_external, 'deg')
print('Total freed sources', nsources, 'with parameters:', params_name)
# remove withe lines
with open(model) as f:
    lines = [line for line in f if line.strip() is not ""]
with open(model, "w") as f:
    f.writelines(lines)

bkgs = ('gll_iem_v07', 'iso_P8R3_SOURCE_V2_v1')

# extended srcs < radius
srcs_extended = {'Source_Name'  : [], 'Extended_Source_Name': [], 'ROI_Center_Distance': [], 'Signif_Avg': [], 'Normalisation': [], 'Normalisation_Error': []}
for src in root.findall('source[@type="DiffuseSource"]'):
    if src.attrib['name'] not in bkgs:
        if float(src.attrib['ROI_Center_Distance']) < radius:
            srcs_extended['Extended_Source_Name'].append(src.attrib['name'])
            srcs_extended['ROI_Center_Distance'].append(float(src.attrib['ROI_Center_Distance']))
            for prm in src.findall('spectrum/parameter'):
                if prm.attrib['name'] in params_name:
                    srcs_extended['Normalisation'].append(float(prm.attrib['value']))
                    srcs_extended['Normalisation_Error'].append(float('nan'))        

for src in srcs_extended['Extended_Source_Name']:
    srcs_extended['Source_Name'].append(point_like[point_like['Extended_Source_Name'] == src]['Source_Name'][0])
    srcs_extended['Signif_Avg'].append(float(point_like[point_like['Extended_Source_Name'] == src]['Signif_avg'][0]))

# print dictionaries
print('Bright Variable (within', radius_external, 'deg) dict:', srcs_variable)
print('Extended (within ', radius,' deg) dict:', srcs_extended)
print("Near srcs:", near)
print("Freed srcs:", freed)
print("DOF:", dof)
