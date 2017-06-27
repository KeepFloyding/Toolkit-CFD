#!/bin/bash
#! =======================================================
#! GENERATE ALL FILES NEEDED FOR FLUENT SIMULATION.
#! Input:
#!	- file name
#!	- sim_config_file.py (contains detail about the simulation)
#! Outputs:
#!	- .cas and .dat files (named after file_name)
#!	- .input file for Fluent run (named after file_name)
#!	- .csh file to submit to cluster (named after name of main folder)
#! Extra Info:
#!	- Simulation details can be found in sim_config_file.py
#!
#! Created by Andris Piebalgs on 15/12/2016
#! =======================================================

#! -------------------------------------------------------
#! INPUTS (note that all the simulation inputs are provided in the sim_config file) 
#! -------------------------------------------------------

#! Input, give file name (case/data files and input/output names; this is then assigned to hthe )

file_name=trial2

export file_name

#! -------------------------------------------------------
#! CREATING ALL THE NECESSARY FOLDERS
#! -------------------------------------------------------

cd ..

if [ ! -d "input" ]; then
	mkdir input
fi

if [ ! -d "output" ]; then
	mkdir output
fi

if [ ! -d "results" ]; then
	mkdir results
fi

cd caseGeneration

#! -------------------------------------------------------
#! ALTER C FILES TO ENSURE THAT THE NAME OF THE PARTS IS ACCOUNTED FOR
#! -------------------------------------------------------

python replaceTextMacro.py

#! -------------------------------------------------------
#! GENERATE JOURNAL FILE VIA PYTHON 
#! -------------------------------------------------------

python << END

from createFluentTextNew import generateCaseFile

generateCaseFile();

END

#! -------------------------------------------------------
#! GENERATING CASE FILES 
#! -------------------------------------------------------

#! Removing any old libraries
rm -r libudf*

#! Generating the case file
/usr/local/ansys_inc/v150/fluent/bin/fluent 3ddp -t8 -ssh -g < "$file_name.jou" >& "$file_name.error"

#! -------------------------------------------------------
#! CLEANING UP
#! -------------------------------------------------------

rm -r cleanup*

#! -------------------------------------------------------
#! GENERATING INPUT (SIMULATION RUN DETAILS)
#! -------------------------------------------------------

cd ..

echo "file/read-case caseGeneration/$file_name.cas
file/read-data caseGeneration/$file_name.dat
define/user-defined/execute-on-demand \"variable_initialization::libudf\"
solve/set/time-step 1e-2
file/auto-save/data-frequency 5000
solve/dual-time-iterate 1000000 100
file/write-case-data final$file_name.cas
file/confirm-overwrite yes
exit
yes" > input/"$file_name.input"

#! -------------------------------------------------------
#! GENERATING CLUSTER SUBMISSION FILE (CLUSTER DETAILS)
#! -------------------------------------------------------

#! Finding the name of the current folder
csh_name=$(pwd | grep -o '[^/]*$')
export csh_name


echo "#! /bin/csh
#
#$ -cwd
#$ -j y -o "$file_name.log"
#$ -pe smp 8-24
#



/usr/local/ansys_inc/v150/fluent/bin/fluent 3ddp -t\$NSLOTS -ssh -g < input/"$file_name.input" >& output/"$file_name.output"
" > "$csh_name.csh"


cd caseGeneration

#! -------------------------------------------------------
#! END OF FILE
#! -------------------------------------------------------
