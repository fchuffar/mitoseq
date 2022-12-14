import os
import argparse
from src.utils import (
    haplogroup_count,
    fuse_haplogroups,
    haplogroupe_accession,
    prepareRef,
    prepareMito,
    prepareGtf,
    prepareSamples,
)

PathToRef = "data/input/reference/"
PathToMito = "data/input/mitochondria/"
PathToGtf = "data/input/gtf/"
PathToSamples = "data/input/samples/"
PathToTemp = "data/temp/"
PathToOutput = "../data/output/"

parser = argparse.ArgumentParser(description="Every argument is optional")

parser.add_argument(
    "-k",
    "--keep",
    action="store_true",
    help="Choose if you're wishing to keep the Temporary files (default=False)",
    default=False,
)
parser.add_argument(
    "-c",
    "--core",
    type=int,
    help="Give the number of core to be used for snakemake (default=4)",
    default=4,
)
parser.add_argument(
    "-t",
    "--thread",
    type=int,
    help="Give the number of thread to be used for commands inside of snakemake (default=4)",
    default=4,
)
parser.add_argument(
    "-r",
    "--genref",
    type=str,
    help="Enter the ftp download link for the complete genome (default is Homo Sapiens GRCh38.p14)",
    default="https://ftp.ncbi.nlm.nih.gov/genomes/refseq/vertebrate_mammalian/Homo_sapiens/reference/GCF_000001405.40_GRCh38.p14/GCF_000001405.40_GRCh38.p14_genomic.fna.gz",
)
parser.add_argument(
    "-m",
    "--mitoref",
    type=str,
    help='Enter the reference accession number for the mitochondria (default is Homo Sapiens GRCh38.p14 mitochondria : "NC_012920.1")',
    default="NC_012920.1",
)
parser.add_argument(
    "-g",
    "--gtfref",
    type=str,
    help="Enter the ftp download link for the Gene Transfert Format (default is Homo Sapiens GRCh38.p14 GTF)",
    default="https://ftp.ncbi.nlm.nih.gov/genomes/refseq/vertebrate_mammalian/Homo_sapiens/reference/GCF_000001405.40_GRCh38.p14/GCF_000001405.40_GRCh38.p14_genomic.gtf.gz",
)
parser.add_argument(
    "-n",
    "--chrMName",
    type=str,
    help="To keep compatibilities for extracting the Mitochondrial chromosome, enter the name of the chrM contig of the reference sequence",
    default="NC_012920.1",
)

"""
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
"""
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


os.system(
    f"""src/setup.sh {args.genref} \
          {args.genref[args.genref.rfind('/') + 1:]} \
          {args.mitoref} \
          {args.gtfref} \
          {args.gtfref[args.gtfref.rfind('/') + 1:]} \
          {args.star}"""
)

referenceName = prepareRef(PathToRef, PathToTemp)

mitochondriaName = prepareMito(PathToMito, PathToTemp, args.star, args.chrMName)

gtfName = prepareGtf(PathToGtf, PathToRef, PathToTemp, args.star)

files = prepareSamples(PathToSamples, PathToTemp, PathToOutput)


# Pipeline execution
prompt = f"""cd src ; \
    snakemake --rerun-incomplete \
    -n \
    -c {args.core} \
    {' '.join(files)} \
    --config mitoName={mitochondriaName} \
    mito_Name={args.chrMName} \
    star={args.star} \
    keep={args.keep} \
    thread={args.thread} \
    consensus={args.consensus} \
    referenceName={referenceName} \
    gtfName={gtfName}"""

os.system(prompt)

# At the end of the pipeline, delete temp file if you don't want to keep it
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
