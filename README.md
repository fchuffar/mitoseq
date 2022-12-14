# MITOSEQ
A pipeline dedicated to mitochondrial genome analysis from RNA sequencing data.

_________
## Installation/Configuration
- You need to clone this project to your desired directory with ```git clone HTTPS/SSH``` but you need to configure your SSH keys to perform the SSH copy

- In order to make this pipeline work you need to have conda installed and the environnement configured:

    -- To download Miniconda : https://docs.conda.io/en/latest/miniconda.html

    -- To install Miniconda : https://conda.io/projects/conda/en/latest/user-guide/install/index.html

    -- To setup the environnement: ```conda env update --file src/environment/env.yml --name MitoSeq ; conda activate MitoSeq```

- Once this done all target reads should be moved into    path/to/mitoseq/data/input/samples/

    -- If you use FASTQ as output make sure that paired RNASeq output sequences are called according to ```{sample_name/info}_R(1|2).fastq```.

    -- If you use BAM as output the prefix of each file will be used as a sample ID, feel free to rename it as you wish.


## Pipeline execution
- Once the previous steps are done you can perform the run by executing the following command
```$ python mitoseq.py```

- This should take time based on the number of samples

What is done to each sample:
```mermaid
graph TD;
Sequencing-->Sample_R1.fastq;
Sequencing-->Sample_R2.fastq;
Sample_R1.fastq-->BAM;
Output.bam-->BAM;
Sample_R2.fastq-->BAM;
Genome_references-->BAM;
Genome_references-->Index;
BAM-->Filtered.bam;
Filtered.bam-->Variant_calling;
Index-->Variant_calling;
Variant_calling-->VCF;
VCF-->Haplogrep

```

## Examples
### For complete information you can get the arguments manual by:
```$ python mythoseq.py -h```

Or feel free to check the documentation file in the root folder of the project.

- By default, the fastq data alignement will be performed by BWA, if you wish this step to be performed by STAR please specify it:

```$ python mitoseq.py --star``` or ```$ python mitoseq.py -a```

In this case the script need

- If your machine is limited in hardware you can specify hardware options:

```$ python mitoseq.py --core 2 --thread 2```  or  ```$ python mitoseq.py -c 2 -t 2```

which will run the pipeline on 2 cores using 2 threads.

- You can choose to keep all transitional files by using the following command:

```$ python mitoseq.py --keep``` or ```$ python mitoseq.py -k```

(Not recomended as far as every run generates ~50Gb of data for the whole genome)

## Results
- By the end you will obtain data/output/haplogroups.txt in which all samples' haplogroups are found along with the Haplogrep's quality score for each sample.
