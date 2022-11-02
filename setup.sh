mkdir Data
mkdir Data/Input Data/Temp
mkdir Data/Input/Ref Data/Input/Samples
cd Data/Input/Ref
esearch -db nucleotide -query "NC_012920.1" | efetch -format fasta > ref_mitochondrial.fasta
