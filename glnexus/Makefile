.PHONY: test
${HOME}/.pixi/bin/pixi:
	curl -sSL https://pixi.sh/install.sh | sh

test: ${HOME}/.pixi/bin/pixi
	${HOME}/.pixi/bin/pixi run bash joint_genotyping_cohort_vcf.sh