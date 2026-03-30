SLURM_IMAGE:= nttg8100/river-slurm:1.1.0
.PHONY: setup example clean

${HOME}/.pixi/bin/pixi:
	curl -sSL https://pixi.sh/install.sh | sh

setup: ${HOME}/.pixi/bin/pixi
	${HOME}/.pixi/bin/pixi install

start-slurm:
	docker run \
		-v ${PWD}:/home/river \
		--name slurm-dev \
		-p 8081:22 \
		--rm \
		--privileged \
		-d ${SLURM_IMAGE}

test: setup
	docker exec \
		-u river \
		-w /home/river \
		slurm-dev \
		/home/river/.pixi/bin/pixi \
		run sparkhpc-example

clean:
	rm -f sparkhpc/sparkcluster-*.log sparkhpc/job
	rm -f ${HOME}/.sparkhpc*
