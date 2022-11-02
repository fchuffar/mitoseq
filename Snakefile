#Paths 
PathToRef = 'Data/Input/Ref/'
PathToRaw = 'Data/Input/Samples/'
PathToTemp = 'Data/Temp/'
PathToOutput = 'Data/Output/'


rule index:
    input:
        reference = PathToRef + "ref_mitochondrial.fasta"
    output:
        sample_fasta = PathToTemp + "{sample}.fasta",
        bwa_index = PathToTemp + "{sample}.fasta.bwt",
        fai_index = PathToTemp + "{sample}.fasta.fai",
        dictionary = PathToTemp + "{sample}.dict"
    conda:
        "Env/config.yaml"
    shell:
        """
        cp {input.reference} {output.sample_fasta}
        bwa index {output.sample_fasta}
        samtools faidx {output.sample_fasta}
        gatk CreateSequenceDictionary -R {output.sample_fasta} 
        """


rule mapping:    ### 1100 s 4 threads
    input:
        reference = PathToTemp + "{sample}.fasta",
        R1 = PathToRaw + "{sample}_R1.fastq",
        R2 = PathToRaw + "{sample}_R2.fastq"
    params:
        thread = config['thread']
    output:
        PathToTemp + "{sample}.bam"
    conda:
        "Env/config.yaml"
    shell:
        "bwa mem -t {params.thread} {input.reference} {input.R1} {input.R2} | samtools view -@ 4 -bh | samtools sort -@ 4 -o {output}"


rule bam_index:   ### 58 s 4 threads
    input:
        bam = PathToTemp + "{sample}.bam"
    output:
        bam_ind = PathToTemp + "{sample}.bam.bai"
    conda:
        "Env/config.yaml"
    shell:
        "samtools index {input.bam}"


rule add_groups:
    input:
        bam = PathToTemp + "{sample}.bam"
    output:
        bam = PathToTemp + "{sample}.groups.bam"
    conda:
        "Env/config.yaml"
    shell:
        "picard AddOrReplaceReadGroups I={input.bam} O={output.bam} RGLB=lib.HSmt RGPL=illumina RGPU='NO_GROUP' RGSM=20"


rule mark:
    input:
        bam_ind = PathToTemp + "{sample}.bam.bai",
        bam = PathToTemp + "{sample}.groups.bam"
    output:
        bam_marked = PathToTemp + "{sample}.marked.bam"
    conda:
        "Env/config.yaml"
    shell:
        "gatk MarkDuplicatesSpark -I {input.bam} -O {output.bam_marked}" 


rule filter:
    input:
        bam = PathToTemp + "{sample}.marked.bam"
    output:
        bam_filtered = PathToTemp + "{sample}.filtered.bam"
    conda:
        "Env/config.yaml"
    shell:
        "samtools view -h -@ 4 -f  0x2 -F 0x4 -F 0x8 -F 0x100 {input.bam} | samtools view -bh -@ 4 -o {output.bam_filtered}"


rule sort:
    input:
        PathToTemp + "{sample}.filtered.bam"
    output:
        PathToTemp + "{sample}.sorted.bam"
    conda:
        "Env/config.yaml"
    shell:
        "picard FixMateInformation I={input} SO=coordinate O={output}"


rule build_index:
    input:
        PathToTemp + "{sample}.sorted.bam"
    output:
        PathToTemp + "{sample}.sorted.bai"
    conda:
        "Env/config.yaml"
    shell:
        "picard BuildBamIndex I={input}"


rule variant_calling:   ###457 s
    input:
        PathToTemp + "{sample}.sorted.bai",
        reference = PathToTemp + "{sample}.fasta",
        target_bam = PathToTemp + "{sample}.sorted.bam"
    output:
        PathToOutput + "{sample}.vcf"
    params:
        thread = config['thread']
    conda:
        "Env/config.yaml"
    shell:
        "gatk Mutect2 --native-pair-hmm-threads {params.thread} -R {input.reference} -I {input.target_bam} -O {output}"
