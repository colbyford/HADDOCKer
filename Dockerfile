FROM ubuntu:16.04

MAINTAINER Colby T. Ford <colby.ford@uncc.edu>

## Install generic libraries for downloading other libraries 
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y git cmake wget

## Make software directory
RUN mkdir software

## Install CNSsolve (http://cns-online.org/v1.3/)
COPY cns_solve_1.3_all_intel-mac_linux.tar.gz /software
RUN cd software && \
    gunzip cns_solve_1.3_all_intel-mac_linux-mp.tar.gz && \
    tar xvf cns_solve_1.3_all_intel-mac_linux-mp.tar
