# Pull base image
#FROM oraclelinux:8 AS oracle8
FROM centos:7

SHELL ["/bin/bash", "--login", "-c"]
# ---------------------------------- Installing dependencies as root ---------------------------------- 
RUN yum install -y epel-release git cmake3 gcc-c++ gcc binutils \
compat-openssl10 libX11-devel libXpm-devel libXft-devel libXext-devel \ 
gsl-devel openssl-devel wget bzip2-devel libffi-devel xz-devel sqlite-devel \
ncurses ncurses-devel make xz libzstd libzstd-devel which

RUN cd /tmp \
    && wget https://www.python.org/ftp/python/3.9.7/Python-3.9.7.tgz \
    && tar zxvf Python-3.9.7.tgz \
    && cd Python-3.9.7/ \
    && ./configure && make && make altinstall \
    && echo 'alias python=python3.9' >> ~/.bashrc \
    && echo 'alias python3=python3.9' >> ~/.bashrc \
    && ln -s /usr/local/bin/python3.9 /usr/local/bin/python3 \
    && source ~/.bashrc



# ---------------------------------- Install python as root ---------------------------------- 
#RUN yum install -y python39 python39-devel
#RUN python3 --version
#RUN python3 -m pip install --upgrade pip

# ----------------------------------- Install Ruby 2.5.9 as root (Ruby 1.9 does not compile) ----
RUN yum install -y ruby 



## --------------- install slurm --------------------------------------------- ##
# Install common YUM dependency packages
RUN source ~/.bashrc \
    && set -ex \
    && yum makecache \
    && yum -y update \
    && yum -y install epel-release \
    && yum -y install \
        autoconf \
        bash-completion \
        bzip2 \
        bzip2-devel \
        file \
        iproute \
        jq \
        gcc \
        gcc-c++ \
        gdbm-devel \
        glibc-devel \
        gmp-devel \
        libasan \
        libffi-devel \
        libGL-devel \
        libX11-devel \
        Lmod \
        make \
        mariadb-server \
        mariadb-devel \
        munge \
        munge-devel \
        ncurses-devel \
        openssl-devel \
        openssl-libs \
        perl \
        pkconfig \
        psmisc \
        readline-devel \
        sqlite-devel \
        tcl-devel \
        tk \
        tk-devel \
        tix-devel \
        supervisor \
        wget \
        vim-enhanced \
        xz-devel \
        zlib-devel \
    && yum clean all \
    && rm -rf /var/cache/yum

#
#
#
#

# Compile, build and install Slurm from Git source
RUN source ~/.bashrc && \
    set -ex && \
    rm -rf /tmp/slurm_build && \
    mkdir -p /tmp/slurm_build && \
    cd /tmp/slurm_build && \
    wget -O slurm.tar.gz https://github.com/SchedMD/slurm/archive/refs/tags/slurm-17-11-12-1.tar.gz && \
    tar -xzf slurm.tar.gz && \
    cd slurm-slurm-17-11-12-1 && \
    bash ./configure --sysconfdir=/etc/slurm && \
    make -j 8 && \
    make install && \
    rm -rf /tmp/slurm_build

RUN source ~/.bashrc \
    && set -ex \
    && groupadd -r slurm \
    && useradd -u 801 -r -g slurm slurm \
    && mkdir -p /etc/sysconfig/slurm \
        /var/spool/slurmd \
        /var/run/slurmd \
        /var/lib/slurmd \
        /var/log/slurm \
    && chown slurm:root /var/spool/slurmd \
        /var/run/slurmd \
        /var/lib/slurmd \
        /var/log/slurm \
    && /sbin/create-munge-key


# ---------------------------------- Create Agilepy user ---------------------------------- 
RUN useradd flareadvocate
USER flareadvocate
WORKDIR /home/flareadvocate
RUN mkdir -p /home/flareadvocate/dependencies

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
SHELL ["/bin/sh", "-c"]
#ENTRYPOINT ["bash", "/home/flareadvocate/entrypoint.sh"]