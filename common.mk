.PHONY: test
HOMEDIR:=$(dir $(abspath $(lastword $(MAKEFILE_LIST))))
${HOME}/.pixi/bin/pixi:
	curl -sSL https://pixi.sh/install.sh | sh