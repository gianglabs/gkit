SLURM_IMAGE:= nttg8100/river-slurm:1.1.0
.PHONY: setup example clean

${HOME}/.pixi/bin/pixi:
	curl -sSL https://pixi.sh/install.sh | sh

setup: ${HOME}/.pixi/bin/pixi
	${HOME}/.pixi/bin/pixi install

start-slurm:
	docker run \
		-v ${PWD}:/tmp/spark \
		-v ${HOME}/.pixi:/root/.pixi \
		--name slurm-dev \
		-p 8081:22 \
		--rm \
		--privileged \
		-d ${SLURM_IMAGE} || echo "Docker Slurm is already configured"
	
	# wait for slurm to start
	sleep 5

# inside user river is the standard user with 1001 mapping id, Github Actions does not have this user
test: ${HOME}/.pixi/bin/pixi start-slurm
	docker exec \
		-w /tmp/spark \
		slurm-dev /root/.pixi/bin/pixi run sparkhpc-example

test-slurm-local:
	${HOME}/.pixi/bin/pixi run sparkhpc-example

clean:
	rm -f sparkhpc/sparkcluster-*.log sparkhpc/job
	rm -f ${HOME}/.sparkhpc*
