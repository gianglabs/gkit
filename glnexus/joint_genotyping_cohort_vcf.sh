################ Download data ##############################
HOME_DIR=$(pwd)
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


################ Joint calling ##############################
# 1. GLnexus
# create testing bed file
cd $HOME_DIR
echo -e "chr12\t111760000\t111765000" > ALDH2_5kb.bed

cd ${HOME_DIR}/cohort_vcf/GIAB/data
glnexus_cli --config DeepVariant --threads 4 --bed $HOME_DIR/ALDH2_5kb.bed *.g.vcf.gz > GIAB_ALDH2_5kb.bcf
bcftools view GIAB_ALDH2_5kb.bcf | bgzip -@ 4 -c >  GIAB_ALDH2_5kb.vcf.gz

cd ${HOME_DIR}/cohort_vcf/1KGP/data
glnexus_cli --config DeepVariant --threads 4 --bed $HOME_DIR/ALDH2_5kb.bed *.gvcf.gz > 1KGP_ALDH2_5kb.bcf
bcftools view 1KGP_ALDH2_5kb.bcf | bgzip -@ 4 -c >  1KGP_ALDH2_5kb.vcf.gz