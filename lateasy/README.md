# Fermi/LAT analysis pipeline

To run the analysis you will need two configuration files. The one referring to the fermipy configuration, and the on referring to the pipeline configuration. Further informazione on the configuration can be found in this [README](templates/README.md).

Run the fermi analysis:
```bash
python run_fermianalysis.py --pipeconf <your_pipe.yml> --fermiconf <your_fermianalysis.yml>
```

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

This will allow the pipeline to run a first a first analysis on the whole selected time interval (integral, i.e. a single point) to estimate the background parameters. If your analysis comprises data for longer time periods (i.e. more than a month) you may want to perform this monthly. You can achive this changing the job submission configuration as follows:

```yaml
slurm:
  mode: fix
  timebin: 2592000
```

This will estimate the background over a month time interval.

## Lightcurve, sed and localisation



