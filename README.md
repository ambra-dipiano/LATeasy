# Introduction

This repository is intended as a collection of tools and script to run automated analysis of Fermi/LAT data with fermipy analysis tool. 

## Environment requirements and necessary variables

We provide an environment recipe for [https://www.anaconda.com/products/distribution](anconda). Any variation from it is not granted to work.

The code requires the following environmental variables:

- <code>FERMITOOLS</code> the absolute path where the repository is installed
- <code>FERMIDATA</code> the absolute path where Fermi data are stored
- <code>FERMIMODEL</code> the absolute path where Fermi source models are stored
- <code>FERMI_DIFFUSE_DIR</code> the absolute path where Fermi diffuse model is stored

## Configuration files

The repository provides two template configuration files in <code>conf</code>. You can find examples of compiled configuration files in the same folder.

- the template for the configuration fermipy analysis: <code>conf_template_fermianalysis.yml</code>
- the template for the configuration of the pipeline: <code>conf_template_pipe.yml</code>

We ask the user to <b>NOT</b> remove any fields in the configuration files, and update accordingly the input parameters based on their use case. If one or more fields are not require by the use case, please leave the field empty.
