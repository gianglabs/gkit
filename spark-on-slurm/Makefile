SLURM_IMAGE:= nttg8100/river-slurm:1.1.0
.PHONY: setup example clean

${HOME}/.pixi/bin/pixi:
	curl -sSL https://pixi.sh/install.sh | sh

setup: ${HOME}/.pixi/bin/pixi
	${HOME}/.pixi/bin/pixi install

start-slurm:
	docker run \
		-v ${PWD}:/home/river/spark \
		--name slurm-dev \
		-p 8081:22 \
		--rm \
		--privileged \
		-d ${SLURM_IMAGE} || echo "Docker Slurm is already configured"

# inside user river is the standard user with 1001 mapping id, Github Actions does not have this user
test: start-slurm
	docker exec \
		-u 1001:1001 \
		-w /home/river/spark \
		slurm-dev /home/river/.pixi/bin/pixi run sparkhpc-example

test-slurm-local:
	${HOME}/.pixi/bin/pixi run sparkhpc-example

clean:
	rm -f sparkhpc/sparkcluster-*.log sparkhpc/job
	rm -f ${HOME}/.sparkhpc*
