#!/bin/csh
#
if ($#argv != 1) goto usage

\mv $1/run.cns $1/run.cns-orig
\mv $1/data/new.html $1/data/new.html-orig
\mv $1/data/sequence/file_A.list $1/data/sequence/file_A.list-orig
\mv $1/data/sequence/file_B.list $1/data/sequence/file_B.list-orig


chmod -R +w $1
\cp -r $HADDOCK/examples/barnase-barstar-run-data/run1-water/* $1

set RUNPATH=`echo $PWD | sed -e 's/\//XX/g'`

sed s/USERNAME/$RUNPATH/ $HADDOCK/examples/barnase-barstar-run-data/run1-water/run.cns | sed -e 's/XX/\//g' | sed s/run1-water/$1/ > $1/run.cns
sed s/USERNAME/$RUNPATH/ $HADDOCK/examples/barnase-barstar-run-data/run1-water/data/new.html | sed -e 's/XX/\//g' > $1/data/new.html
sed s/USERNAME/$RUNPATH/ $HADDOCK/examples/barnase-barstar-run-data/run1-water/data/sequence/file_A.list | sed -e 's/XX/\//g' > $1/data/sequence/file_A.list
sed s/USERNAME/$RUNPATH/ $HADDOCK/examples/barnase-barstar-run-data/run1-water/data/sequence/file_B.list | sed -e 's/XX/\//g' > $1/data/sequence/file_B.list

goto exit

usage:

echo "Correct usage is: copy_haddock_files.csh target_run_directory_name"

exit:
