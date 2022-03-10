# input is complex and subunit and other subunit
#

# first for receptor
for i in $1 $2; do
    # get the atom lines of chain A
    grep "^ATOM" $i | awk 'BEGIN {FS=""} {if ($22 == "A") print}' > tmp
    # get the chain
    grep "CA" tmp | cut -c22 > chain
    # get the residue number and strip white space of it
    grep "CA" tmp | cut -c23-26 | sed '/^$/d;s/[[:blank:]]//g' > resi
    # paste it togeter
    paste -d "" chain resi | sort >  ${i}.tmp
done

# take only common residue numbers and print it in a zone file the awk command
# collapses the sequence into a range. This is especially helpful further on
# with the rzone.
comm -12 ${1}.tmp ${2}.tmp | cut -c2- | sort -n | \
    awk 'NR==1{first=$1;last=$1;next} $1 == last+1 {last=$1;next} {print "zone A"first"-A"last;first=$1;last=first} END{print "zone A"first"-A"last}' > ${2%.*}.lzone

# now do it for ligand
for i in $1 $3; do
    # get the atom lines of chain A
    grep "^ATOM" $i | awk 'BEGIN {FS=""} {if ($22 == "B") print}' > tmp
    # get the chain
    grep "CA" tmp | cut -c22 > chain
    # get the residue number and strip white space of it
    grep "CA" tmp | cut -c23-26 | sed '/^$/d;s/[[:blank:]]//g' > resi
    # paste it togeter
    paste -d "" chain resi | sort >  ${i}.tmp
done

# take only common residue numbers and print it in a zone file
comm -12 ${1}.tmp ${3}.tmp | cut -c2- | sort -n | \
    awk 'NR==1{first=$1;last=$1;next} $1 == last+1 {last=$1;next} {print "rzone B"first"-B"last;first=$1;last=first} END{print "rzone B"first"-B"last}' > ${3%.*}.lzone

# clean up
rm ${1}.tmp ${2}.tmp ${3}.tmp
rm tmp resi chain
