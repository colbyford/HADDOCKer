# FROM phusion/baseimage:0.9.16
# FROM jupyter/scipy-notebook:latest
FROM python:3.9

MAINTAINER Colby T. Ford <colby.ford@uncc.edu>

ENV DEBIAN_FRONTEND noninteractive
USER root

RUN apt-get update && \
    apt-get install -y \
        build-essential \
        git \
        wget \
        cmake

## Make software directory
RUN mkdir /software
WORKDIR /software

## Install HADDOCK 3
## Source: https://github.com/haddocking/haddock3
RUN git clone --recursive https://github.com/haddocking/haddock3.git

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

RUN cd /software/cns_solve/intel-x86_64bit-linux/source && \
    find . -type f -name 'cns_solve*.exe' -exec sh -c 'x="{}"; mv "$x" "cns_solve.exe"' \;

RUN mkdir -p /software/haddock3/bin/ && \
    ln -s /software/cns_solve/intel-x86_64bit-linux/source/cns_solve.exe /software/haddock3/bin/cns