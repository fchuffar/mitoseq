# A module useful for a fast and easy way to access functionalities of the system
from os import system


# A module for writing easily an user-friendly command-line interfaces
from argparse import ArgumentParser



from src.utils import (
    prepareRef,
    prepareMito,
    prepareGtf,
    prepareSamples,
    fuse_haplogroups,
)  # These are all the functions coming from utils.py

PathToRef = "data/input/reference/"
PathToMito = "data/input/mitochondria/"
PathToGtf = "data/input/gtf/"
PathToSamples = "data/input/samples/"
PathToTemp = "data/temp/"
PathToOutput = "../data/output/"

# Create a class object that will be used to group every arguments and options
parser = ArgumentParser(description="Every argument is optional but, in recommendation, you should at least precise the keep, core, thread, chrM arguments")


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
parser.add_argument(
    "-e",
    "--consensus",
    action="store_true",
    help="Use consensus method for haplogrep (default=False)",
    default=False,
)
parser.add_argument(
    "-s",
    "--star",
    action="store_true",
    help="Use STAR for mapping (default=False)",
    default=False,
)

# Parse the arguments and put them into a dictionary for fast and easy access
args = parser.parse_args()


system(
    f"""src/setup.sh {args.genref} \
          {args.genref[args.genref.rfind('/') + 1:]} \
          {args.mitoref} \
          {args.gtfref} \
          {args.gtfref[args.gtfref.rfind('/') + 1:]} \
          {args.star}"""
)

referenceName = prepareRef(PathToRef, PathToTemp)

mitochondriaName = prepareMito(PathToMito, PathToTemp, args.chrMName)

gtfName = prepareGtf(PathToGtf, PathToRef, PathToTemp, args.star)

files = prepareSamples(PathToSamples, PathToTemp, PathToOutput)


# Pipeline execution
prompt = f"""cd src ; \
    snakemake --rerun-incomplete \
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

system(prompt)

# At the end of the pipeline, delete temp file if you don't want to keep it
if not args.keep:
    system("rm -rf data/temp/ 2> /dev/null")


fuse_haplogroups()

system("column -t data/output/haplogroups.txt")
