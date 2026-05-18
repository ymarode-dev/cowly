.PHONY: help setup up up-fg down logs ps health version seed test test-integration test-service \
        build-images push-images pull up-pull dev watch backup restore reset

ROOT := $(shell pwd)
VERSION := $(shell tr -d '[:space:]' < VERSION)
export COWLY_VERSION ?= $(VERSION)

COMPOSE := docker compose -f docker-compose.yml
COMPOSE_PULL := docker compose -f docker-compose.pull.yml
COMPOSE_DEV := docker compose -f docker-compose.yml -f docker-compose.dev.yml

help:
	@echo "Cowly local commands"
	@echo "  make setup          Bootstrap (.env, build, start, wait for health)"
	@echo "  make setup-seed     Bootstrap + demo data"
	@echo "  make up             Start stack (detached)"
	@echo "  make down           Stop stack (keeps data)"
	@echo "  make logs           Follow all service logs"
	@echo "  make ps             Service status"
	@echo "  make health         Gateway health check"
	@echo "  make version        Show running version"
	@echo "  make seed           Load demo data (profile seed)"
	@echo "  make test           Run all unit tests in Docker (Python 3.11)"
	@echo "  make test-integration  Unit + E2E tests in Docker (starts stack if needed)"
	@echo "  make test-service SVC=auth-service  Test one service in Docker"
	@echo "  make build-images   Build versioned Docker images"
	@echo "  make push-images    Build and push to COWLY_IMAGE_REGISTRY"
	@echo "  make pull           Pull pre-built images"
	@echo "  make up-pull        Run from pre-built images only"
	@echo "  make dev            Start with dev compose overrides"
	@echo "  make watch          Dev stack with compose watch"
	@echo "  make backup         pg_dump all databases"
	@echo "  make restore DIR=  Restore from backup directory"
	@echo "  make reset          Stop and wipe database volume (confirmed)"

setup:
	@./scripts/setup.sh

setup-seed:
	@./scripts/setup.sh --seed

up:
	$(COMPOSE) up --build -d

up-fg:
	$(COMPOSE) up --build

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f

ps:
	$(COMPOSE) ps

health:
	@curl -sf "http://localhost:$${COWLY_GATEWAY_PORT:-8000}/health" | python3 -m json.tool

version:
	@curl -sf "http://localhost:$${COWLY_GATEWAY_PORT:-8000}/version" | python3 -m json.tool

seed:
	$(COMPOSE) --profile seed up cowly-seed

test:
	@./scripts/run_all_tests.sh

test-integration:
	@RUN_INTEGRATION=1 ./scripts/run_all_tests.sh

test-service:
	@test -n "$(SVC)" || (echo "Usage: make test-service SVC=herd-service" && exit 1)
	@./scripts/run_service_tests.sh "$(SVC)"

build-images:
	@./scripts/build-and-push.sh

push-images:
	@PUSH=true ./scripts/build-and-push.sh

pull:
	$(COMPOSE_PULL) pull

up-pull:
	$(COMPOSE_PULL) up -d

dev:
	$(COMPOSE_DEV) up --build -d

watch:
	$(COMPOSE_DEV) watch

backup:
	@./scripts/db-backup.sh

restore:
	@test -n "$(DIR)" || (echo "Usage: make restore DIR=backups/TIMESTAMP" && exit 1)
	@./scripts/db-restore.sh "$(DIR)"

reset:
	@./scripts/reset.sh
