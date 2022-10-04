# Configuration files

Specifics on the configuration files.

## Fermi analysis configuration

Please, refer to the [fermipy documentation](https://fermipy.readthedocs.io/en/latest/).

## Pipeline configuration

The configuration file is structure in different tags. The following list provides a complete description of all parameters, which can also be found commented in the template file. We suggest to make a copy of the template provided and fill out all section required by your specific use case.

In the following we present a description of the parameters pertainin to each section of the configuration file.

### Section: "path"

The tag "path" of the configuration file, collects all absolute paths poiting to directories required by the analysis. It is important that you provide absolute path, without relative pointers or environmental variable to avoid ambiguity.

| keyword        | type | description                            |
|----------------|------|----------------------------------------|
| data           | str  | folder where data is stored            |   
| models         | str  | folder where models are stored         |
| galdir         | str  | folder where the galactic diffuse background is stored |
| output         | str  | folder where to store output           |

### Section: "file"

The tag "file" of the configuration file, collects all file names which will be used during the analysis. Beware that here you should only fill the file name, without path, and you should make sure that the file is placed in the correct folder which is indicated by the following description.

| keyword        | type | description                            |
|----------------|------|----------------------------------------|
| target         | str  | name of the target source model, it must be place in "models" from the previous section |
| photometry     | str  | name of file contaning the AP exposure, it must be place in "data" from the previous section |
| catalogue      | str  | name of catalogue FITS file, it must be place in "data" from the previous section |
| observation    | str  | name of events file to create the sky region model, it must be place in "data" from the previous section |
| inputmodel     | str  | name of the sky region model to generate and use for analysis, it will be place (or must be if existing) in "models" from the previous section |
| folded8        | str  | name of folded time intervals data file, if needed it must be placed in "data" from the previous section |

### Section: "background"

The tag "background" of the configuration file, collects all initial will contain all initial background hypothesis. If unsure, leave the values empty and provide only the models name. Beware that the specified model must be locally existing in your "galdir" folder from the "path" section of the configuration file. 

| keyword        | type | description                            |
|----------------|------|----------------------------------------|
| isomodel       | str  | name of the isothropic background model, it must be placed in  "galdir" from the previous section |
| isofree        | bool | free isothropic background during analysis |
| isonorm        | float | normalisation value of the isothropic background model, if null takes default |
| galmodel       | str  | name of the galactic background model, it must be placed in  "galdir" from the previous section |
| galfree        | bool | free galactic background model during analysis |
| galnorm        | float | normalisazione value of the galactic background model, if null takes default |
| galindex       | float | index value of the galactic background model, if null takes default |

### Section: "target"

The tag "target" of the configuration file, collects all parameters relevant to the target itself. Beware that the model information will not be duplicated in this section, but should provided in a proper XML file containing both spectral and spatial models of the source.

| keyword        | type | description                            |
|----------------|------|----------------------------------------|
| name           | str  | name of the target source              |
| 4FGLname       | str  | name of the target source in 4FGL cat, if missing or equal to the "name" then please duplicate the value here |

### Section: "variable_sources"

The tag "variable_sources" of the configuration file, should be compiled using the 4FGL name of all variabls sources that you want to check during the analysis as children tags. You must substitute the <code><SOURCE_NAME></code> tag with the source catalogue name. You can add as many as you need, so long as you replicate the same format.

For each <SOURCE_NAME> children tag you will need the following parameters.

| keyword        | type | description                            |
|----------------|------|----------------------------------------|
| ROI_Center_Distance | float | distance from the sky region center in degrees |
| Signif_Avg          | float | significance reported in the catalogue |

* extended_sources: this tag will contain a list of all extended sources to check 
  * <SOURCE_NAME>: replace this tag with the source name, you can add as many as needed
    * ROI_Center_Distance: (int) distance form the center
    * Signif_Avg: (float) significance
    * Normalisation: (list) normalisation values
    * Normalisation_Error: (list) normalisation errors

* execute: this tag will contain all execution option
  * lc: (bool) perform lightcurve
  * sed: (bool) perform sed
  * localise: (bool) perform localisation
  * agg_backend: (bool) change matplotlib backent to agg
  * verbose: (int) value of fermipy verbosity
  * loglevel: (int) level of pipeline logging: 0=none, 10=debug, 20=info, 30=warning, 40=error, 50=critical

* lightcurve: this tag will contain all lightcurve options
  * bintype: (str) how to define time bins < fix/filter/integral >
  * binsize: (int) lightcurve binsize in seconds for fix bins

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