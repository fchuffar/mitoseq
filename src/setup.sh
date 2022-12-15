#!/bin/sh

# Organize the working directories and download the reference sequence.
# If any result of these command already exist, it will be skipped.

# Arguments $1, $3, $4 are the reference and ftp link
# Arguments $2, $5 are the expected file name to unzip
# Arguments $4 is to check if you use STAR mapping, in that case, you will need a GTF.

# Creating the working directories.
mkdir -p data/input/reference data/input/samples data/input/gtf data/temp data/output

# Deleting all the .gitignore in input directory.
rm data/input/*/.gitignore 2> /dev/null

# Moving to the input directory.
cd data/input/

# if there is no human genome reference, download and extract it.
if test 0 -eq $(ls reference/*.fna 2> /dev/null | wc -l ) && test 0 -eq $(ls reference/*.fasta 2> /dev/null | wc -l ); then
    echo "Downloading genome of reference..."
    wget "$1" -P reference/ 2> /dev/null
    echo "gunzipping genome of reference..."
    gunzip reference/"$2"
fi

# if there is no michondria reference, download it.
if test 0 -eq $(ls mitochondria/*.fna 2> /dev/null | wc -l) && test 0 -eq $(ls mitochondria/*.fasta 2> /dev/null | wc -l); then
    echo "Downloading mitochondria of reference..."
    efetch -db nuccore -id "$3" -format fasta > mitochondria/mitochondria.fasta
fi

# if you use star mapping and there is no gene reference, download it.
if [ "$6" = True ] && test 0 -eq $(ls gtf/*.gtf 2> /dev/null | wc -l ); then
    echo "Downloading Gene Transfert Format of reference..."
    wget "$4" -P gtf/ 2> /dev/null
    echo "gunzipping Gene Transfert Format of reference..."
    gunzip gtf/"$5"
fi