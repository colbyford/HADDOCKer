#!/bin/csh
#
echo '######################################################'
echo '  '
echo '  HADDOCK scoring water'
echo '______________________________________________________'
foreach i ($argv)
  set clufi=$i/structures/it1/water/clusters_haddock-sorted.stat_best4
  if (-e $clufi) then
    echo '===========' $i '============='
    awk '{if ($6-$7<=4) {print "  ",NR-1,$1,$6,$7}}' $clufi | sed -e 's/file\.nam_//'| grep -v "#" >ttmp1
    cat /dev/null >ttmp2
    foreach j (`grep clust ttmp1 |awk '{print $2}'`)
      if (-e $i/structures/it1/water/clusters_best4.fnat) then
        grep $j"\ " $i/structures/it1/water/clusters_best4.fnat >>ttmp2
      endif
    end
    echo 'Rank of clusters with i-RMSD<4A:'
    if (-e $i/structures/it1/water/clusters_best4.fnat) then
      paste ttmp1 ttmp2 |awk '{printf "  %2d %-8s %5.2f +/- %5.2f  Fnat= %5.2f +/- %5.2f\n",$1,$5,$3,$4,$6,$7}'
    else
      cat ttmp1 |awk '{printf "  %2d %-8s %5.2f +/- %5.2f\n",$1,$2,$3,$4}'
    endif
    \rm ttmp1 ttmp2
  endif
end
echo '######################################################'
echo '  '
echo '  HADDOCK scoring it1'
echo '______________________________________________________'
foreach i ($argv)
  set clufi=$i/structures/it1/clusters_haddock-sorted.stat_best4
  if (-e $clufi) then
    echo '===========' $i '============='
    awk '{if ($6-$7<=4) {print "  ",NR-1,$1,$6,$7}}' $clufi | sed -e 's/file\.nam_//'| grep -v "#" >ttmp1
    cat /dev/null >ttmp2
    foreach j (`grep clust ttmp1 |awk '{print $2}'`)
      if (-e $i/structures/it1/clusters_best4.fnat) then
        grep $j"\ " $i/structures/it1/clusters_best4.fnat >>ttmp2
      endif
    end
    echo 'Rank of clusters with i-RMSD<4A:'
    if (-e $i/structures/it1/clusters_best4.fnat) then
      paste ttmp1 ttmp2 |awk '{printf "  %2d %-8s %5.2f +/- %5.2f  Fnat= %5.2f +/- %5.2f\n",$1,$5,$3,$4,$6,$7}'
    else
      cat ttmp1 |awk '{printf "  %2d %-8s %5.2f +/- %5.2f\n",$1,$2,$3,$4}'
    endif
    \rm ttmp1 ttmp2
  endif
end
