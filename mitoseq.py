import os
import argparse
from function import haplogroup_count, fuse_haplogroups

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
    metavar="bank",
    type=str,
    help="enter the bank file with all haplogroups",
    default="genbank_haplogroup_count.csv",
)
parser.add_argument(
    "-n",
    "--num",
    metavar="num",
    type=int,
    help="enter the minimum count to accept an haplogroup",
    default=0,
)
args = parser.parse_args()

## Obtaining a sample list from the files existing in the samples folder
if (
    len(os.listdir("Data/Input/Samples")) != 0
    and len(os.listdir("Data/Input/Samples")) % 2 != 1
):
    os.system("ls Data/Input/Samples > Data/Temp/Samples.txt")
elif len(os.listdir("Data/Input/Samples")) % 2 != 1:
    raise BrokenPipeError(
        "This pipeline is for paired end alignment only, make sure you have put paired end reads"
    )
else:
    raise FileExistsError("The Data/Input/Samples folder is empty")
f = open("Data/Temp/Samples.txt")
files = f.readlines()
files = files[::2]
f.close()
os.system("rm Data/Temp/Samples.txt")


samples_list = []
for line in files:
    if ".fastq" in line:
        sample = line.replace("_R1.fastq\n", "")
        samples_list.append(sample)
    else:
        raise TypeError(f"The {line} doesn't seem to be a .fastq file")
print(samples_list)

##Pipeline execution
for sample in samples_list:
    prompt = f"snakemake -c {args.core} Data/Output/{sample}.vcf --config thread={args.thread}"
    os.system(prompt)
    if not args.keep:
        os.system("rm Data/Temp/*")

fuse_haplogroups()
print(haplogroup_count("haplogroups.txt", args.num, args.bank))
