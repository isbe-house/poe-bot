
export UID=$(shell id -u)
export GID=$(shell id -g)
SHELL := /bin/bash

export TWINE_USERNAME=${TWINE_USERNAME:-"UNDEFINED"}
export TWINE_PASSWORD=${TWINE_PASSWORD:-"UNDEFINED"}

up: ## Start all containers
	docker-compose \
        -f  docker-compose.yaml \
        up -d --build trade-slurp grafana web discord-bot jupyter

run-discord-bot: ## Run container connected
	docker-compose \
		-f  docker-compose.yaml \
		run --rm discord-bot

debug-discord-bot: ## Start interactive python shell to debug with
	docker-compose \
		-f docker-compose.yaml \
		run --rm discord-bot /bin/bash

run-trade-slurp: ## Run container connected
	docker-compose \
		-f  docker-compose.yaml \
		run --rm trade-slurp

debug-trade-slurp: ## Start interactive python shell to debug with
	docker-compose \
		-f docker-compose.yaml \
		run --rm trade-slurp /bin/bash

run-influx: ## Run container connected
	docker-compose \
		-f  docker-compose.yaml \
		run --rm influx

run-jupyter: ## Run container connected
	docker-compose \
		-f  docker-compose.yaml \
		run --rm --service-ports jupyter

debug-influx: ## Start interactive python shell to debug with
	docker-compose \
		-f docker-compose.yaml \
		run --rm influx /bin/bash

exec-influx: ## Start interactive python shell to debug with
	docker-compose \
		-f docker-compose.yaml \
		exec influx /bin/bash

build:
	docker-compose \
		-f docker-compose.yaml \
		build

rebuild:
	docker-compose \
		-f docker-compose.yaml \
		build --no-cache --parallel

down: ## Stop all containers
	docker-compose \
		-f  docker-compose.yaml \
		down

logs: ## Display logs (follow)
	docker-compose \
        -f  docker-compose.yaml \
        logs --follow --tail=20 discord-bot trade-slurp

debug-web: ## Start interactive python shell to debug with
	docker-compose \
		-f docker-compose.yaml \
		run --rm web /bin/bash

# jupyter: ## Start a jupyter environment for debugging and such
# 	docker-compose \
# 		-f  docker-compose.yaml \
# 		run --rm jupyter

test: ## Start a jupyter environment for debugging and such
	make test-poe-lib-pytest
	docker-compose -f docker-compose.yaml rm -fsv test-mongo

test-poe-lib-pytest:
	docker-compose \
		-f  docker-compose.yaml \
		run --rm poe-lib-test \
		python -m pytest --cov-report term:skip-covered --cov=poe_lib --color=yes tests
	# Run with -x if you need to stop at first failure.
	# docker-compose \
	# 	-f  docker-compose.yaml \
	# 	run --rm poe-lib-test \
	# 	coverage html


######################################################################################################################################################

help:
	@grep -E '^[0-9a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help

.PHONY: up down clean populate test build debug run build-docs dist release docs
# .SILENT: test up down up clean
