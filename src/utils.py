# A module useful for a fast and easy way to access functionalities of the system
from os import listdir, system, rename


def fuse_haplogroups() -> None:
    """
    From the data/output, get all the results haplogrep files from all samples and merge them into one file: haplogroups.txt
    Will great a new column with the name of the origin file.
    """
    with open("data/output/haplogroups.txt", "w", encoding="utf-8") as output_file:
        output_file.write(
            '"SampleID"	"Haplogroup"	"Rank"	"Quality"	"Range"	"Origin_Filename"\n'
        )
        for file in listdir("data/output/"):
            with open(f"data/output/{file}", encoding="utf-8") as input_file:
                for line in input_file.readlines()[1:]:
                    output_file.write(line.replace("\n", "") + f"  {file}\n")


def prepareRef(PathToRef: str, PathToTemp: str) -> str:
    """
    Prepare the reference file for the pipeline
    Will first check if there is one reference genome
    Then will convert possible alternative fasta format: .fna into .fasta in order to make snakemake easier to use
    Will get the reference name without its extension to pass it into snakemake
    Will make a copy of reference into temp/reference to not overwrite the original
    """
    if len(listdir(PathToRef)) > 1:
        raise Exception(
            f"Too many references files in {PathToRef} directory, there should only be one"
        )

    elif len(listdir(PathToRef)) == 0:
        raise Exception(
            f"No reference file found in {PathToRef} directory, there be one"
        )

    if listdir(PathToRef)[0][-4:] == ".fna":
        rename(
            PathToRef + listdir(PathToRef)[0],
            PathToRef + listdir(PathToRef)[0].replace(".fna", ".fasta"),
        )

    referenceName = listdir(PathToRef)[0].replace(".fasta", "")
    system(
        f"""
            mkdir -p {PathToTemp}reference
            cp -u {PathToRef}{referenceName}.fasta {PathToTemp}reference
            """
    )

    return referenceName


def prepareMito(PathToMito: str, PathToTemp: str, chrMName: str) -> str:
    """
    Prepare the mitochondrial reference file for the pipeline
    Will first check if there is one reference genome
    Then will convert possible alternative fasta format: .fna into .fasta in order to make snakemake easier to use
    Will convert the mitochondrial contig name into the same as the reference genome for compatibility reasons (--chrMName argument)
    Will get the reference name without its extension to pass it into snakemake
    Will make a copy of mitochondrial reference into temp/mitochondria to not overwrite the original
    """
    if len(listdir(PathToMito)) > 1:
        raise Exception(
            f"Too many references files in {PathToMito} directory, there should only be one"
        )

    elif len(listdir(PathToMito)) == 0:
        raise Exception(
            f"No mitochondrial reference file found in {PathToMito} directory, there be one"
        )

    if listdir(PathToMito)[0][-4:] == ".fna":
        rename(
            PathToMito + listdir(PathToMito)[0],
            PathToMito + listdir(PathToMito)[0].replace(".fna", ".fasta"),
        )

    data = None
    with open(PathToMito + listdir(PathToMito)[0], "r+") as file:
        data = file.read()
        if data[1 : data.find(" ")] != chrMName:
            data = data.replace(data[1 : data.find(" ")], chrMName)
            file.write(data)
        else:
            data = None

    if data != None:
        with open(PathToMito + listdir(PathToMito)[0], "w+") as file:
            file.write(data)

    mitochondriaName = listdir(PathToMito)[0].replace(".fasta", "")
    system(
        f"""
            mkdir -p {PathToTemp}mitochondria
            cp -u {PathToMito}{mitochondriaName}.fasta {PathToTemp}mitochondria
            """
    )

    return mitochondriaName


def prepareGtf(PathToGtf: str, PathToRef: str, PathToTemp: str, star: bool) -> str:
    """
    Prepare the Gene Transfert Format file for the pipeline
    Prepared only in the case STAR mapping is used
    Will first check if there is one GTF reference
    Will get the GTF name without its extension to pass it into snakemake
    """
    gtfName = "None"
    if star == True:
        if len(listdir(PathToGtf)) > 1:
            raise Exception(
                f"Too many gtf files in {PathToRef} directory, there should only be one"
            )
        if len(listdir(PathToGtf)) == 0:
            raise Exception(
                f"No gtf files found in {PathToRef} directory, you have to add it to use star mapping"
            )
        gtfName = listdir(PathToGtf)[0].replace(".gtf", "")
        system(f"mkdir -p {PathToTemp}/genomeDir")

    return gtfName


def prepareSamples(PathToSamples: str, PathToTemp: str, PathToOutput: str) -> set():
    """
    Prepare the sample files for the pipeline
    Will first check if there is at least one sample
    Then will convert possible alternative format in order to make snakemake easier to use:
    .fq -> .fastq, .fq.gz -> fastq.gz
    For the bam, will add their name into the result set
    For the .fastq, will get all the sample name into a set with their extensions replaced by .txt
    (which should be the result we get by running snakemake) and with the path to output to pass it into snakemake
    Create a directory in temp with their name for a better organisation
    """
    if len(listdir(PathToSamples)) == 0:
        raise Exception(f"No file found in {PathToSamples} directory")

    files = []
    for file in listdir(PathToSamples):
        rename(
            PathToSamples + file,
            PathToSamples
            + file.replace(".fq", ".fastq").replace(".fq.gz", ".fastq.gz"),
        )

    sample_list = listdir(PathToSamples)
    ignore_list = []  # To list the .fastq samples that already have their pair checked
    for file in sample_list:
        if file[-4:] == ".bam" or file[-6:] == ".bam.gz":
            name = file[: file.find(".")]
            system(
                f"""
                mkdir -p {PathToTemp}{name}
                cp -u {PathToSamples}{file} {PathToTemp}{name}/{name}.bam
            """
            )
            files.append(f"{PathToOutput}{name}.txt")

        elif (
            file[-6:] == ".fastq"
            or file[-9:] == ".fastq.gz"
            and file not in ignore_list
        ):
            if file.find("_R1") != -1:  # if there is _R1, no need to check for _R2
                if file.replace("_R1", "_R2") in sample_list:
                    name = file[: file.find("_R1")]
                    ignore_list.append(file.replace("_R1", "_R2"))
                    system(f"mkdir -p {PathToTemp}{name}")
                    files.append(f"{PathToOutput}{name}.txt")
            elif file.find("_R2") != -1:  # if there is _R2, no need to check for _R1
                if file.replace("_R2", "_R1") in sample_list:
                    name = file[: file.find("_R2")]
                    ignore_list.append(file.replace("_R2", "_R1"))
                    system(f"mkdir -p {PathToTemp}{name}")
                    files.append(f"{PathToOutput}{name}.txt")
            else:
                raise Exception(
                    f"Invalid .fastq file in {PathToSamples} directory, this pipeline only work with paired-end and bam"
                )
        elif file not in ignore_list:
            raise Exception(
                f"There seem to be an unwanted file in {PathToSamples} directory"
            )

    return set(files)
