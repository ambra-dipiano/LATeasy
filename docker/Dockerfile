# Pull base image
FROM oraclelinux:8 AS oracle8

# ---------------------------------- Installing dependencies as root ---------------------------------- 
RUN yum install -y epel-release git cmake3 gcc-c++ gcc binutils \
compat-openssl10 libX11-devel libXpm-devel libXft-devel libXext-devel \ 
gsl-devel openssl-devel wget bzip2-devel libffi-devel xz-devel sqlite-devel \
ncurses ncurses-devel make xz libzstd libzstd-devel which

# ---------------------------------- Install python as root ---------------------------------- 
RUN yum install -y python39 python39-devel
RUN python3 --version
RUN python3 -m pip install --upgrade pip

# ----------------------------------- Install Ruby 2.5.9 as root (Ruby 1.9 does not compile) ----
RUN yum install -y ruby 

# ---------------------------------- Create Agilepy user ---------------------------------- 
RUN useradd flareadvocate
USER flareadvocate
WORKDIR /home/flareadvocate
RUN mkdir -p /home/flareadvocate/dependencies
SHELL ["/bin/bash", "--login", "-c"]

user root 

RUN wget https://repo.anaconda.com/archive/Anaconda3-2023.07-2-Linux-x86_64.sh && \
    chmod +x Anaconda3-2023.07-2-Linux-x86_64.sh && \
    ./Anaconda3-2023.07-2-Linux-x86_64.sh -b -p /opt/conda && \
    rm Anaconda3-2023.07-2-Linux-x86_64.sh

COPY ./ /opt/FermiTools/


RUN ls /opt/FermiTools/


RUN chown -R flareadvocate:flareadvocate /opt/FermiTools/

USER flareadvocate

RUN export PATH=$PATH:/opt/conda/bin && conda config --append channels conda-forge && conda config --append channels fermi && conda config --append channels pypi && conda env create -n fermi -f /opt/FermiTools/environment.yml

RUN export PATH=$PATH:/opt/conda/bin && source activate fermi && cd /opt/FermiTools/ && pip install -e .

USER root
RUN  mkdir /shared_dir && chown -R flareadvocate:flareadvocate /shared_dir
#COPY ./entrypoint.sh /home/flareadvocate/entrypoint.sh
#RUN chmod +x /home/flareadvocate/entrypoint.sh

USER flareadvocate
#ENTRYPOINT ["bash", "/home/flareadvocate/entrypoint.sh"]