#!/bin/sh

# Organize the working directories and download the reference sequence.
# If any result of these command already exist, it will be skipped.


# Creating the working directories.
mkdir -p data/input/reference data/input/samples data/temp data/output

# Creating the working directories.
rm data/input/reference/.gitignore data/input/samples/.gitignore data/temp/.gitignore data/output/.gitignore 2> /dev/null

# Moving to the reference directory.
cd data/input/reference

# if there is no reference file, download the michondria reference.
if test 0 -eq $(ls | wc -l) ; then
    efetch -db nuccore -id "$1" -format fasta > ref_mitochondrial.fasta
fi
