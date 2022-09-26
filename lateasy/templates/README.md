# Configuration files

Specifics on the configuration files.

## Fermi analysis configuration

Please, refer to the [fermipy documentation](https://fermipy.readthedocs.io/en/latest/).

## Pipeline configuration

The configuration file is structure in different tags. The following list provides a complete description of all parameters, as can also be found commented in the template file.

* path: this tag will contain all paths
  * data: (str) folder where data is stored        
  * models: (str) folder where models are stored
  * galdir: (str) folder where the galactic diffuse background is stored
  * output: (str) folder where to store output

* file: this tag will contain all files name relative to the previously defined path
  * target: (str) name of model of target source 
  * photometry: (str) name of file contaning the AP exposure 
  * catalogue: (str) name of catalogue file
  * observation: (str) name of data file
  * inputmodel: (str) name of analysis model 
  * folded8: (str) name of folded time intervals


* background: this tag will contain all initial background hypothesis
  * isomodel: (str) isothropic background model
  * isofree: (bool) free isothropic background
  * isonorm: (float) normalisation value of the isothropic background model, if null takes default
  * galmodel: (str) galactic background model
  * galfree: (bool) free galactic background model
  * galnorm: (float) normalisazione value of the galactic background model, if null takes default
  * galindex: (float) index value of the galactic background model, if null takes default

* target: this tag will contain all parameters related to the target source
  * name: (str) name of the target source

* variable_sources: this tag will contain a list of all variable sources to check 
  * <SOURCE_NAME>: replace this tag with the source name, you can add as many as needed
    * ROI_Center_Distance: (float) distance from center
    * Signif_Avg: (float) significance

* extended_sources: this tag will contain a list of all extended sources to check 
  * <SOURCE_NAME>: replace this tag with the source name, you can add as many as needed
    * Extended_Source_Name: (str) extended catalogue name of the source
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