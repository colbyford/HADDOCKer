#!/bin/sh 
#
echo Content-type: text/plain
echo

AIR_ACTIVE_1=`echo $QUERY_STRING | awk 'BEGIN{RS="&"} {printf "%s\n",$0}' |grep ACTIVE_1 | awk 'BEGIN{FS="="} {print $2}'| sed -e 's/+/\ /g' -e 's/%2C/\ /g'`
AIR_ACTIVE_2=`echo $QUERY_STRING | awk 'BEGIN{RS="&"} {printf "%s\n",$0}' |grep ACTIVE_2 | awk 'BEGIN{FS="="} {print $2}'| sed -e 's/+/\ /g' -e 's/%2C/\ /g'`
AIR_ACTIVE_3=`echo $QUERY_STRING | awk 'BEGIN{RS="&"} {printf "%s\n",$0}' |grep ACTIVE_3 | awk 'BEGIN{FS="="} {print $2}'| sed -e 's/+/\ /g' -e 's/%2C/\ /g'`
AIR_ACTIVE_4=`echo $QUERY_STRING | awk 'BEGIN{RS="&"} {printf "%s\n",$0}' |grep ACTIVE_4 | awk 'BEGIN{FS="="} {print $2}'| sed -e 's/+/\ /g' -e 's/%2C/\ /g'`
AIR_ACTIVE_5=`echo $QUERY_STRING | awk 'BEGIN{RS="&"} {printf "%s\n",$0}' |grep ACTIVE_5 | awk 'BEGIN{FS="="} {print $2}'| sed -e 's/+/\ /g' -e 's/%2C/\ /g'`
AIR_ACTIVE_6=`echo $QUERY_STRING | awk 'BEGIN{RS="&"} {printf "%s\n",$0}' |grep ACTIVE_6 | awk 'BEGIN{FS="="} {print $2}'| sed -e 's/+/\ /g' -e 's/%2C/\ /g'`

AIR_PASSIVE_1=`echo $QUERY_STRING | awk 'BEGIN{RS="&"} {printf "%s\n",$0}' |grep PASSIVE_1 | awk 'BEGIN{FS="="} {print $2}'| sed -e 's/+/\ /g' -e 's/%2C/\ /g'`
AIR_PASSIVE_2=`echo $QUERY_STRING | awk 'BEGIN{RS="&"} {printf "%s\n",$0}' |grep PASSIVE_2 | awk 'BEGIN{FS="="} {print $2}'| sed -e 's/+/\ /g' -e 's/%2C/\ /g'`
AIR_PASSIVE_3=`echo $QUERY_STRING | awk 'BEGIN{RS="&"} {printf "%s\n",$0}' |grep PASSIVE_3 | awk 'BEGIN{FS="="} {print $2}'| sed -e 's/+/\ /g' -e 's/%2C/\ /g'`
AIR_PASSIVE_4=`echo $QUERY_STRING | awk 'BEGIN{RS="&"} {printf "%s\n",$0}' |grep PASSIVE_4 | awk 'BEGIN{FS="="} {print $2}'| sed -e 's/+/\ /g' -e 's/%2C/\ /g'`
AIR_PASSIVE_5=`echo $QUERY_STRING | awk 'BEGIN{RS="&"} {printf "%s\n",$0}' |grep PASSIVE_5 | awk 'BEGIN{FS="="} {print $2}'| sed -e 's/+/\ /g' -e 's/%2C/\ /g'`
AIR_PASSIVE_6=`echo $QUERY_STRING | awk 'BEGIN{RS="&"} {printf "%s\n",$0}' |grep PASSIVE_6 | awk 'BEGIN{FS="="} {print $2}'| sed -e 's/+/\ /g' -e 's/%2C/\ /g'`

PROT_SEGID_1=`echo $QUERY_STRING | awk 'BEGIN{RS="&"} {printf "%s\n",$0}' |grep SEGID_1 | awk 'BEGIN{FS="="} {print $2}'`
PROT_SEGID_2=`echo $QUERY_STRING | awk 'BEGIN{RS="&"} {printf "%s\n",$0}' |grep SEGID_2 | awk 'BEGIN{FS="="} {print $2}'`
PROT_SEGID_3=`echo $QUERY_STRING | awk 'BEGIN{RS="&"} {printf "%s\n",$0}' |grep SEGID_3 | awk 'BEGIN{FS="="} {print $2}'`
PROT_SEGID_4=`echo $QUERY_STRING | awk 'BEGIN{RS="&"} {printf "%s\n",$0}' |grep SEGID_4 | awk 'BEGIN{FS="="} {print $2}'`
PROT_SEGID_5=`echo $QUERY_STRING | awk 'BEGIN{RS="&"} {printf "%s\n",$0}' |grep SEGID_5 | awk 'BEGIN{FS="="} {print $2}'`
PROT_SEGID_6=`echo $QUERY_STRING | awk 'BEGIN{RS="&"} {printf "%s\n",$0}' |grep SEGID_6 | awk 'BEGIN{FS="="} {print $2}'`

AIR_DIST=`echo $QUERY_STRING | awk 'BEGIN{RS="&"} {printf "%s\n",$0}' |grep AIR_DIST | awk 'BEGIN{FS="="} {print $2}'`

echo '!' 
echo '! HADDOCK AIR restraints for 1st molecule'
echo '!' 

for i in $AIR_ACTIVE_1
do
  echo '!' 
  echo 'assign ( resid '$i ' and segid '$PROT_SEGID_1')'
  echo '       ('
  inum=0
  itot=`echo $AIR_ACTIVE_2 $AIR_ACTIVE_3 $AIR_ACTIVE_4 $AIR_ACTIVE_5 $AIR_ACTIVE_6 $AIR_PASSIVE_2 $AIR_PASSIVE_3 $AIR_PASSIVE_4 $AIR_PASSIVE_5 $AIR_PASSIVE_6 | wc | awk '{print $2}'`
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

  for j in $AIR_ACTIVE_3 $AIR_PASSIVE_3
  do
    inum=`expr $inum + 1`
    echo '        ( resid '$j ' and segid '$PROT_SEGID_3')' 
    if [ $inum != $itot ]
      then
        echo '     or' 
    fi
    if [ $inum = $itot ]
      then
        echo '       ) ' $AIR_DIST $AIR_DIST '0.0'
    fi
  done

  for j in $AIR_ACTIVE_4 $AIR_PASSIVE_4
  do
    inum=`expr $inum + 1`
    echo '        ( resid '$j ' and segid '$PROT_SEGID_4')' 
    if [ $inum != $itot ]
      then
        echo '     or' 
    fi
    if [ $inum = $itot ]
      then
        echo '       ) ' $AIR_DIST $AIR_DIST '0.0'
    fi
  done

  for j in $AIR_ACTIVE_5 $AIR_PASSIVE_5
  do
    inum=`expr $inum + 1`
    echo '        ( resid '$j ' and segid '$PROT_SEGID_5')' 
    if [ $inum != $itot ]
      then
        echo '     or' 
    fi
    if [ $inum = $itot ]
      then
        echo '       ) ' $AIR_DIST $AIR_DIST '0.0'
    fi
  done

  for j in $AIR_ACTIVE_6 $AIR_PASSIVE_6
  do
    inum=`expr $inum + 1`
    echo '        ( resid '$j ' and segid '$PROT_SEGID_6')' 
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
# Now the same for the 2nd molecule
#
echo '!' 
echo '! HADDOCK AIR restraints for 2nd molecule'
echo '!' 
#

for i in $AIR_ACTIVE_2
do
  echo '!' 
  echo 'assign ( resid '$i ' and segid '$PROT_SEGID_2')'
  echo '       ('
  inum=0
  itot=`echo $AIR_ACTIVE_1 $AIR_ACTIVE_3 $AIR_ACTIVE_4 $AIR_ACTIVE_5 $AIR_ACTIVE_6 $AIR_PASSIVE_1 $AIR_PASSIVE_3 $AIR_PASSIVE_4 $AIR_PASSIVE_5 $AIR_PASSIVE_6 | wc | awk '{print $2}'`
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

  for j in $AIR_ACTIVE_3 $AIR_PASSIVE_3
  do
    inum=`expr $inum + 1`
    echo '        ( resid '$j ' and segid '$PROT_SEGID_3')' 
    if [ $inum != $itot ]
      then
        echo '     or' 
    fi
    if [ $inum = $itot ]
      then
        echo '       ) ' $AIR_DIST $AIR_DIST '0.0'
    fi
  done

  for j in $AIR_ACTIVE_4 $AIR_PASSIVE_4
  do
    inum=`expr $inum + 1`
    echo '        ( resid '$j ' and segid '$PROT_SEGID_4')' 
    if [ $inum != $itot ]
      then
        echo '     or' 
    fi
    if [ $inum = $itot ]
      then
        echo '       ) ' $AIR_DIST $AIR_DIST '0.0'
    fi
  done

  for j in $AIR_ACTIVE_5 $AIR_PASSIVE_5
  do
    inum=`expr $inum + 1`
    echo '        ( resid '$j ' and segid '$PROT_SEGID_5')' 
    if [ $inum != $itot ]
      then
        echo '     or' 
    fi
    if [ $inum = $itot ]
      then
        echo '       ) ' $AIR_DIST $AIR_DIST '0.0'
    fi
  done

  for j in $AIR_ACTIVE_6 $AIR_PASSIVE_6
  do
    inum=`expr $inum + 1`
    echo '        ( resid '$j ' and segid '$PROT_SEGID_6')' 
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
# Now the same for the 3rd molecule
#
echo '!' 
echo '! HADDOCK AIR restraints for 3rd molecule'
echo '!' 

for i in $AIR_ACTIVE_3
do
  echo '!' 
  echo 'assign ( resid '$i ' and segid '$PROT_SEGID_3')'
  echo '       ('
  inum=0
  itot=`echo $AIR_ACTIVE_1 $AIR_ACTIVE_2 $AIR_ACTIVE_4 $AIR_ACTIVE_5 $AIR_ACTIVE_6 $AIR_PASSIVE_1 $AIR_PASSIVE_2 $AIR_PASSIVE_4 $AIR_PASSIVE_5 $AIR_PASSIVE_6 | wc | awk '{print $2}'`
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

  for j in $AIR_ACTIVE_4 $AIR_PASSIVE_4
  do
    inum=`expr $inum + 1`
    echo '        ( resid '$j ' and segid '$PROT_SEGID_4')' 
    if [ $inum != $itot ]
      then
        echo '     or' 
    fi
    if [ $inum = $itot ]
      then
        echo '       ) ' $AIR_DIST $AIR_DIST '0.0'
    fi
  done

  for j in $AIR_ACTIVE_5 $AIR_PASSIVE_5
  do
    inum=`expr $inum + 1`
    echo '        ( resid '$j ' and segid '$PROT_SEGID_5')' 
    if [ $inum != $itot ]
      then
        echo '     or' 
    fi
    if [ $inum = $itot ]
      then
        echo '       ) ' $AIR_DIST $AIR_DIST '0.0'
    fi
  done

  for j in $AIR_ACTIVE_6 $AIR_PASSIVE_6
  do
    inum=`expr $inum + 1`
    echo '        ( resid '$j ' and segid '$PROT_SEGID_6')' 
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
# Now the same for the 4th molecule
#
echo '!' 
echo '! HADDOCK AIR restraints for 4th molecule'
echo '!' 

for i in $AIR_ACTIVE_4
do
  echo '!' 
  echo 'assign ( resid '$i ' and segid '$PROT_SEGID_4')'
  echo '       ('
  inum=0
  itot=`echo $AIR_ACTIVE_1 $AIR_ACTIVE_2 $AIR_ACTIVE_3 $AIR_ACTIVE_5 $AIR_ACTIVE_6 $AIR_PASSIVE_1 $AIR_PASSIVE_2 $AIR_PASSIVE_3 $AIR_PASSIVE_5 $AIR_PASSIVE_6 | wc | awk '{print $2}'`
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

  for j in $AIR_ACTIVE_3 $AIR_PASSIVE_3
  do
    inum=`expr $inum + 1`
    echo '        ( resid '$j ' and segid '$PROT_SEGID_3')' 
    if [ $inum != $itot ]
      then
        echo '     or' 
    fi
    if [ $inum = $itot ]
      then
        echo '       ) ' $AIR_DIST $AIR_DIST '0.0'
    fi
  done

  for j in $AIR_ACTIVE_5 $AIR_PASSIVE_5
  do
    inum=`expr $inum + 1`
    echo '        ( resid '$j ' and segid '$PROT_SEGID_5')' 
    if [ $inum != $itot ]
      then
        echo '     or' 
    fi
    if [ $inum = $itot ]
      then
        echo '       ) ' $AIR_DIST $AIR_DIST '0.0'
    fi
  done

  for j in $AIR_ACTIVE_6 $AIR_PASSIVE_6
  do
    inum=`expr $inum + 1`
    echo '        ( resid '$j ' and segid '$PROT_SEGID_6')' 
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
# Now the same for the 5th molecule
#
echo '!' 
echo '! HADDOCK AIR restraints for 5th molecule'
echo '!' 

for i in $AIR_ACTIVE_5
do
  echo '!' 
  echo 'assign ( resid '$i ' and segid '$PROT_SEGID_5')'
  echo '       ('
  inum=0
  itot=`echo $AIR_ACTIVE_1 $AIR_ACTIVE_2 $AIR_ACTIVE_3 $AIR_ACTIVE_4 $AIR_ACTIVE_6 $AIR_PASSIVE_1 $AIR_PASSIVE_2 $AIR_PASSIVE_3 $AIR_PASSIVE_4 $AIR_PASSIVE_6 | wc | awk '{print $2}'`
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

  for j in $AIR_ACTIVE_3 $AIR_PASSIVE_3
  do
    inum=`expr $inum + 1`
    echo '        ( resid '$j ' and segid '$PROT_SEGID_3')' 
    if [ $inum != $itot ]
      then
        echo '     or' 
    fi
    if [ $inum = $itot ]
      then
        echo '       ) ' $AIR_DIST $AIR_DIST '0.0'
    fi
  done

  for j in $AIR_ACTIVE_4 $AIR_PASSIVE_4
  do
    inum=`expr $inum + 1`
    echo '        ( resid '$j ' and segid '$PROT_SEGID_4')' 
    if [ $inum != $itot ]
      then
        echo '     or' 
    fi
    if [ $inum = $itot ]
      then
        echo '       ) ' $AIR_DIST $AIR_DIST '0.0'
    fi
  done

  for j in $AIR_ACTIVE_6 $AIR_PASSIVE_6
  do
    inum=`expr $inum + 1`
    echo '        ( resid '$j ' and segid '$PROT_SEGID_6')' 
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
# Now the same for the 6th molecule
#
echo '!' 
echo '! HADDOCK AIR restraints for 6th molecule'
echo '!' 

for i in $AIR_ACTIVE_6
do
  echo '!' 
  echo 'assign ( resid '$i ' and segid '$PROT_SEGID_6')'
  echo '       ('
  inum=0
  itot=`echo $AIR_ACTIVE_1 $AIR_ACTIVE_2 $AIR_ACTIVE_3 $AIR_ACTIVE_4 $AIR_ACTIVE_5 $AIR_PASSIVE_1 $AIR_PASSIVE_2 $AIR_PASSIVE_3 $AIR_PASSIVE_4 $AIR_PASSIVE_5 | wc | awk '{print $2}'`
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

  for j in $AIR_ACTIVE_3 $AIR_PASSIVE_3
  do
    inum=`expr $inum + 1`
    echo '        ( resid '$j ' and segid '$PROT_SEGID_3')' 
    if [ $inum != $itot ]
      then
        echo '     or' 
    fi
    if [ $inum = $itot ]
      then
        echo '       ) ' $AIR_DIST $AIR_DIST '0.0'
    fi
  done

  for j in $AIR_ACTIVE_4 $AIR_PASSIVE_4
  do
    inum=`expr $inum + 1`
    echo '        ( resid '$j ' and segid '$PROT_SEGID_4')' 
    if [ $inum != $itot ]
      then
        echo '     or' 
    fi
    if [ $inum = $itot ]
      then
        echo '       ) ' $AIR_DIST $AIR_DIST '0.0'
    fi
  done

  for j in $AIR_ACTIVE_5 $AIR_PASSIVE_5
  do
    inum=`expr $inum + 1`
    echo '        ( resid '$j ' and segid '$PROT_SEGID_5')' 
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

