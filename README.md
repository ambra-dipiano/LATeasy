# Introduction

This repository is intended as a collection of tools and script to run automated analysis of Fermi/LAT data with fermipy analysis tool. 

## Environment requirements 

We provide an environment recipe for [anaconda](https://www.anaconda.com/products/distribution). Any variation from it is not granted to work.

- [environment-fermipy2.yml](./environment-fermipy2.yml) for fermpy v0.19 and python v2.7
- [environment-fermipy3.yml](./environment-fermipy3.yml) for fermipy v1.2 and python v3.9 

You can create such environments like this:

```bach
conda env create -n <name> -f <environment-file.yml>
```

## Installation

Please activate the conda environment beforehand:

```bash
conda activate <name>
```

To install the software:

```bash
pip install .
```

For developers, you can install in editable mode:

```bash
pip install -e .
```

# Configuration files

The repository provides two template configuration files in <code>template</code>. You can find examples of compiled configuration files in the <code>examples</code> folder.

- the template for the configuration fermipy analysis: [template_fermianalysis.yml](./lateasy/templates/template_fermianalysis.yml)
- the template for the configuration of the pipeline: [template_pipe.yml](./lateasy/templates/template_pipe.yml)
- the template for the slurm job submission of the pipeline: [template_slurm.ll](./lateasy/templates/template_slurm.ll)

We ask the user to <b>NOT</b> remove any fields in the configuration files, and update accordingly the input parameters. If one or more fields are not require by the use case, please leave the field empty. Further informazione on the configuration can be found [here](lateasy/templates/README.md).

# Sky region models

To perform the analysis two sets of models other than the background are required. First of all is the target model, secondly is the model of the sky region. 

## Generate the sky region model

To generate the sky region model we will make use of a Fermi user contribution script, the [make4FGLxml.py](https://fermi.gsfc.nasa.gov/ssc/data/analysis/user/make4FGLxml.py). To better understand the used parameters, please refer to the official [readme](https://fermi.gsfc.nasa.gov/ssc/data/analysis/user/readme_make4FGLxml.txt). To this model, if required, the target source model will be added. Further informazione on the configuration can be found [here](lateasy/templates/README.md).

Generate the sky region model:
```bash
python generate_fermianalysis_inputmodel.py --pipeconf <your_pipe.yml>
```

## Update the sky region model

To update the sky region model we will make use of the catalogue combined with the previously generated sky region model. Be sure to have both stored under the correct path. Note also that the user requires writing access to the generated file, thus we suggest to always generate your own model with the previous script. Further informazione on the configuration can be found [here](lateasy/templates/README.md).

Update the sky region model:
```bash
python update_fermianalysis_inputmodel.py --pipeconf <your_pipe.yml>
```

# Job submission

It is possible to parallelise multiple analyses through slurm. We provide a script to automatically update the fermipy configuration file (.yaml), create the executable bash script (.sh) and create the Slurm submission job (.ll). The script can directly submit the jobs after creation. Further informazione on the configuration can be found [here](lateasy/templates/README.md).

Slurm job creation and submission:
```bash
python generate_fermianalysis_jobs.py --pipeconf <your_pipe.yml> --fermiconf <your_fermianalysis.yml>
```

## Specifics on the folded analysis

Prior to create the Slurm job submission, if a folded analysis is require we provide a script to appropriately update the fermipy configuration filters. You should execute this script **PRIOR** to the Slurm job submission. You are required to provide a data file with the time intervals of the folded analysis. See the above section on configuration file for more information. Further informazione on the configuration can be found [here](lateasy/templates/README.md).

Folded configuration update:
```bash
python update_fermianalysis_folded_config.py --pipeconf <your_pipe.yml> --fermiconf <your_fermianalysis.yml>
```

# Analysis

To run the analysis you will need two configuration files. The one referring to the fermipy configuration, and the on referring to the pipeline configuration. Further informazione on the configuration can be found [here](lateasy/templates/README.md).

Run the fermi analysis:
```bash
python run_fermianalysis.py --pipeconf <your_pipe.yml> --fermiconf <your_fermianalysis.yml>
```

# Post-processing

To collect your results (lightcurve, SED, localisation or roi optimisation) in a single data file you can execute the following script. Further informazione on the configuration can be found [here](lateasy/templates/README.md).

Run the fermi analysis:
```bash
python collect_results.py --pipeconf <your_pipe.yml>
```