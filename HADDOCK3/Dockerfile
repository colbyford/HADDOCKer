# FROM phusion/baseimage:0.9.16
FROM jupyter/scipy-notebook:latest
# FROM python:3.7

MAINTAINER Colby T. Ford <colby.ford@uncc.edu>

## global env
# ENV HOME=/home TERM=xterm

## Change bash Shell to tcshRUN \
# RUN apt-get update && \
#     # apt-get dist-upgrade -y && \
#     apt-get install tcsh sudo && \
#     chsh -s /bin/tcsh
#     # chsh -s /usr/bin/tcsh
# SHELL ["/bin/tcsh", "-c"]

## set proper timezone
# RUN echo America/New_York > /etc/timezone && sudo dpkg-reconfigure --frontend noninteractive tzdata

## Make software directory
RUN mkdir software

## Get HADDOCK 3
## Source: https://github.com/haddocking/haddock3/archive/refs/tags/v3.0.alpha2.tar.gz
COPY haddock3-3.0.alpha2.tar.gz /software
RUN cd software && \
    mkdir haddock && \
    tar xvfz haddock3-3.0.alpha2.tar.gz -C /software/haddock && \
    cd haddock && \
    pip install -r requirements.txt