HOME_DIR=$(pwd)
################ Download data ##############################
# Download reference
mkdir -p reference
aws s3 cp --no-sign-request s3://ngi-igenomes/igenomes/Homo_sapiens/GATK/GRCh38/Sequence/WholeGenomeFasta/Homo_sapiens_assembly38.fasta reference
aws s3 cp --no-sign-request s3://ngi-igenomes/igenomes/Homo_sapiens/GATK/GRCh38/Sequence/WholeGenomeFasta/Homo_sapiens_assembly38.fasta.fai reference
aws s3 cp --no-sign-request s3://ngi-igenomes/igenomes/Homo_sapiens/GATK/GRCh38/Sequence/WholeGenomeFasta/Homo_sapiens_assembly38.dict reference

# GIAB
cd ${HOME_DIR}/cohort_vcf/GIAB/data
gsutil cp gs://deepvariant/case-study-outputs/1.10.0/deeptrio/wgs/HG002.child.g.vcf.gz .
gsutil cp gs://deepvariant/case-study-outputs/1.10.0/deeptrio/wgs/HG002.child.g.vcf.gz.tbi .

gsutil cp gs://deepvariant/case-study-outputs/1.10.0/deeptrio/wgs/HG003.parent1.g.vcf.gz .
gsutil cp gs://deepvariant/case-study-outputs/1.10.0/deeptrio/wgs/HG003.parent1.g.vcf.gz.tbi .

gsutil cp gs://deepvariant/case-study-outputs/1.10.0/deeptrio/wgs/HG004.parent2.g.vcf.gz .
gsutil cp gs://deepvariant/case-study-outputs/1.10.0/deeptrio/wgs/HG004.parent2.g.vcf.gz.tbi .


# 1KGP
cd ${HOME_DIR}/cohort_vcf/1KGP/data
aws s3 cp --no-sign-request s3://1000genomes-dragen-v4-2-7/data/individuals/hg38_alt_masked_graph_v3/NA21144/NA21144.final.hard-filtered.gvcf.gz .
aws s3 cp --no-sign-request s3://1000genomes-dragen-v4-2-7/data/individuals/hg38_alt_masked_graph_v3/NA21144/NA21144.final.hard-filtered.gvcf.gz.tbi .

aws s3 cp --no-sign-request s3://1000genomes-dragen-v4-2-7/data/individuals/hg38_alt_masked_graph_v3/NA21143/NA21143.final.hard-filtered.gvcf.gz .
aws s3 cp --no-sign-request s3://1000genomes-dragen-v4-2-7/data/individuals/hg38_alt_masked_graph_v3/NA21143/NA21143.final.hard-filtered.gvcf.gz.tbi .

aws s3 cp --no-sign-request s3://1000genomes-dragen-v4-2-7/data/individuals/hg38_alt_masked_graph_v3/NA21142/NA21142.final.hard-filtered.gvcf.gz .
aws s3 cp --no-sign-request s3://1000genomes-dragen-v4-2-7/data/individuals/hg38_alt_masked_graph_v3/NA21142/NA21142.final.hard-filtered.gvcf.gz.tbi .