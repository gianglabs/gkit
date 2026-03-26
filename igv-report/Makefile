.PHONY: test clean
${HOME}/.pixi/bin/pixi:
	curl -sSL https://pixi.sh/install.sh | sh

test: ${HOME}/.pixi/bin/pixi
	${HOME}/.pixi/bin/pixi run bash scripts/example_create_report.sh

clean:
	rm -rf output