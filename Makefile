

IS_DOCKER_INSTALLED = $(shell which docker >> /dev/null 2>&1; echo $$?)

# Docker info
DOCKER_REPO ?= kaleoum
DOCKER_IMAGE ?= py-runner
DOCKER_TAG ?= ci1

.PHONY: help
help:
	@echo ""
	@echo "Usage:-"
	@echo "\tmake deps          	-- sets up dependencies for image build"
	@echo "\tmake build-amd64   	-- builds the litmus-py docker amd64 image"
	@echo "\tmake push-amd64    	-- pushes the litmus-py amd64 image"
	@echo "\tmake build-amd64-byoc  -- builds the chaostest docker amd64 image"
	@echo "\tmake push-amd64-byoc   -- pushes the chaostest amd64 image"
	@echo ""

.PHONY: all
all: deps build-amd64 push-amd64 build-amd64-byoc push-amd64-byoc trivy-check

.PHONY: deps
deps: _build_check_docker

_build_check_docker:
	@if [ $(IS_DOCKER_INSTALLED) -eq 1 ]; \
		then echo "" \
		&& echo "ERROR:\tdocker is not installed. Please install it before build." \
		&& echo "" \
		&& exit 1; \
		fi;

.PHONY: build-amd64
build-amd64:

	@echo "-------------------------"
	@echo "--> Build py-runner image" 
	@echo "-------------------------"
	@sudo docker build --file Dockerfile --tag $(DOCKER_REPO)/$(DOCKER_IMAGE):$(DOCKER_TAG) . --build-arg TARGETARCH=amd64

.PHONY: push-amd64
push-amd64:
	@echo "-------------------"
	@echo "--> go-runner image" 
	@echo "-------------------"
	REPONAME="$(DOCKER_REPO)" IMGNAME="$(DOCKER_IMAGE)" IMGTAG="$(DOCKER_TAG)" ./build/push

.PHONY: build-amd64-byoc
build-amd64:

	@echo "-------------------------"
	@echo "--> Build py-runner image" 
	@echo "-------------------------"
	@sudo docker build --file byoc/Dockerfile --tag $(DOCKER_REPO)/$(DOCKER_IMAGE):$(DOCKER_TAG) . --build-arg TARGETARCH=amd64

.PHONY: push-amd64-byoc
push-amd64:
	@echo "-------------------"
	@echo "--> go-runner image" 
	@echo "-------------------"
	REPONAME="$(DOCKER_REPO)" IMGNAME="$(DOCKER_IMAGE)" IMGTAG="$(DOCKER_TAG)" .byoc/buildscripts/push

.PHONY: trivy-check
trivy-check:

	@echo "------------------------"
	@echo "---> Running Trivy Check"
	@echo "------------------------"
	@./trivy --exit-code 0 --severity HIGH --no-progress $(DOCKER_REPO)/$(DOCKER_IMAGE):$(DOCKER_TAG)
	@./trivy --exit-code 0 --severity CRITICAL --no-progress $(DOCKER_REPO)/$(DOCKER_IMAGE):$(DOCKER_TAG)