FROM python:3.12.13-slim

LABEL maintainer="Colby T. Ford <colby@tuple.xyz>, Rafael Jaimes III <rafael.jaimes@ll.mit.edu>"

ENV DEBIAN_FRONTEND=noninteractive
USER root

## System dependencies
RUN apt-get update && \
    apt-get install -y \
        build-essential \
        git \
        nano \
        wget \
        cmake && \
    apt-get clean 

## Make software directory
RUN mkdir /software
WORKDIR /software

## Checkout HADDOCK 3
RUN git clone --recursive https://github.com/haddocking/haddock3.git && \
    cd haddock3 && \
    ## v3.0.0-beta.5
    # git checkout 1482d85
    ## 2024.10.0b6
    # git checkout 8763134
    ## 2026.03.0
    git checkout 4d6f6f1

RUN cd /software/haddock3 && \
    pip install .

## Set Working Directory back to haddock3
WORKDIR /software/haddock3
