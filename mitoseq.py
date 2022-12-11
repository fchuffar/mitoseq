import os
import argparse
from src.utils import haplogroup_count, fuse_haplogroups, haplogroupe_accession

PathToRaw = "data/input/samples/"
PathToRef = "data/input/reference/"
PathToGtf = "data/input/gtf/"
PathToTempSamples = "data/temp/samples"
PathToTemp = "data/temp/"

parser = argparse.ArgumentParser(description="Every argument is optional")
parser.add_argument(
    "-k",
    "--keep",
    action="store_true",
    help="Choose if you keep the Temporary files (default=False)",
    default=False,
)
parser.add_argument(
    "-c",
    "--core",
    type=int,
    help="Choose the number of core to be used for snakemake (default=4)",
    default=4,
)
parser.add_argument(
    "-t",
    "--thread",
    type=int,
    help="Choose the number of thread to be used for commands inside of snakemake (default=4)",
    default=4,
)
parser.add_argument(
    "-b",
    "--bank",
    type=str,
    help='Enter the bank file with all haplogroups (default="src/web_data/genbank_haplogroup_count.csv")',
    default="src/web_data/genbank_haplogroup_count.csv",
)
parser.add_argument(
    "-n",
    "--num",
    type=int,
    help="Enter the minimum count to accept an haplogroup (default=0)",
    default=0,
)
parser.add_argument(
    "-u",
    "--tree",
    type=str,
    help='Enter the tree file which link haplogroup to accession number (default="src/web_data/phylotree.txt")',
    default="src/web_data/phylotree.txt",
)
parser.add_argument(
    "-r",
    "--reference",
    type=str,
    help='Enter the reference accession number, the default one point to the mitochondria reference (default="JQ705953")',
    default="NC_012920.1",
)
parser.add_argument(
    "-s",
    "--consensus",
    action="store_true",
    help="Use consensus method for haplogrep (default=False)",
    default=False,
)
parser.add_argument(
    "-a",
    "--star",
    action="store_true",
    help="Use STAR for mapping (default=False)",
    default=False,
)
args = parser.parse_args()


os.system(f"src/setup.sh {args.reference}")

if len(os.listdir(PathToRef)) > 1:
    raise Exception(
        f"Too many references files in {PathToRef} directory, there should only be one"
    )

referenceName = os.listdir(PathToRef)[0].replace(".fasta", "")

gtfName = None
if args.star == True:
    if len(os.listdir(PathToGtf)) > 1:
        raise Exception(
            f"Too many gtf files in {PathToRef} directory, there should only be one"
        )
    if len(os.listdir(PathToGtf)) == 0:
        raise Exception(
            f"No gtf files found in {PathToRef} directory, you have to add it"
        )
    gtfName = os.listdir(PathToGtf)[0].replace(".gtf", "")
    os.system(f"mkdir -p {PathToTemp}/genomeDir")

## Obtaining a sample list from the files existing in the samples folder
if len(os.listdir(PathToRaw)) == 0:
    raise Exception(f"No file found in {PathToRaw} directory")
'''
if len(os.listdir(PathToRaw)) % 2 == 1:
    raise Exception(
        "This pipeline is for paired end alignment only, make sure you have put paired end reads"
    )
'''
os.system(f"ls {PathToRaw} > {PathToTempSamples}.txt")


with open(f"{PathToTempSamples}.txt", "r", encoding="utf-8") as file:
    files = file.readlines()
    files = files[::2]
os.system(f"rm {PathToTempSamples}.txt")


samples_list = []
for line in files:
    if line.find(".bam") != -1:
        sample = line[: line.find("_")]
        os.system(f"mkdir -p data/temp/{sample}")
        origin = PathToRaw + line.replace("\n", '')
        samples_list.append(f"../data/output/{sample}.txt")
        os.system(f"cp -u {origin} data/temp/{sample}/{sample}.sorted.bam")
    elif line.find("_R1.f") != -1:
        sample = line[: line.find("_R1.f")]
        samples_list.append(f"../data/output/{sample}.txt")
        os.system(f"mkdir -p data/temp/{sample}")
    else:
        continue
        # raise TypeError(f"The {line} doesn't seem to be a .fastq or a .bam file")
os.system(f"mkdir -p data/temp/reference")



##Pipeline execution
prompt = f"cd src ; snakemake --rerun-incomplete --config star={args.star} keep={args.keep} thread={args.thread} consensus={args.consensus} referenceName={referenceName} gtfName={gtfName} -c {args.core} {' '.join(samples_list)}"
os.system(prompt)

if not args.keep:
    os.system("rm -rf data/temp/ 2> /dev/null")


fuse_haplogroups()

"""
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
os.system("column -t data/output/haplogroups.txt")
