#!/bin/sh 
#
echo Content-type: text/plain
echo

AIR_ACTIVE_1=`echo $QUERY_STRING | awk 'BEGIN{RS="&"} {printf "%s\n",$0}' |grep ACTIVE_1 | awk 'BEGIN{FS="="} {print $2}'| sed -e 's/+/\ /g' -e 's/%2C/\ /g'`
AIR_ACTIVE_2=`echo $QUERY_STRING | awk 'BEGIN{RS="&"} {printf "%s\n",$0}' |grep ACTIVE_2 | awk 'BEGIN{FS="="} {print $2}'| sed -e 's/+/\ /g' -e 's/%2C/\ /g'`

AIR_PASSIVE_1=`echo $QUERY_STRING | awk 'BEGIN{RS="&"} {printf "%s\n",$0}' |grep PASSIVE_1 | awk 'BEGIN{FS="="} {print $2}'| sed -e 's/+/\ /g' -e 's/%2C/\ /g'`
AIR_PASSIVE_2=`echo $QUERY_STRING | awk 'BEGIN{RS="&"} {printf "%s\n",$0}' |grep PASSIVE_2 | awk 'BEGIN{FS="="} {print $2}'| sed -e 's/+/\ /g' -e 's/%2C/\ /g'`

PROT_SEGID_1=`echo $QUERY_STRING | awk 'BEGIN{RS="&"} {printf "%s\n",$0}' |grep SEGID_1 | awk 'BEGIN{FS="="} {print $2}'`
PROT_SEGID_2=`echo $QUERY_STRING | awk 'BEGIN{RS="&"} {printf "%s\n",$0}' |grep SEGID_2 | awk 'BEGIN{FS="="} {print $2}'`

AIR_DIST=`echo $QUERY_STRING | awk 'BEGIN{RS="&"} {printf "%s\n",$0}' |grep AIR_DIST | awk 'BEGIN{FS="="} {print $2}'`

echo '! HADDOCK AIR restraints for 1st partner'

for i in $AIR_ACTIVE_1
do
  echo '!' 
  echo 'assign ( resid '$i ' and segid '$PROT_SEGID_1')'
  echo '       ('
  inum=0
  itot=`echo $AIR_ACTIVE_2 $AIR_PASSIVE_2 | wc | awk '{print $2}'`
  for j in $AIR_ACTIVE_2 $AIR_PASSIVE_2 
  do
    inum=`expr $inum + 1`
    echo '        ( resid '$j ' and segid '$PROT_SEGID_2')' 
    if [ $inum != $itot ]
      then
        echo '     or' 
    fi
    if [ $inum = $itot ]
      then
        echo '       ) ' $AIR_DIST $AIR_DIST '0.0'
    fi
  done
    
done
#
# Now the same for the 2nd partner
#
echo '!' 
echo '! HADDOCK AIR restraints for 2nd partner'

for i in $AIR_ACTIVE_2
do
  echo '!'
  echo 'assign ( resid '$i ' and segid '$PROT_SEGID_2')'
  echo '       ('
  inum=0
  itot=`echo $AIR_ACTIVE_1 $AIR_PASSIVE_1 | wc | awk '{print $2}'`
  for j in $AIR_ACTIVE_1 $AIR_PASSIVE_1 
  do
    inum=`expr $inum + 1`
    echo '        ( resid '$j ' and segid '$PROT_SEGID_1')' 
    if [ $inum != $itot ]
      then
	echo '     or' 
    fi
    if [ $inum = $itot ]
      then
	echo '       ) ' $AIR_DIST $AIR_DIST '0.0'
    fi
  done
    
done

