import os
import argparse
from src.utils import haplogroup_count, fuse_haplogroups, haplogroupe_accession

PathToRaw = "data/input/samples/"
PathToTempSamples = "data/temp/samples"

parser = argparse.ArgumentParser(description="test")
parser.add_argument(
    "-c",
    "--core",
    type=int,
    help="Choose the number of core to be used for snakemake",
    default=4,
)
parser.add_argument(
    "-k",
    "--keep",
    type=bool,
    help="Choose if you keep the Temporary files",
    default=0,
)
parser.add_argument(
    "-t",
    "--thread",
    type=int,
    help="Choose the number of thread to be used for commands inside of snakemake",
    default=4,
)
parser.add_argument(
    "-b",
    "--bank",
    type=str,
    help="Enter the bank file with all haplogroups",
    default="src/web_data/genbank_haplogroup_count.csv",
)
parser.add_argument(
    "-n",
    "--num",
    type=int,
    help="Enter the minimum count to accept an haplogroup",
    default=0,
)
parser.add_argument(
    "-u",
    "--tree",
    type=str,
    help="Enter the tree file which link haplogroup to accession number",
    default="src/web_data/phylotree.txt",
)
args = parser.parse_args()


os.system("src/setup.sh")

## Obtaining a sample list from the files existing in the samples folder
if len(os.listdir(PathToRaw)) == 0:
    raise Exception("No file found in sample directory")
if (
    len(os.listdir(PathToRaw)) != 0
    and len(os.listdir(PathToRaw)) % 2 != 1
):
    os.system(f"ls {PathToRaw} > {PathToTempSamples}.txt")
elif len(os.listdir(PathToRaw)) % 2 != 1:
    raise Exception(
        "This pipeline is for paired end alignment only, make sure you have put paired end reads"
    )
else:
    raise FileExistsError(f"The {PathToRaw} folder is empty")

with open(f"{PathToTempSamples}.txt", "r", encoding="utf-8") as file:
    files = file.readlines()
    files = files[::2]
os.system(f"rm {PathToTempSamples}.txt")


samples_list = []
for line in files:
    if ".fastq.gz" in line:
        sample = line.replace("_R1.fastq.gz\n", "")
        samples_list.append(sample)
    elif ".fastq" in line:
        sample = line.replace("_R1.fastq\n", "")
        samples_list.append(sample)
    else:
        raise TypeError(f"The {line} doesn't seem to be a .fastq file")
print(samples_list)


##Pipeline execution
for sample in samples_list:
    prompt = f"cd src ; snakemake -c {args.core} ../data/temp/{sample}.bam --config thread={args.thread}"
    os.system(prompt)
    if not args.keep:
        os.system("rm data/temp/*")

"""
fuse_haplogroups()
haplogroups = haplogroup_count("haplogroups.txt", args.num, args.bank)
print(haplogroups)
for haplogroup in haplogroups:

    access = haplogroupe_accession(args.tree, haplogroup[2])
    if access == None:
        print(f"No sequence for haplogroup {haplogroup[2]}")
    else:
        os.system(
            f"efetch -db nuccore -id {access} -format fasta > data/output/{haplogroup[1]}.fasta"
        )
"""