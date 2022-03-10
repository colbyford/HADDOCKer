#!/bin/csh
#
if ($#argv != 1) then
  goto usage
endif
source $1

set CNSEXEC=`echo $CNSTMP |sed -e 's/\//\\\//g'`
set QUEUECOM=`echo $QUEUETMP |sed -e 's/\//\\\//g'`
echo " "

set ROOT=`pwd |sed -e 's/\//\\\//g'`

# setup HADDOCK2.4
sed "s/HCLOUD/$ROOT/" haddock_configure.csh-conf >haddock_configure.csh
sed "s/HCLOUD/$ROOT/" haddock_configure.sh-conf >haddock_configure.sh
chmod +x haddock_configure.csh haddock_configure.sh
cat protocols/run.cns-conf | sed "s/HCLOUD/$ROOT/" | sed "s/CNSEXEC/$CNSEXEC/" | sed "s/QUEUECOM/$QUEUECOM/" | sed "s/NUMJOB/$NUMJOB/" >protocols/run.cns

# setup QueueSubmit script
echo "Setting up QueueSubmit to " $QUEUESUB
cd Haddock/Main
if ( -e QueueSubmit.py ) then
  \rm QueueSubmit.py
endif
ln -s `echo $QUEUESUB` QueueSubmit.py
cd ../../

# initialising example and test files
git submodule init
git submodule update

# compile utilities
echo "Now compiling HADDOCK utilities"
make

echo  " "
echo  "HADDOCK2.4 configured"
echo  "to use it source first haddock_configure.csh/sh"
echo  " "
echo  "edit those two files to define the location of auxiliary software like profit"
goto exit

usage:
echo "./install.csh <config-file>"
echo " "
echo "where the config file contains the info about"
echo " - the location of the cns executable"
echo " - the submission command to execute jobs"
echo " - the number of concurrent jobs to exectue"
echo " "
echo " e.g."
echo 'set CNSTMP=/home/software/science/cns/cns_solve_1.31-UU/intel-x86_64bit-linux/bin/cns"'
echo 'set QUEUETMP="ssub short"'
echo 'set NUMJOB=400'

exit:
