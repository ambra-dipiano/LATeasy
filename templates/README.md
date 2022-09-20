# Fermi analysis configuration

Please, refer to the [fermipy documentation](https://fermipy.readthedocs.io/en/latest/).

# Pipeline configuration

The configuration file is structure in different tags. The following list provides a complete description of all parameters, as can also be found commented in the template file.

This tag will contain all paths.

* path
    - data: (str) folder where data is stored        
    - models: (str) folder where models are stored
    - galdir: (str) folder where the galactic diffuse background is stored
    - output: (str) folder where to store output

This tag will contain all files name relative to the previously defined path.

* file
    - target: (str) name of model of target source 
    - photometry: (str) name of file contaning the AP exposure 
    - catalogue: (str) name of catalogue file
    - observation: (str) name of data file
    - inputmodel: (str) name of analysis model 

This tag will contain all initial background hypothesis.

* background
    - isomodel: (str) isothropic background model
    - isofree: (bool) free isothropic background
    - isonorm: (float) normalisation value of the isothropic background
    - galmodel: (str) galactic background model
    - galfree: (bool) free galactic background model
    - galnorm: (float) normalisazione value of the galactic background model
    - galindex: (float) index value of the galactic background model

This tag will contain all parameters related to the target source.

* target
    - name: (str) name of the target source

This tag will contain a list of all variable sources to check.

* variable_sources 
    - <SOURCE_NAME>: replace this tag with the source name, you can add as many as needed
        1. ROI_Center_Distance: (float) distance from center
        2. Signif_Avg: (float) significance

This tag will contain a list of all extended sources to check.

* extended_sources
    - <SOURCE_NAME>: replace this tag with the source name, you can add as many as needed
        1. Extended_Source_Name: (str) extended catalogue name of the source
        2. ROI_Center_Distance: (int) distance form the center
        3. Signif_Avg: (float) significance
        4. Normalisation: (list) normalisation values
            - 
        5. Normalisation_Error: (list) normalisation errors
            - 

This tag will contain all execution option.

* execute
    - lc: (bool) perform lightcurve
    - sed: (bool) perform sed
    - localise: (bool) perform localisation

This tag will contain all lightcurve options.

* lightcurve
    - bintype: (str) how to define time bins < fix/filter/integral >
    - binsize: (int) lightcurve binsize in seconds for fix bins

This tag will contain all make4FGL.py script options.

* makemodel
    - normfree: (bool) free normalisation
    - radius: (float) inner radius for freeing normalisation
    - significance: (float) minimum significance for freeing normalisation
    - ds9reg: (bool) make ds9 region file

This tag will contain all to update the sky region.

* updatemodel
    - radius: (float) radius within sources are freed
    - extradius: (float) external radius within sources are freed by condition
    - mints: (int) min ts to free sources within radius
    - extmints: (int) min ts to free sources withint external radius
    - minvariability: (float) min variability threshold
    - freeparams: (list) parameters to free, must be a list
        1.
    - newbkg: (list) backgrounds to keep or substitute
        1. 
