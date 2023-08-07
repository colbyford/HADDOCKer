FROM python:3.9-bullseye

LABEL maintainer="Colby T. Ford <colby@tuple.xyz>"

ENV DEBIAN_FRONTEND noninteractive
USER root

# gfortran-9 is the latest supported by CNS
# gfortran-10 changed type mismatch warnings to errors
# Debian Bullseye (11) is the latest with gfortran-9
RUN apt-get update && \
    apt-get install -y \
        build-essential \
        git \
        nano \
        wget \
        cmake \
        gfortran-9 \
        flex \
        csh && \
    apt-get clean && \
    ln -s /usr/bin/gfortran-9 /usr/bin/gfortran

## Make software directory
RUN mkdir /software
WORKDIR /software

## Checkout HADDOCK 3 and custom cns1.3 files
## (https://github.com/haddocking/haddock3)
RUN git clone --recursive https://github.com/haddocking/haddock3.git && \
    cd haddock3 && \
    ## v3.0.0-beta.3
    git checkout 1cca9b5

## Install CNSsolve (http://cns-online.org/v1.3/)
COPY cns_solve_1.3_all_intel-mac_linux.tar.gz /software/

# the custom cns1.3 files are from the HADDOCK3 repo under "varia"
RUN export CNS=/software/cns_solve && \
    tar -xzf /software/cns_solve_1.3_all_intel-mac_linux.tar.gz && \
    mv /software/cns_solve_1.3/ $CNS && \
    rm /software/cns_solve_1.3_all_intel-mac_linux.tar.gz && \
    cp /software/haddock3/varia/cns1.3/* $CNS/source && \
    sed -i 's/_CNSsolve_location_/\/software\/cns_solve/g' $CNS/cns_solve_env && \
    chmod -R 777 /software && \
    cd $CNS && \
    make install compiler=gfortran

RUN mkdir -p /software/haddock3/bin/ && \
    ln -s /software/cns_solve/intel-x86_64bit-linux/source/*.exe /software/haddock3/bin/cns

## Compile HADDOCK
RUN cd /software/haddock3/src/fcc/src && \
    chmod u+x Makefile && \
    make

RUN cd /software/haddock3 && \
    pip install -r requirements.txt && \
    python setup.py develop --no-deps

WORKDIR /software/haddock3
