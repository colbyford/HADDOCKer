FROM phusion/baseimage:0.9.16

LABEL maintainer="Colby T. Ford <colby@tuple.xyz>, Rafael Jaimes III <rafael.jaimes@ll.mit.edu>"

ENV DEBIAN_FRONTEND noninteractive
USER root

## Set the number of cores you want cns/HADDOCK to use
ARG CORES=24

## Install essential for building
RUN apt-get update && \
    apt-get install -y \
        build-essential \
        git \
        cmake \
        wget \
        flex \
        gfortran \
        python-pip \
        python3-pip \
        python3-pandas \
        python2.7 \
        python2.7-dev

## Change bash Shell to tcsh
RUN sudo apt-get install tcsh && \
    chsh -s /bin/tcsh
    # chsh -s /usr/bin/tcsh
SHELL ["/bin/tcsh", "-c"]

## Install CNSsolve (http://cns-online.org/v1.3/)
COPY cns_solve_1.3_all_intel-mac_linux.tar.gz /software/

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
    sed -i s/NUMJOB=24/NUMJOB=$CORES/g local_config_file && \
    ./install.csh local_config_file

## Grant execution permissions to entire dir
RUN sudo chmod -R 777 $home

## Fix Symlink issue to QueueSubmit.py
RUN cd $HOME/haddock/haddock2.4-2021-01/Haddock/Main/ && \
    rm QueueSubmit.py && \
    cp QueueSubmit_concat.py QueueSubmit.py
