SHELL := /bin/bash

# Defaults — override with: make deploy CONDA_ENV= METAFLOW_PROFILE=
CONDA_ENV ?= base
METAFLOW_PROFILE ?= mozart

# Build ENV_PREFIX from optional components
_CONDA := $(if $(CONDA_ENV),source ~/.zshrc 2>/dev/null && conda activate $(CONDA_ENV) &&,)
_MF    := $(if $(METAFLOW_PROFILE),METAFLOW_PROFILE=$(METAFLOW_PROFILE),)
ENV_PREFIX := $(_CONDA) $(_MF)

.PHONY: help install config-local config-prod run-local test-local deploy status logs delete test-remote clean run-python populate

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'

install: ## Install evidently and dependencies
	$(ENV_PREFIX) pip install "evidently[sql]" pyyaml s3fs psycopg2-binary scikit-learn

config-local: ## Generate local SQLite config (for dev/testing)
	$(ENV_PREFIX) python generate_config.py --local

config-prod: ## Generate production config (PostgreSQL + S3, requires Metaflow creds)
	$(ENV_PREFIX) python generate_config.py

run-local: config-local ## Start Evidently UI locally with SQLite
	$(ENV_PREFIX) python run_evidently.py --host 0.0.0.0 --port 8000 --conf-path evidently_config.yaml

test-local: ## Run test against local instance (http://localhost:8000)
	$(ENV_PREFIX) python test_app.py --url http://localhost:8000

deploy: ## Deploy Evidently app to Outerbounds
	$(ENV_PREFIX) outerbounds app deploy --config-file evidently-ui.yaml

status: ## Check deployment status
	$(ENV_PREFIX) outerbounds app list | grep -i evidently || echo "No evidently apps found"

logs: ## Show app logs (pass WORKER_ID=... for specific worker)
	$(ENV_PREFIX) outerbounds app logs --name evidently-ui $(if $(WORKER_ID),--worker-id $(WORKER_ID),)

delete: ## Delete the deployed Evidently app
	$(ENV_PREFIX) outerbounds app delete --name evidently-ui

test-remote: ## Run test against deployed instance (pass URL=https://...)
	$(ENV_PREFIX) python test_app.py --url $(URL) --use-auth

test-remote-project: ## Run full test with project creation (pass URL=https://...)
	$(ENV_PREFIX) python test_app.py --url $(URL) --use-auth --test-project

populate: ## Populate dashboard with sample ML data (pass URL=https://...)
	$(ENV_PREFIX) python populate_data.py --url $(URL)

run-python: ## Run a python snippet (pass CMD="...")
	$(ENV_PREFIX) python -c "$(CMD)"

clean: ## Remove generated config and local workspace
	rm -f evidently_config.yaml
	rm -rf workspace/
