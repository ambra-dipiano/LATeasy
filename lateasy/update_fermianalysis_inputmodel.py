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
from lateasy.utils.functions import set_logger, get_target_coords

parser = argparse.ArgumentParser(description='Fermi/LAT data analysis pipeline')
parser.add_argument('--pipeconf',  type=str, required=True, help='configuration file')
args = parser.parse_args()

# load yaml configurations
with open(args.pipeconf) as f:
    pipeconf = yaml.safe_load(f)

# logging
logname = join(pipeconf['path']['output'], str(__file__).replace('.py','.log'))
log = set_logger(filename=logname, level=pipeconf['execute']['loglevel'])

# file shortcuts
model = join(pipeconf['path']['models'], pipeconf['file']['inputmodel'])
igrmodel = join(pipeconf['path']['models'], pipeconf['file']['target'])
cat = join(pipeconf['path']['data'], pipeconf['file']['catalogue'])

# target coordinates 
target = get_target_coords(igrmodel, pipeconf['target']['name'])
log.info('Target Coordinates: (RA, DEC) = (' + str(target[0]) + ', ' + str(target[1]) + ') deg' )
center_J2000 = SkyCoord(ra=target[0], dec=target[1], frame='fk5', unit='deg')

# thresholds
radius = pipeconf['updatemodel']['radius'] 
log.info('Internal radius within sources are freed: ' + str(radius) + ' deg')
min_ts = pipeconf['updatemodel']['mints']  
log.info('Minimum TS to free sources within internal radius: ' + str(min_ts))
radius_external = pipeconf['updatemodel']['extradius'] 
log.info('External radius within which sources are fixed except for bright and variable sources: ' + str(radius_external) + ' deg')
min_ts_external = pipeconf['updatemodel']['extmints']  
log.info('Minimum TS to free sources within external radius: ' + str(min_ts))
variability_threshold = pipeconf['updatemodel']['minvariability'] 
log.info('Variability index above which sources have < 0.01 chance of being steady')

# background sources in library
bkgs = pipeconf['updatemodel']['newbkg']
# list of parameters to free
params_name = pipeconf['updatemodel']['freeparams']
for p in params_name:
    log.info('Free ' + p)

# load data from catalogue (point-like and extended)
with fits.open(cat) as hdul:
    point_like = hdul[1].data

# find sources within radius and external radius in catalogue 
positions = SkyCoord(ra=point_like['RAJ2000'], dec=point_like['DEJ2000'], frame='fk5', unit='degree')
r = positions.separation(center_J2000).deg
near_srcs = point_like[r <= radius]
log.info('Surces within ' + str(radius) + ' deg:' + str(len(near_srcs)))
external_srcs = point_like[r <= radius_external]
log.info('Surces within ' + str(radius_external) + ' deg: ' + str(len(external_srcs)))

# variable srcs and their names < radius_external and TS > 50
variable_srcs = point_like[point_like['Variability_Index'] >= variability_threshold]
variable_external_srcs = external_srcs[external_srcs['Variability_Index'] >= variability_threshold]
variable_external_bright = variable_external_srcs[variable_external_srcs['Signif_Avg'] >= min_ts_external]
variable_external_bright_name = variable_external_bright['Source_Name']
log.info('Variable within ' + str(radius_external) + 'deg and TS >' + str(min_ts_external) + ': ' + str(len(variable_external_bright_name)))
for name in variable_external_bright_name:
    log.info('Source name:' + name)

# save variable srcs < radius_external and TS > min_ts_external
srcs_variable = {'Source_Name': [], 'ROI_Center_Distance': [], 'Signif_Avg': []}
for src in variable_external_bright:
    srcs_variable['Source_Name'].append(src['Source_Name'])
    srcs_variable['Signif_Avg'].append(src['Signif_Avg'])

# find variable sources match between catalogue and source library and set them free 
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
if iso is not None:
    iso.set('name', pipeconf['background']['isomodel'])
    spc = iso.find('spectrum')
    spc.set('file', join(pipeconf['path']['galdir'], pipeconf['background']['isomodel']) + '.txt')
    log.warning('Change isomodel with: ' + pipeconf['background']['isomodel'])

# update source library and append mysource model
if root.find('source[@name="' + pipeconf['target']['name'] + '"]') == None:
    try:
        root.insert(0, mysource)
        log.info('Add target model')
    except Exception as e:
        log.error(e)
        raise FileNotFoundError(e)
else:
    log.info('Target model already in sky region model')

# write update model
with open(model, 'wb') as f:
    src_lib.write(model)
log.info('Freed all sources within ' + str(radius) + ' deg')
log.info('Freed variable srcs with TS > ' + str(min_ts_external) + 'within ' +  str(radius_external) + ' deg')
log.info('Total freed sources ' + str(nsources))

# remove withe lines
with open(model) as f:
    lines = [line for line in f if line.strip() is not ""]
with open(model, "w") as f:
    f.writelines(lines)

bkgs = (pipeconf['background']['isomodel'], pipeconf['background']['galmodel'])

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

print('Extended sourceswithin ' + str(radius) + ' deg')
for src in srcs_extended['Extended_Source_Name']:
    log.info('Extended: ' + src)
log.info("Total degrees of freedom:" + str(dof))
