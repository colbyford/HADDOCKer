FROM python:3.9

LABEL maintainer="Colby T. Ford <colby@tuple.xyz>"

ENV DEBIAN_FRONTEND noninteractive
USER root

RUN apt-get update && \
    apt-get install -y \
        build-essential \
        git \
        nano \
        wget \
        cmake

## Make software directory
RUN mkdir /software
WORKDIR /software

## Install HADDOCK 3 (https://github.com/haddocking/haddock3)
RUN git clone --recursive https://github.com/haddocking/haddock3.git && \
    cd haddock3 && \
    ## v3.0.0-beta.3
    git checkout 1cca9b5

RUN cd /software/haddock3/src/fcc/src && \
    chmod u+x Makefile && \
    make

RUN cd /software/haddock3 && \
    pip install -r requirements.txt && \
    python setup.py develop --no-deps

## Install CNSsolve (http://cns-online.org/v1.3/)
COPY cns_solve_1.3_all_intel-mac_linux.tar.gz /software/

RUN tar -xzf /software/cns_solve_1.3_all_intel-mac_linux.tar.gz && \
    mv /software/cns_solve_1.3/ /software/cns_solve/ && \
    rm /software/cns_solve_1.3_all_intel-mac_linux.tar.gz

RUN mkdir -p /software/haddock3/bin/ && \
    ln -s /software/cns_solve/intel-x86_64bit-linux/source/cns_solve-1111091055.exe /software/haddock3/bin/cns


WORKDIR /software/haddock3