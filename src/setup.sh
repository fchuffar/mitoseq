#!/bin/sh

# Organize the working directories and download the reference sequence.
# If any result of these command already exist, it will be skipped.


# Creating the working directories.
mkdir -p data/input/reference data/input/samples data/input/gtf data/temp data/output

# Deleting all the .gitignore in input directory.
rm data/input/*/.gitignore 2> /dev/null

# Moving to the input directory.
cd data/input/

# if there is no human genome reference, download and extract it.
if test 0 -eq $(ls reference/*.fna 2> /dev/null | wc -l ) && test 0 -eq $(ls reference/*.fasta 2> /dev/null | wc -l ); then
    wget https://ftp.ncbi.nlm.nih.gov/genomes/refseq/vertebrate_mammalian/Homo_sapiens/reference/GCF_000001405.40_GRCh38.p14/GCF_000001405.40_GRCh38.p14_genomic.fna.gz -P reference/
    gunzip reference/GCF_000001405.40_GRCh38.p14_genomic.fna.gz
fi

# if there is no michondria reference, download it.
if test 0 -eq $(ls mitochondria/*.fna 2> /dev/null | wc -l) && test 0 -eq $(ls mitochondria/*.fasta 2> /dev/null | wc -l); then
    efetch -db nuccore -id "$1" -format fasta > mitochondria/mitochondria.fasta
fi


# if you use star mapping and there is no gene reference, download it.
if [ "$2" = True ] && test 0 -eq $(ls gtf/*.gtf 2> /dev/null | wc -l ); then
    wget https://ftp.ncbi.nlm.nih.gov/genomes/refseq/vertebrate_mammalian/Homo_sapiens/reference/GCF_000001405.40_GRCh38.p14/GCF_000001405.40_GRCh38.p14_genomic.gtf.gz -P gtf/
    gunzip gtf/GCF_000001405.40_GRCh38.p14_genomic.gtf.gz
fi