# FROM ubuntu:16.04
FROM phusion/baseimage:0.9.16
# FROM mcr.microsoft.com/azureml/openmpi3.1.2-ubuntu16.04

ENV DEBIAN_FRONTEND noninteractive
USER root

# WORKDIR /software

## global env
# ENV HOME=/home TERM=xterm

## set proper timezone
# RUN echo America/New_York > /etc/timezone && sudo dpkg-reconfigure --frontend noninteractive tzdata

## Install essential for building
    # software-properties-common \
RUN apt-get update && \
    apt-get install -y \
        build-essential \
        git \
        cmake \
        wget \
        flex \
        gfortran \
        python-pip \
        python2.7 \
        python2.7-dev

## Change bash Shell to tcsh
RUN sudo apt-get install tcsh && \
    chsh -s /bin/tcsh
    # chsh -s /usr/bin/tcsh
SHELL ["/bin/tcsh", "-c"]

## Make software directory
# RUN mkdir /software

## Install CNSsolve (http://cns-online.org/v1.3/)
COPY cns_solve_1.3_all_intel-mac_linux.tar.gz /software/
# RUN cd /software && \
#     gunzip cns_solve_1.3_all_intel-mac_linux.tar.gz && \
#     tar xvf cns_solve_1.3_all_intel-mac_linux.tar && \
#     rm cns_solve_1.3/cns_solve_env
# COPY cns_solve_env /software/cns_solve_1.3
# RUN cd /software/cns_solve_1.3 && \
#     make install

## Install FreeSASA
# RUN cd software && \
#     wget https://freesasa.github.io/freesasa-2.0.3.tar.gz && \
#     tar xvfz freesasa-2.0.3.tar.gz && \
#     cd freesasa-2.0.3 && \
#     ./configure --disable-json --disable-xml --prefix ~/software && \
#     make && \
#     make install

## Install HADDOCK (https://www.bonvinlab.org/software/haddock2.4/installation/)
COPY haddock2.4-2021-01.tgz /software/
# RUN cd /software && \
#     tar xvfz haddock2.4-2021-01.tgz

## re-Make CNS with HADDOCK
RUN setenv PFX $HOME/haddock && \
    setenv CNS $PFX/cns_solve && \
    mkdir -p $CNS && \
    tar -C $CNS --strip-components=1 -xzf /software/cns_solve_1.3_all_intel-mac_linux.tar.gz && \
    tar -C $PFX -xzf /software/haddock2.4-2021-01.tgz && \
    pushd $CNS && \
    sed -i.BACK -e "s|_CNSsolve_location_|$CNS|g" cns_solve_env && \
    cp -a $PFX/haddock2.4-2021-01/cns1.3/* source && \
    make install && \
    popd


## Copy config file
COPY local_config_file $HOME/haddock/haddock2.4-2021-01/

## Rename date/time dependent cns_solve-0000000000.exe
RUN cd $HOME/haddock/cns_solve/intel-x86_64bit-linux/source && \
    find . -type f -name 'cns_solve*.exe' -exec sh -c 'x="{}"; mv "$x" "cns_solve.exe"' \;

## Configure HADDOCK
RUN cd $HOME/haddock/haddock2.4-2021-01 && \
    ./install.csh local_config_file
    #&& \
    #source ./haddock_configure.csh

## Mimic haddock_configure.csh task
# ENV HADDOCK $HOME/haddock/haddock2.4-2021-01
# ENV HADDOCKTOOLS $HADDOCK/tools
# ENV PYTHONPATH ${HADDOCK}
# RUN alias haddock2.4 `which python` $HADDOCK/Haddock/RunHaddock.py
# ENV NACCESS `which naccess`
# ENV PALES `which pales`
# ENV PROFIT `which profit`
# ENV TENSOR2 `which tensor2`

# COPY local_config_file /software/haddock2.4-2021-01
# RUN cd /software/haddock2.4-2021-01 && \
#     ./install.csh local_config_file 
    # && \
    # source haddock_configure.csh

## Grant execution permissions to entire dir
RUN sudo chmod -R 777 $home

## Fix Symlink issue to QueueSubmit.py
RUN cd $HOME/haddock/haddock2.4-2021-01/Haddock/Main/ && \
    rm QueueSubmit.py && \
    cp QueueSubmit_concat.py QueueSubmit.py