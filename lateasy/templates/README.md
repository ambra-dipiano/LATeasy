# Configuration files

Specifics on the configuration files.

## Fermi analysis configuration

Please, refer to the [fermipy documentation](https://fermipy.readthedocs.io/en/latest/).

## Pipeline configuration

The configuration file is structure in different tags. The following list provides a complete description of all parameters, which can also be found commented in the template file. We suggest to make a copy of the template provided and fill out all section required by your specific use case.

In the following we present a description of the parameters pertainin to each section of the configuration file.

### Section: <code>path</code>

The tag <code>path</code> of the configuration file, collects all absolute paths poiting to directories required by the analysis. It is important that you provide absolute path, without relative pointers or environmental variable to avoid ambiguity. This section is always required to be compiled.

| keyword        | type | description                            |
|----------------|------|----------------------------------------|
| data           | str  | folder where data is stored            |   
| models         | str  | folder where models are stored         |
| galdir         | str  | folder where the galactic diffuse background is stored |
| output         | str  | folder where to store output           |

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

### Section: <code>background</code>

The tag <code>background</code> of the configuration file, collects all initial will contain all initial background hypothesis. If unsure, leave the values empty and provide only the models name. Beware that the specified model must be locally existing in your <code>galdir</code> folder from the <code>path</code> section of the configuration file. This section is always required to be compiled.

| keyword        | type | description                            |
|----------------|------|----------------------------------------|
| isomodel       | str  | name of the isothropic background model, it must be placed in  <code>galdir</code> from the previous section |
| isofree        | bool | free isothropic background during analysis |
| isonorm        | float | normalisation value of the isothropic background model, if null takes default |
| galmodel       | str  | name of the galactic background model, it must be placed in  <code>galdir</code> from the previous section |
| galfree        | bool | free galactic background model during analysis |
| galnorm        | float | normalisazione value of the galactic background model, if null takes default |
| galindex       | float | index value of the galactic background model, if null takes default |

### Section: <code>target</code>

The tag <code>target</code> of the configuration file, collects all parameters relevant to the target itself. Beware that the model information will not be duplicated in this section, but should provided in a proper XML file containing both spectral and spatial models of the source. This section is always required to be compiled.

| keyword        | type | description                            |
|----------------|------|----------------------------------------|
| name           | str  | name of the target source              |
| 4FGLname       | str  | name of the target source in 4FGL cat, if missing or equal to the "name" then please duplicate the value here |

### Section: <code>variable_sources</code>

The tag <code>variable_sources</code> of the configuration file, should be compiled using the 4FGL name of all variabls sources that you want to check during the analysis as children tags. You must substitute the <code><SOURCE_NAME></code> tag with the source catalogue name. You can add as many as you need, so long as you replicate the same format. For each children tag you will need the following parameters. During the analysis these parameters will be use to check the parameters fit update. If not required, please put the <code>variable_sources</code> tag to <code>NULL</code>

| keyword        | type | description                            |
|----------------|------|----------------------------------------|
| ROI_Center_Distance | float | distance from the sky region center in degrees |
| Signif_Avg          | float | significance reported in the catalogue |


### Section: <code>extended_sources</code>

The tag <code>extended_sources</code> of the configuration file, should be compiled using the 4FGL name of all extended sources that you want to check during the analysis as children tags. You must substitute the <code><SOURCE_NAME></code> tag with the source catalogue name. You can add as many as you need, so long as you replicate the same format. For each children tag you will need the following parameters. During the analysis these parameters will be use to check the parameters fit update. If not required, please put the <code>variable_sources</code> tag to <code>NULL</code>

| keyword        | type | description                            |
|----------------|------|----------------------------------------|
| ROI_Center_Distance | float | distance from the sky region center in degrees |
| Signif_Avg          | float | significance reported in the catalogue |
| Normalisation       | list  | normalisation values of the source model |
| Normalisation_Error | list  | normalisation errors of the source model |

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

### Section: <code>lightcurve</code>

The tag <code>lightcurve</code> of the configuration file, collects all lightcurve parameters of the analysis. This section must always be compiled for the analysis script and the jobs generation scripts.

| keyword        | type  | description                            |
|----------------|-------|----------------------------------------|
| bintype        | str   | how to define time bins; options: <code>fix</code>, <code>filter</code>, <code>integral</code> |
| binsize        | int   | lightcurve binsize in seconds when <code>bintype=fix</code> |

* makemodel: this tag will contain all make4FGL.py script options
  * normfree: (bool) free normalisation
  * radius: (float) inner radius for freeing normalisation
  * significance: (float) minimum significance for freeing normalisation
  * ds9reg: (bool) make ds9 region file

* updatemodel: this tag will contain all parameters to update the sky region  
  * radius: (float) radius within sources are freed
  * extradius: (float) external radius within sources are freed by condition
  * mints: (int) min ts to free sources within radius
  * extmints: (int) min ts to free sources withint external radius
  * minvariability: (float) min variability threshold
  * freeparams: (list) parameters to free, must be a list
  * newbkg: (list) backgrounds to keep or substitute

* slurm: this tag will contain all slurm job submission parameters 
  * envname: (str) virtual environment to activate
  * template: (str) path to slurm job submission template to launch
  * bkgresults: (str) path to LC results file to extract background parameter if needed
  * name: (str) basename of the analysis
  * tmin: (float) start time 
  * tmax: (float) stop time
  * timebin: (float) time bin size of distinct analysis
  * emax: (int) maximum energy
  * mode: (str) execution mode relative to size of time bin: <hour|fix|integral>
  * queue: (str) slurm partition
  * sbatch: (bool) to submit jobs after creating them

* folded: this tag will contain all folded analysis options
  * bins: (int) number of bins, 0 if all

* postprocessing: this tag will contain all post-processing options
  * collect: (str) which results to collect data from <LC|LOC|ROI|SED>
  * mints: (int) minimum ts threshold for significant signal
  * plot: (bool) compute default plot for collected data