# FROM ubuntu:16.04
FROM phusion/baseimage:0.9.16

MAINTAINER Colby T. Ford <colby.ford@uncc.edu>

## global env
ENV HOME=/home TERM=xterm

## set proper timezone
RUN echo America/New_York > /etc/timezone && sudo dpkg-reconfigure --frontend noninteractive tzdata

## Install essential for building
    # software-properties-common \
RUN DEBIAN_FRONTEND=noninteractive
RUN \
  apt-get update && \
  apt-get dist-upgrade -y && \
  apt-get -y autoremove && \
  apt-get install -y \
    build-essential \
    git \
    cmake \
    wget \
    python-pip \
    python2.7 \
    python2.7-dev

## Change bash Shell to tcsh
RUN sudo apt-get install tcsh && \
    chsh -s /bin/tcsh
    # chsh -s /usr/bin/tcsh
SHELL ["/bin/tcsh", "-c"]

## Make software directory
RUN mkdir software

## Install CNSsolve (http://cns-online.org/v1.3/)
COPY cns_solve_1.3_all_intel-mac_linux.tar.gz /software
RUN cd software && \
    gunzip cns_solve_1.3_all_intel-mac_linux.tar.gz && \
    tar xvf cns_solve_1.3_all_intel-mac_linux.tar && \
    rm cns_solve_1.3/cns_solve_env
COPY cns_solve_env /software/cns_solve_1.3
RUN cd software/cns_solve_1.3 && \
    source cns_solve_env


## Install HADDOCK (https://www.bonvinlab.org/software/haddock2.4/installation/)
COPY haddock2.4-2021-01.tgz /software
RUN cd software && \
    tar xvfz haddock2.4-2021-01.tgz

## Configure HADDOCK
COPY local_config_file /software/haddock2.4-2021-01
RUN cd /software/haddock2.4-2021-01 && \
    ./install.csh local_config_file 
    #&& \
    #source haddock_configure.csh