# Introduction

This repository is intended as a collection of tools and script to run automated analysis of Fermi/LAT data with fermipy analysis tool. 

## Environment requirements and necessary variables

We provide an environment recipe for [https://www.anaconda.com/products/distribution](anconda). Any variation from it is not granted to work.

- <code>environment-fermipy2.yml</code> for fermpy v0.19 and python v2.7
- <code>environment-fermipy3.yml</code> for fermipy v1.0 and python v3.7 

## Configuration files

The repository provides two template configuration files in <code>template</code>. You can find examples of compiled configuration files in the <code>examples</code> folder.

- the template for the configuration fermipy analysis: <code>templates/template_fermianalysis.yml</code>
- the template for the configuration of the pipeline: <code>templates/template_pipe.yml</code>

We ask the user to <b>NOT</b> remove any fields in the configuration files, and update accordingly the input parameters. If one or more fields are not require by the use case, please leave the field empty. Further informazione on the configuration can be found [here](templates/README.md)
