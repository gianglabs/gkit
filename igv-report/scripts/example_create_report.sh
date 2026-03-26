# prepare data
bash scripts/remote_subset.sh \
		1:114842600 \
		200 \
		data/example_sources.csv \
		output

# example script for generating the report
create_report output/High_Confidence_GIAB__114842600.vcf.gz \
    --genome hg19 \
    --flanking 1000 \
    --track-config ./output/tracks_config.json\
    --output output/example.html \
    --standalone \
    --title "Source" \
    --info-columns platforms,platformnames,datasets