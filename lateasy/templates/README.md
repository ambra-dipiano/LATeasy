# Configuration files

Specifics on the configuration files.

## Fermi analysis configuration

Please, refer to the [fermipy documentation](https://fermipy.readthedocs.io/en/latest/). We provide a [template](./template_fermianalysis.yml) that you can fill out to your needs.

## Pipeline configuration

The configuration file is structure in different tags. The following list provides a complete description of all parameters, which can also be found commented in the template file. We suggest to make a copy of the [template](./template_pipe.yml) provided and fill out all section required by your specific use case.

In the following we present a description of the parameters pertainin to each section of the configuration file.

### Section: <code>path</code>

The tag <code>path</code> of the configuration file, collects all absolute paths poiting to directories required by the analysis. It is important that you provide absolute path, without relative pointers or environmental variable to avoid ambiguity. This section is always required to be compiled.

| keyword        | type | description                            |
|----------------|------|----------------------------------------|
| data           | str  | folder where data is stored            |   
| models         | str  | folder where models are stored         |
| galdir         | str  | folder where the galactic diffuse background is stored |
| output         | str  | folder where to store output           |

In exemple:

```yaml
path:
  data: /data01/homes/dipiano/FermiTools/lateasy/crab/data            
  models: /data01/homes/dipiano/FermiTools/lateasy/crab/models
  galdir: /opt/anaconda3/envs/fermi/share/fermitools/refdata/fermi/galdiffuse/
  output: /data01/homes/dipiano/FermiTools/lateasy/crab/output
```

### Section: <code>file</code>

The tag <code>file</code> of the configuration file, collects all file names which will be used during the analysis. Beware that here you should only fill the file name, without path, and you should make sure that the file is placed in the correct folder which is indicated by the following description. This section is always required to be compiled.

| keyword        | type | description                            |
|----------------|------|----------------------------------------|
| target         | str  | name of the target source model, it must be place in "models" from the previous section |
| photometry     | str  | name of file contaning the AP exposure, it must be place in <code>data</code> from the previous section |
| catalogue      | str  | name of catalogue FITS file, it must be place in <code>data</code> from the previous section |
| observation    | str  | name of events file to create the sky region model, it must be place in <code>data</code> from the previous section |
| inputmodel     | str  | name of the sky region model to generate and use for analysis, it will be place (or must be if existing) in "models" from the previous section |
| folded8        | str  | name of folded time intervals data file, if needed it must be placed in <code>data</code> from the previous section |

The photometry  file must be a txt file with the following columns

```
start_met stop_met exposure counts
```

In exemple:

```yaml
file: 
  observation: L220930045127B298B5DA45_PH00.fits
  target: crab.xml
  inputmodel: 4FGL_inputmodel.xml
  catalogue: gll_psc_v27.fit
  photometry: 
  folded8: 
```

### Section: <code>background</code>

The tag <code>background</code> of the configuration file, collects all initial will contain all initial background hypothesis, including the model which [make4FGLxml.py](https://fermi.gsfc.nasa.gov/ssc/data/analysis/user/make4FGLxml.py) selects as default choices. If you want to use a different version, you should refer to the <code>updatemodel</code> section below. If unsure, leave the values empty and provide only the models name. Beware that the specified model must be locally existing in your <code>galdir</code> folder from the <code>path</code> section of the configuration file. This section is always required to be compiled.

| keyword        | type | description                            |
|----------------|------|----------------------------------------|
| isomodel       | str  | name of the isothropic background model, it must be placed in  <code>galdir</code> from the previous section |
| isofree        | bool | free isothropic background during analysis |
| isonorm        | float | normalisation value of the isothropic background model, if null takes default |
| galmodel       | str  | name of the galactic background model, it must be placed in  <code>galdir</code> from the previous section |
| galfree        | bool | free galactic background model during analysis |
| galnorm        | float | normalisazione value of the galactic background model, if null takes default |
| galindex       | float | index value of the galactic background model, if null takes default |

In exemple:

```yaml
background:
  isomodel: iso_P8R3_SOURCE_V2_v1
  isofree: true
  isonorm: 1
  galmodel: gll_iem_v07
  galfree: true
  galnorm: 1 
  galindex: 0
```

### Section: <code>target</code>

The tag <code>target</code> of the configuration file, collects all parameters relevant to the target itself. Beware that the model information will not be duplicated in this section, but should provided in a proper XML file containing both spectral and spatial models of the source. This section is always required to be compiled.

| keyword        | type | description                            |
|----------------|------|----------------------------------------|
| name           | str  | name of the target source              |
| 4FGLname       | str  | name of the target source in 4FGL cat, if missing or equal to the "name" then please duplicate the value here |

In exemple:

```yaml
target:
  name: Crab
  4FGLname: 4FGL J0534.5+2200
```

or 

```yaml
target:
  name: IGRJ17354-3255
  4FGLname: IGRJ17354-3255
```

### Section: <code>variable_sources</code>

The tag <code>variable_sources</code> of the configuration file, should be compiled using the 4FGL name of all variabls sources that you want to check during the analysis as children tags. You must substitute the <code><SOURCE_NAME></code> tag with the source catalogue name. You can add as many as you need, so long as you replicate the same format. For each children tag you will need the following parameters. During the analysis these parameters will be use to check the parameters fit update. If not required, please put the <code>variable_sources</code> tag to <code>NULL</code>

| keyword        | type | description                            |
|----------------|------|----------------------------------------|
| ROI_Center_Distance | float | distance from the sky region center in degrees |
| Signif_Avg          | float | significance reported in the catalogue |

In exemple:

```yaml
variable_sources: null
```

or

```yaml
variable_sources:
  4FGL J1802.6-3940:
    ROI_Center_Distance: 8.682
    Signif_Avg: 65.025505
```

### Section: <code>extended_sources</code>

The tag <code>extended_sources</code> of the configuration file, should be compiled using the 4FGL name of all extended sources that you want to check during the analysis as children tags. You must substitute the <code><SOURCE_NAME></code> tag with the source catalogue name. You can add as many as you need, so long as you replicate the same format. For each children tag you will need the following parameters. During the analysis these parameters will be use to check the parameters fit update. If not required, please put the <code>variable_sources</code> tag to <code>NULL</code>

| keyword        | type | description                            |
|----------------|------|----------------------------------------|
| ROI_Center_Distance | float | distance from the sky region center in degrees |
| Signif_Avg          | float | significance reported in the catalogue |
| Normalisation       | list  | normalisation values of the source model |
| Normalisation_Error | list  | normalisation errors of the source model |

In exemple:

```yaml
extended_sources: null
```

or

```yaml
extended_sources:
  FGES J1745.8-3028:
    ROI_Center_Distance: 3.31
    Signif_Avg: 29.66
    Normalisation: 
      - 9.332740743411838
      - 2.2291994
    Normalisation_Error: 
      - null
      - null
```

### Section: <code>execute</code>

The tag <code>execute</code> of the configuration file, collects all execution option of the analysis. This section must always be compiled for the analysis script and the jobs generation scripts.

| keyword        | type  | description                            |
|----------------|-------|----------------------------------------|
| lc             | bool  | perform lightcurve                     |
| sed            | bool  | perform sed                            |
| localise       | bool  | perform localisation                   |
| agg_backend    | bool  | change matplotlib backent to <code>agg</code> |
| verbose        | int   | value of fermipy verbosity             |
| loglevel       | int   | level of pipeline logging; options are <code>0=none</code>, <code>10=debug</code>, <code>20=info</code>, <code>30=warning</code>, <code>40=error</code>, <code>50=critical</code> |

In exemple:

```yaml
execute:
  lc: true
  sed: true
  localise: true
  agg_backend: true
  verbose: 1
  loglevel: 10
```

### Section: <code>lightcurve</code>

The tag <code>lightcurve</code> of the configuration file, collects all lightcurve parameters of the analysis. This section must always be compiled for the analysis script and the jobs generation scripts. The parameter of this section are directly forwarded to the configuration of fermipy and describe how the fermipy lightcurve will be executed.

| keyword        | type  | description                            |
|----------------|-------|----------------------------------------|
| bintype        | str   | how to define time bins; options: <code>fix</code>, <code>filter</code>, <code>integral</code> |
| binsize        | int   | lightcurve binsize in seconds when <code>bintype=fix</code> |

In exemple:

```yaml
lightcurve:
  bintype: fix
  binsize: 86400
```

### Section: <code>makemodel</code>

The tag <code>makemodel</code> of the configuration file, collects all options to run the [make4FGLxml.py](https://fermi.gsfc.nasa.gov/ssc/data/analysis/user/make4FGLxml.py) script. Please refer to its [readme](https://fermi.gsfc.nasa.gov/ssc/data/analysis/user/readme_make4FGLxml.txt) for further information. This section must be compiled only to generate the sky region model.

| keyword        | type  | description                            |
|----------------|-------|----------------------------------------|
| normfree       | bool  | free normalisation                     |
| radius         | float | inner radius for freeing normalisation |
| significance   | float | minimum significance for freeing normalisation |
| ds9reg         | bool  | make ds9 region file                   |

In exemple:

```yaml
makemodel:
  normfree: yes 
  radius: 5
  significance: 25 
  ds9reg: True
```

### Section: <code>updatemodel</code>

The tag <code>updatemodel</code> of the configuration file, collects the parameters necessary to update and modify the sky region model as generated by the [make4FGLxml.py](https://fermi.gsfc.nasa.gov/ssc/data/analysis/user/make4FGLxml.py) script. This section must be completed only to run the model update script. If you want to use a different version of the background with respect to the default of the [make4FGLxml.py](https://fermi.gsfc.nasa.gov/ssc/data/analysis/user/make4FGLxml.py) you should specify which in this section.

| keyword        | type  | description                            |
|----------------|-------|----------------------------------------|
| radius         | float | inner radius within sources are freed  |
| extradius      | float | outer radius within sources are freed  |
| mints          | int   | min ts to free sources within <code>radius</code> |
| extmints       | int   | min ts to free sources withint <code>extradius</code> |
| minvariability | float | min variability threshold              |
| freeparams     | list  | parameters to free                     |
| newbkg         | list  | backgrounds to substitute in the model |

In exemple:

```yaml
updatemodel:
  radius: 5
  extradius: 10
  mints: 25
  extmints: 50
  minvariability: 18.48
  freeparams:
    - norm
    - Prefactor
  newbkg:
    - gll_iem_v07
    - iso_P8R3_SOURCE_V3_v1
```

### Section: <code>slurm</code>

The tag <code>slurm</code> of the configuration file, collects all slurm parallelisation parameters. This section is required to be completed only if the analysis are submitted to slurm for execution.

| keyword        | type  | description                            |
|----------------|-------|----------------------------------------|
| envname        | str   | virtual environment to activate        |
| template       | str   | absolute path to slurm job submission template |
| bkgresults     | str   | absolute path to LC results file from which to extract the updated background parameter or basename of the file if placed into the <code>output</code> folder of the <code>path</code> section; if null takes default values from <code>background</code> section |
| name           | str   | rootname of the analysis job         |
| tmin           | int   | start time of the analysis job in MET  |
| tmax           | int   | stop time of the analysis job in MET   |
| timebin        | int   | time bin size of the job submission in seconds; it relates to the extent of one fermipy analysis: if less than <code>tmax-tmin</code> then segmented lightcurves will be submitted as parallel analyses jobs to cover the full <code>[tmin, tmax]</code> interval, if equal to <code>tmax-tmin</code> then a single analysis will be submitted |
| emax           | int   | maximum energy of the analysis         |
| mode           | str   | execution mode relative to size of time bin; options: <code>hour</code> (compute at hours timescale from 1 day prior tmin to 1 day after tmax), <code>fix</code> (ompute at given timescale from tmin to tmax), <code>integral</code> (compute integral from tmin to tmax)                                     |
| queue          | str   | slurm partition name                   |
| sbatch         | bool  | submit jobs after creating them       |
| activation     | str   | conda activation keyword; options: <code>conda</code>, <code>source</code> |

We also provide a [template](template_slurm.ll) example for the job submission script. Please follow the specified instruction within it.

In exemple:

```yaml
slurm:
  envname: fermipy2
  template: /data01/homes/dipiano/FermiTools/lateasy/crab/conf/slurm.ll
  bkgresults: backgrounds.txt
  name: PY2
  tmin: 276652802
  tmax: 276739202
  timebin: 86400
  emax: 300000
  mode: fix
  queue: large
  sbatch: true
  activation: conda
```

### Section: <code>folded</code>

The tag <code>folded</code> of the configuration file, collects the parameters required to run folded analyses. This section is required only to submit folded analysis job.

| keyword        | type  | description                            |
|----------------|-------|----------------------------------------|
| bins           | int   | number of bins, 0 to select all available ones |

In exemple:

```yaml
folded:
  bins: 0
```

### Section: <code>postprocessing</code>

The tag <code>postprocessing</code> of the configuration file, collects the parameters required to run the postprocessing script. This script gathers all results in a single file, based on the type of output you want to collect. This section is required only to to run the postprocessing script.

| keyword        | type  | description                            |
|----------------|-------|----------------------------------------|
| collect        | str   | which results to collect data from, options: <code>LC</code>, <code>LOC</code>, <code>ROI</code>, <code>SED</code>       |
| mints          | int   | minimum ts threshold for detection     |
| plot           | bool  | compute default plot for collected data, only if <code>collect=LC</code> |

In exemple:

```yaml
postprocessing:
  collect: lc
  mints: 9
  plot: false
```

