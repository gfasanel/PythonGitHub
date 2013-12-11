#!/bin/sh

# Reading in file with BR combination to creat limit.txt (containing mass, cls for obs, exp and +/- 1 and 2 sig)  for various v* directories
BR="$1"
combinedMode="$2"

count=0

cat ${BR} | while read tw bh bz
do
    
    bz=`printf "%.6f" $bz`
    tw=`printf "%.6f" $tw`
    bh=`printf "%.6f" $bh`

    cat ${combinedMode} | awk -v br1=$bz -v br2=$tw -v br3=$bh -F "[ |:|_|(|)]" 'BEGIN{print "\# limits\n\#\n\# mass observed -2sig -1sig median_exp +1sig +2sig\n\#-------------------------------------------"}{if ($2 ==br1 && $3 == br2 && $4 == br3) {print $1"  "$7"  "$19"  "$10"  "$8"  "$13"  "$16}}' > multileptons_v${count}/limits.txt

    ((count++))



done
