# Ambient Superconductivity Lab — task runner.
# `make help` lists targets. Python runs with src/ on the path, so an editable
# install is optional.

PYTHON ?= python
export PYTHONPATH := $(CURDIR)/src$(if $(PYTHONPATH),:$(PYTHONPATH))
BIB := docs/references.bib

.DEFAULT_GOAL := help
.PHONY: help env test lint-bib verify-refs prove-0 prove-all status readme site site-dev site-test manim clean

help: ## List targets
	@grep -E '^[a-zA-Z0-9_%-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'

env: ## Create the conda environment `asl` (Miniforge/mamba)
	mamba env create -f environment.yml || conda env create -f environment.yml

test: ## Run the unit tests
	$(PYTHON) -m pytest

lint-bib: ## Lint docs/references.bib
	$(PYTHON) -m asl.refs.lint $(BIB)

verify-refs: ## Verify every DOI online (uses ASL_OFFLINE=1 to read the cache only)
	$(PYTHON) -m asl.refs.verify $(BIB)

prove-0: verify-refs lint-bib ## Stage 0 proof (verifies references first)
	$(PYTHON) -m asl.proofs.runner 0

prove-%: ## Run the proof for stage N, e.g. make prove-1
	$(PYTHON) -m asl.proofs.runner $*

prove-all: verify-refs ## Run every stage marked ci: true in proofs/registry.yaml
	$(PYTHON) -m asl.proofs.runner --all

status: ## Write status badges into site/public/status (after prove-all)
	$(PYTHON) -m asl.proofs.status badges site/public/status

readme: ## Regenerate the README status table from proofs/registry.yaml
	$(PYTHON) -m asl.proofs.status readme

site: ## Build the GitHub Pages site into site/dist
	cd site && npm ci && npm run build

site-dev: ## Run the site locally with hot reload
	cd site && npm install && npm run dev

site-test: ## Playwright visual tests (non-blank canvas + screenshots)
	cd site && npx playwright install --with-deps chromium && npm run test:visual

manim: ## Render Manim scenes at low quality (as CI does)
	cd animations/manim && for f in scenes/*.py; do manim -ql --media_dir ../../build/manim "$$f" -a || exit 1; done

clean: ## Remove build outputs and proof results
	rm -rf build site/dist site/test-results site/playwright-report proofs/stage*/result.json
