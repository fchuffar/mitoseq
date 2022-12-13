import os
import argparse
from src.utils import haplogroup_count, fuse_haplogroups, haplogroupe_accession

PathToSamples = "data/input/samples/"
PathToRef = "data/input/reference/"
PathToMito = "data/input/mitochondria/"
PathToGtf = "data/input/gtf/"
PathToTempSamples = "data/temp/samples"
PathToTemp = "data/temp/"
PathToOutput = "../data/output/"

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


os.system(f"src/setup.sh {args.reference} {args.star}")

if len(os.listdir(PathToRef)) > 1:
    raise Exception(
        f"Too many references files in {PathToRef} directory, there should only be one"
    )


if os.listdir(PathToRef)[0][-4:] == ".fna":
    os.rename(
        PathToRef + os.listdir(PathToRef)[0],
        PathToRef + os.listdir(PathToRef)[0].replace(".fna", ".fasta"),
    )

referenceName = os.listdir(PathToRef)[0].replace(".fasta", "")


if len(os.listdir(PathToMito)) > 1:
    raise Exception(
        f"Too many references files in {PathToMito} directory, there should only be one"
    )

if os.listdir(PathToMito)[0][-4:] == ".fna":
    os.rename(
        PathToMito + os.listdir(PathToMito)[0],
        PathToMito + os.listdir(PathToMito)[0].replace(".fna", ".fasta"),
    )

data = None
with open(PathToMito + os.listdir(PathToMito)[0], "r+") as file:
    data = file.read()
    if data[1:5] != "chrM":
        data = data.replace(data[1 : data.find(" ")], "chrM")
        file.write(data)
    else:
        data = None

if data != None:
    with open(PathToMito + os.listdir(PathToMito)[0], "w+") as file:
        file.write(data)

mitochondriaName = os.listdir(PathToMito)[0].replace(".fasta", "")
os.system(f"""
          mkdir -p {PathToTemp}mitochondria
          cp -u {PathToMito}{mitochondriaName}.fasta {PathToTemp}mitochondria
        """)

gtfName = None
if args.star == True:
    if len(os.listdir(PathToGtf)) > 1:
        raise Exception(
            f"Too many gtf files in {PathToRef} directory, there should only be one"
        )
    if len(os.listdir(PathToGtf)) == 0:
        raise Exception(
            f"No gtf files found in {PathToRef} directory, you have to add it to use star mapping"
        )
    gtfName = os.listdir(PathToGtf)[0].replace(".gtf", "")
    os.system(f"mkdir -p {PathToTemp}/genomeDir")


## Obtaining a sample list from the files existing in the samples folder
if len(os.listdir(PathToSamples)) == 0:
    raise Exception(f"No file found in {PathToSamples} directory")

files = []
for file in os.listdir(PathToSamples):
    os.rename(
        PathToSamples + file,
        PathToSamples + file.replace(".fq", ".fastq").replace(".fq.gz", ".fastq.gz"),
    )

sample_list = os.listdir(PathToSamples)
ignore_list = []
for file in sample_list:
    if file[-4:] == ".bam" or file[-6:] == ".bam.gz":
        name = file[: file.find(".")]
        os.system(
            f"""
            mkdir -p {PathToTemp}{name}
            cp -u {PathToSamples}{file} {PathToTemp}{name}/{name}.bam
        """
        )
        files.append(f"{PathToOutput}{name}.txt")

    elif file[-6:] == ".fastq" or file[-9:] == ".fastq.gz" and file not in ignore_list:
        if file.find("_R1"):
            if file.replace("_R1", "_R2") in sample_list:
                name = file[: file.find("_R1")]
                ignore_list.append(file.replace("R1", "R2"))
                os.system(f"mkdir -p {PathToTemp}{name}")
                files.append(f"{PathToOutput}{name}.txt")
        elif file.find("_R2"):
            if file.replace("_R2", "_R1") in sample_list:
                name = file[: file.find("_R2")]
                ignore_list.append(file.replace("R2", "R1"))
                os.system(f"mkdir -p {PathToTemp}{name}")
                files.append(f"{PathToOutput}{name}.txt")
        else:
            raise Exception(
                f"Invalid .fastq file in {PathToSamples} directory, this pipeline only work with paired-end and bam"
            )
    elif file not in ignore_list:
        raise Exception(
            f"There seem to be an unwanted file in {PathToSamples} directory"
        )

files = set(files)



# Pipeline execution
prompt = f"cd src ; snakemake --rerun-incomplete --config mitoName={mitochondriaName} star={args.star} keep={args.keep} thread={args.thread} consensus={args.consensus} referenceName={referenceName} gtfName={gtfName} -c {args.core} {' '.join(files)}"
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
