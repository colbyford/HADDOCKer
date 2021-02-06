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

## Make software directory
RUN mkdir software

## Install CNSsolve (http://cns-online.org/v1.3/)
COPY cns_solve_1.3_all_intel-mac_linux.tar.gz /software
RUN cd software && \
    gunzip cns_solve_1.3_all_intel-mac_linux.tar.gz && \
    tar xvf cns_solve_1.3_all_intel-mac_linux.tar

## Install HADDOCK (https://www.bonvinlab.org/software/haddock2.4/installation/)
COPY haddock2.4-2021-01.tgz /software
RUN cd software && \
    tar xvfz haddock2.4-2021-01.tgz