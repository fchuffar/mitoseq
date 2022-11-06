#!/bin/sh

# Organize the working directories and download the reference sequence.
# If any result of these command already exist, it will be skipped.

# Stop on any error.
set -ue

# Creating the working directories.
mkdir -p data/input/reference data/input/samples data/temp data/output

# Moving to the reference directory.
cd data/input/reference

# if there is no reference file, download it.
if test ! -f ref_mitochondrial.fasta ; then
    efetch -db nuccore -id JQ705953 -format fasta > ref_mitochondrial.fasta
fi
