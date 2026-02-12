SHELL := /bin/bash
CONDA_ACTIVATE := source ~/.zshrc 2>/dev/null && conda activate ob-lambdas
METAFLOW_PROFILE := mozart

.PHONY: help install config-local config-prod run-local test-local deploy status logs delete test-remote clean run-python

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'

install: ## Install evidently and dependencies in ob-lambdas conda env
	$(CONDA_ACTIVATE) && pip install "evidently[sql]" pyyaml s3fs psycopg2-binary

config-local: ## Generate local SQLite config (for dev/testing)
	$(CONDA_ACTIVATE) && METAFLOW_PROFILE=$(METAFLOW_PROFILE) python generate_config.py --local

config-prod: ## Generate production config (PostgreSQL + S3, requires Metaflow creds)
	$(CONDA_ACTIVATE) && METAFLOW_PROFILE=$(METAFLOW_PROFILE) python generate_config.py

run-local: config-local ## Start Evidently UI locally with SQLite
	$(CONDA_ACTIVATE) && METAFLOW_PROFILE=$(METAFLOW_PROFILE) python run_evidently.py --host 0.0.0.0 --port 8000 --conf-path evidently_config.yaml

test-local: ## Run test against local instance (http://localhost:8000)
	$(CONDA_ACTIVATE) && METAFLOW_PROFILE=$(METAFLOW_PROFILE) python test_app.py --url http://localhost:8000

deploy: ## Deploy Evidently app to Outerbounds
	$(CONDA_ACTIVATE) && METAFLOW_PROFILE=$(METAFLOW_PROFILE) outerbounds app deploy --config-file evidently-ui.yaml

status: ## Check deployment status
	$(CONDA_ACTIVATE) && METAFLOW_PROFILE=$(METAFLOW_PROFILE) outerbounds app list | grep -i evidently || echo "No evidently apps found"

logs: ## Show app logs (pass WORKER_ID=... for specific worker)
	$(CONDA_ACTIVATE) && METAFLOW_PROFILE=$(METAFLOW_PROFILE) outerbounds app logs --name evidently-ui $(if $(WORKER_ID),--worker-id $(WORKER_ID),)

delete: ## Delete the deployed Evidently app
	$(CONDA_ACTIVATE) && METAFLOW_PROFILE=$(METAFLOW_PROFILE) outerbounds app delete --name evidently-ui

test-remote: ## Run test against deployed instance (pass URL=https://...)
	$(CONDA_ACTIVATE) && METAFLOW_PROFILE=$(METAFLOW_PROFILE) python test_app.py --url $(URL) --use-auth

test-remote-project: ## Run full test with project creation (pass URL=https://...)
	$(CONDA_ACTIVATE) && METAFLOW_PROFILE=$(METAFLOW_PROFILE) python test_app.py --url $(URL) --use-auth --test-project

run-python: ## Run a python snippet (pass CMD="...")
	$(CONDA_ACTIVATE) && METAFLOW_PROFILE=$(METAFLOW_PROFILE) python -c "$(CMD)"

clean: ## Remove generated config and local workspace
	rm -f evidently_config.yaml
	rm -rf workspace/
