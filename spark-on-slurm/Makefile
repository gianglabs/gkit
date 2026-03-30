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

get-slurm:
	@count=0; \
	max=5; \
	until [ $$count -ge $$max ]; do \
		echo "Checking SLURM (attempt $$((count+1))/$$max)..." ; \
		docker exec -it -w /home/river slurm-dev squeue && break; \
		count=$$((count+1)); \
		echo "SLURM not ready, retrying in 5 seconds..." ; \
		sleep 5; \
	done; \
	if [ $$count -eq $$max ]; then \
		echo "SLURM still not available after $$max attempts"; \
		exit 1; \
	fi

# inside user river is the standard user with 1001 mapping id, Github Actions does not have this user
test: ${HOME}/.pixi/bin/pixi start-slurm get-slurm
	docker exec \
		-w /tmp/spark \
		slurm-dev /root/.pixi/bin/pixi run sparkhpc-example

test-slurm-local:
	${HOME}/.pixi/bin/pixi run sparkhpc-example

clean:
	rm -f sparkhpc/sparkcluster-*.log sparkhpc/job
	rm -f ${HOME}/.sparkhpc*
