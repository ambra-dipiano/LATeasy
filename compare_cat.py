import xml.etree.ElementTree as ET
from astropy.io import fits
from astropy.coordinates import SkyCoord

model27 = '/data01/projects/IGRJ17354-3255/FERMI/FERMI_MODELS/4FGL27_IGR_inputmodel.xml'
cat27 = '/data01/projects/IGRJ17354-3255/FERMI/FERMI_DATA/gll_psc_v27.fit'
model22 = '/data01/projects/IGRJ17354-3255/FERMI/FERMI_MODELS/4FGL22_IGR_inputmodel.xml'
cat22 = '/data01/projects/IGRJ17354-3255/FERMI/FERMI_DATA/gll_psc_v22.fit'
catalogs = [cat22, cat27]
models = [model22, model27]

# target coordinates (TO-DO: check frame - negligible difference if iscr <--> fk5)
target = (263.854022, -32.938505)
center_J2000 = SkyCoord(ra=target[0], dec=target[1], frame='fk5', unit='deg')
# thresholds
radius = 1.5
bkgs = ('gll_iem_v07', 'iso_P8R3_SOURCE_V3_v1')
# list of parameters to check
models_params_name = ('ROI_Center_Distance', 'norm', 'Prefactor', 'Index', 'Index1', 'Index2', 'RA', 'DEC')
cat_params_name = ('Name', 'Assoc_Name', 'Detection_Significance', 'Energy_Flux', 'RA', 'DEC', 'Spectrum_Type', 'PL_Index', 'Detection_Significance')

for cat in catalogs:
    with fits.open(cat) as hdul:
        point_like = hdul[1].data
    positions = SkyCoord(ra=point_like['RAJ2000'], dec=point_like['DEJ2000'], frame='fk5', unit='degree')
    r = positions.separation(center_J2000).deg
    near_srcs = point_like[r <= radius]
    print(f'Surces in {cat} within', radius, ' deg :', len(near_srcs))

# find variable sources match between catalogue and source library
for model in models:
    src_lib = ET.parse(model)
    root = src_lib.getroot()
    nsources = 0
    near = 0
    for src in root.findall('source[@type="PointSource"]'):
        if float(src.attrib['ROI_Center_Distance']) <= radius:
            nsources += 1
    for src in root.findall('source[@type="DiffuseSource"]'):
        if src.attrib['name'] not in bkgs and float(src.attrib['ROI_Center_Distance']) <= radius:
            nsources += 1
    print(f'Surces in {model} within', radius, ' deg :', nsources)

def dict_from_model(model):
    sources = {}
    src_lib = ET.parse(model)
    root = src_lib.getroot()
    for src in root.findall('source[@type="PointSource"]'):
        if float(src.attrib['ROI_Center_Distance']) <= radius:
            sources[src.attrib['name']] = {}
            sources[src.attrib['name']]['ROI_Center_Distance'] = src.attrib['ROI_Center_Distance']
            for p in src.findall('spatialModel/parameter'):
                sources[src.attrib['name']][p.attrib['name']] = float(p.attrib['value'])*float(p.attrib['scale'])
            for p in src.findall('spectrum/parameter'):
                sources[src.attrib['name']][p.attrib['name']] = float(p.attrib['value'])*float(p.attrib['scale'])
    for src in root.findall('source[@type="DiffuseSource"]'):
        if src.attrib['name'] not in bkgs and float(src.attrib['ROI_Center_Distance']) <= radius:
            try:
                sources[src.attrib['name']]['name'] = src.attrib['name']
            except KeyError:
                continue
            sources[src.attrib['name']]['ROI_Center_Distance'] = src.attrib['ROI_Center_Distance']
            for p in src.findall('spatialModel/parameter'):
                sources[src.attrib['name']][p.attrib['name']] = float(p.attrib['value'])*float(p.attrib['scale'])
            for p in src.findall('spectrum/parameter'):
                sources[src.attrib['name']][p.attrib['name']] = float(p.attrib['value'])*float(p.attrib['scale'])
    return sources

# from model
s22 = dict_from_model(model22)
s27 = dict_from_model(model27)

# from catalog    
with fits.open(cat22) as hdul:
    point_like = hdul[1].data
positions = SkyCoord(ra=point_like['RAJ2000'], dec=point_like['DEJ2000'], frame='fk5', unit='degree')
r = positions.separation(center_J2000).deg
near22 = point_like[r <= radius]

with fits.open(cat27) as hdul:
    point_like = hdul[1].data
positions = SkyCoord(ra=point_like['RAJ2000'], dec=point_like['DEJ2000'], frame='fk5', unit='degree')
r = positions.separation(center_J2000).deg
near27 = point_like[r <= radius]

# new sources
print(f"\n4FGL NEW SOURCES\n{'-'*25}")
new_srcs = [s for s in s27.keys() if s not in s22.keys()]
print(f"{new_srcs}")

# diff sources
for s in s22.keys():
    print(f"\nNAME {s}\n{'-'*25}")
    for p in models_params_name:
        try:
            if s22[s][p] != s27[s][p]:
                print(f"{p.upper()} v22 = {s22[s][p]} | v27 = {s27[s][p]}")
        except KeyError:
            pass

agile = ['4FGL J1732.5−3131', '4FGL J1731.2−3234', '4FGL J1735.9-3342', '4FGL J1738.8-3241', '4FGL J1739.6-3155', '4FGL J1730.5-3352']

print(f"\n\nIN PAPER\n{'-'*25}\n", [s for s in near27['Source_Name'] if s in agile])

#print(near27.columns)

for n in agile:
    agile_src = near27[near27['Source_Name'] == n]
    print(f"\nNAME {n}\n{'-'*25}")
    print(agile_src['Flux1000'], agile_src['Energy_Flux100'])