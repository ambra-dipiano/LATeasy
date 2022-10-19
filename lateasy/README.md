# Fermi/LAT analysis pipeline

To run the analysis you will need two configuration files. The one referring to the fermipy configuration, and the on referring to the pipeline configuration. Further informazione on the configuration can be found in this [README](templates/README.md).

Run the fermi analysis:
```bash
python run_fermianalysis.py --pipeconf <your_pipe.yml> --fermiconf <your_fermianalysis.yml>
```

Furthermore provide also a [presentation](https://docs.google.com/presentation/d/1eTz8FA4qTjW9XyVesUEjY7dBzDi_E-pEzzoXDrhe6dQ/edit?usp=sharing) of the proceedure description step by step.

## Background estimation

Unless you have previous knowledge about the background, proper estimation with this tool should be configured as follows:

For the background (only interested parameters are shown):

```yaml
background:
  isofree: true
  isonorm: 1
  galfree: true
  galnorm: 1 
  galindex: 0
```

For the lightcurve (only interested parameters are shown):

```yaml
lightcurve:
  bintype: integral
```

For the job submission if necessary (only interested parameters are shown):

In exemple:

```yaml
slurm:
  mode: integral
```

This will allow the pipeline to run a first a first analysis on the whole selected time interval (integral, i.e. a single point) to estimate the background parameters. If your analysis comprises data for longer time periods (i.e. more than a month) you may want to perform this monthly. You can achive this changing the job submission configuration as follows (only interested parameters are shown):

```yaml
slurm:
  mode: fix
  timebin: 2592000
```

This will estimate the background over a month time interval.

## Lightcurve

To execute the final lightcurve you have two options.

If you have knowledge of the background or have extimated it as specified in the previous [section](#background-estimation), then you may fix the values such the following example (only interested parameters are shown):

```yaml
background:
  isofree: false
  isonorm: 0.8486124962536352
  galfree: false
  galnorm: 1.0754991214934595
  galindex: 0
```

If you do not have any solid knowledge about the background, you may use instead (only interested parameters are shown):

```yaml
background:
  isofree: true
  isonorm: 1
  galfree: true
  galnorm: 1 
  galindex: 0
```

To submit a single job with given fixed lightcurve binning (i.e. daily lightcurve) you may use the following configuration (only interested parameters are shown):

```yaml
lightcurve:
  bintype: fix
  binsize: 86400

slurm:
  mode: integral
```

To submit multiple jobs over given periods (i.e. monthly) with given fixed lightcurve binning (i.e. daily lightcurve) you may use the following configuration (only interested parameters are shown):

```yaml
lightcurve:
  bintype: fix
  binsize: 86400

slurm:
  mode: fix
  timebin: 2592000
```
