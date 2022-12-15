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
)  # These are all the functions used from utils.py

PathToRef = "data/input/reference/"
PathToMito = "data/input/mitochondria/"
PathToGtf = "data/input/gtf/"
PathToSamples = "data/input/samples/"
PathToTemp = "data/temp/"
PathToOutput = "../data/output/"

# Create a class object that will be used to group every arguments and options
parser = ArgumentParser(
    description="Every argument is optional but, in recommendation, you should at least precise the keep, core, thread, chrM arguments"
)

# Here are all the possibles arguments
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

# Launch the src/setup.sh with the needed arguments, please read the documentation inside of it
system(
    f"""src/setup.sh {args.genref} \
          {args.genref[args.genref.rfind('/') + 1:]} \
          {args.mitoref} \
          {args.gtfref} \
          {args.gtfref[args.gtfref.rfind('/') + 1:]} \
          {args.star}"""
)

# Prepare the renference file for the pipeline
referenceName = prepareRef(PathToRef, PathToTemp)

# Prepare the mitochondria reference file for the pipeline
mitochondriaName = prepareMito(PathToMito, PathToTemp, args.chrMName)

# Prepare the Gene Transfert Format file for the pipeline
gtfName = prepareGtf(PathToGtf, PathToRef, PathToTemp, args.star)

# Will get all the samples names to pass it into the pipeline
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

# Execute the program
system(prompt)

# At the end of the pipeline, delete temp file if you don't want to keep it
if not args.keep:
    system("rm -rf data/temp/ 2> /dev/null")

# Will merge the differents haplogrep results, found in the output folder, into haplogroups.txt
fuse_haplogroups()

# Give the resulting haplogroups as a formated output in the standard output
system("column -t data/output/haplogroups.txt")
