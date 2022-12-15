from os import listdir, system, rename

# A module useful for a fast and easy way to access functionalities of the system


def fuse_haplogroups():
    """ """
    with open("data/output/haplogroups.txt", "w", encoding="utf-8") as output_file:
        output_file.write(
            '"SampleID"	"Haplogroup"	"Rank"	"Quality"	"Range"	"Origin_Filename"\n'
        )
        for file in listdir("data/output/"):
            with open(f"data/output/{file}", encoding="utf-8") as input_file:
                for line in input_file.readlines()[1:]:
                    output_file.write(line.replace("\n", "") + f"  {file}\n")


def prepareRef(PathToRef: str, PathToTemp: str) -> str:
    """ """
    if len(listdir(PathToRef)) > 1:
        raise Exception(
            f"Too many references files in {PathToRef} directory, there should only be one"
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
    """ """
    if len(listdir(PathToMito)) > 1:
        raise Exception(
            f"Too many references files in {PathToMito} directory, there should only be one"
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
    """ """
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


def prepareSamples(PathToSamples: str, PathToTemp: str, PathToOutput: str) -> set(str):
    """ """
    ## Obtaining a sample list from the files existing in the samples folder
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
    ignore_list = []
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
            if file.find("_R1") != -1:
                if file.replace("_R1", "_R2") in sample_list:
                    name = file[: file.find("_R1")]
                    ignore_list.append(file.replace("_R1", "_R2"))
                    system(f"mkdir -p {PathToTemp}{name}")
                    files.append(f"{PathToOutput}{name}.txt")
            elif file.find("_R2") != -1:
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
