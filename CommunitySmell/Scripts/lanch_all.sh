#!/usr/bin/bash

directory="conf/"

# bash check if directory exists
if [ -d $directory ]; then
	echo "conf Directory exists"

    # bash for loop
    for f in $( ls $directory ); do
        echo "Launch community smell analisys for conf/$f"
        echo
        Rscript R/automate_community_smell_calculate.R -c conf/$f
        echo
        echo "END"
        echo
    done

    "END all the analysis..."
    
else 
	echo "Directory does not exist"
fi