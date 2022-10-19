# Fermi/LAT monitoring lightcurve comparison

To compare the collected results via the post-processing [script](../collect_results.py) with the official Fermi/LAT monitoring lightcurve you first have to download the data file from the [repository](https://fermi.gsfc.nasa.gov/ssc/data/access/lat/msl_lc/). Secondly, you must run the following script as follows:

```bash
python compare_fermi_lc.py --pipeconf <your_pipe.yml> --fermi <fermi_data.lc>
```

The script will produce a plot of the Fermi/LAT lightcurve (energy range from 100 to 300000 keV) and your own results, displaying both the flux and test statistic as a function of time. 