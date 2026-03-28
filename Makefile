# SPDX-FileCopyrightText: 2025-2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

.PHONY: help install update lint test migrate run shell clean checkmigrations ci \
       license-add license-check loc \
       docker-build docker-up docker-down docker-logs docker-shell docker-clean

# Variables
SHELL := /bin/bash
PYTHON := pdm run python
PDM := pdm run
DJANGO := $(PYTHON) manage.py
ENV_FILE := .env.development
WITH_ENV := set -a && source $(ENV_FILE) && set +a &&

# =============================================================================
# Development
# =============================================================================

help: ## Show all available commands
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-24s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies
	pdm install

update: ## Update dependencies
	pdm update --unconstrained
	pdm sync

lint: ## Run linters
	$(PDM) lint

test: ## Run tests
	$(WITH_ENV) $(PDM) pytest

ci: lint test ## Run lint + tests (CI check)

run: migrate ## Run dev server (with migrations)
	$(WITH_ENV) $(DJANGO) runserver 0.0.0.0:8000

shell: ## Open Django shell
	$(WITH_ENV) $(DJANGO) shell

migrate: ## Run database migrations
	$(WITH_ENV) $(DJANGO) makemigrations
	$(WITH_ENV) $(DJANGO) migrate

checkmigrations: ## Check for unapplied migrations (dry-run)
	$(WITH_ENV) $(DJANGO) makemigrations --check --dry-run --no-input

clean: ## Remove temporary files (.pyc, caches, coverage)
	find . -name "**/*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +
	rm -f .coverage coverage.xml
	rm -rf htmlcov/ .mypy_cache .pytest_cache .ruff_cache

license-add: ## Add license headers to source files
	$(PDM) license-add

license-check: ## Check license headers
	$(PDM) license-check

loc: ## Count lines of code vs tests
	@code=$$(find . -type f -name '*.py' ! -name 'test_*.py' ! -path '*/venv/*' ! -path '*/.venv/*' ! -path '*/migrations/*' | xargs wc -l | tail -n1 | awk '{print $$1}'); \
	tests=$$(find . -type f -name 'test_*.py' ! -path '*/venv/*' ! -path '*/.venv/*' ! -path '*/migrations/*' | xargs wc -l | tail -n1 | awk '{print $$1}'); \
	if [ -z "$$tests" ]; then tests=0; fi; \
	total=$$((code + tests)); \
	ratio=$$(python3 -c "print(round(($$tests / $$total * 100) if $$total else 0, 2))"); \
	echo "Total Python lines: $$total (code: $$code, tests: $$tests, ratio: $$ratio%)"

# =============================================================================
# Docker
# =============================================================================

DOCKER_IMAGE := kotlyar562/guitar0net-backend
DOCKER_TAG := $(shell git describe --tags --always 2>/dev/null || echo "latest")

docker-build: ## Build Docker image
	docker build -t $(DOCKER_IMAGE):$(DOCKER_TAG) -f Dockerfile .

docker-up: ## Start dev environment (docker compose)
	docker network create guitar0-network 2>/dev/null || true
	GIT_SHA=$(shell git rev-parse --short HEAD) docker compose up -d

docker-down: ## Stop dev environment
	docker compose down

docker-logs: ## Tail container logs
	docker compose logs -f

docker-shell: ## Shell into app container
	docker compose exec app bash

docker-clean: ## Remove containers, volumes, and images
	docker compose down -v --rmi local

# Monitoring and deployment are managed in guitar0-net/infrastructure repo
