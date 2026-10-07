# Convenience commands — run `make help`.
PY ?= python
.DEFAULT_GOAL := help

help:           ## show this help
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  %-16s %s\n", $$1, $$2}'

setup-notebook: ## install notebook dependencies + spaCy model
	$(PY) -m pip install -r requirements.txt && $(PY) -m spacy download en_core_web_sm

sample:         ## regenerate the synthetic sample dataset
	$(PY) scripts/make_sample_data.py

notebook:       ## open JupyterLab on the final-project notebook
	$(PY) -m jupyterlab notebooks/HomeLensAI_Final_Project.ipynb

run-notebook:   ## execute the notebook headlessly (uses the sample data if the real data is absent)
	cd notebooks && $(PY) -m jupyter nbconvert --to notebook --execute HomeLensAI_Final_Project.ipynb --output /tmp/HomeLensAI_executed.ipynb

export:        ## regenerate frontend/data from artifacts/ (run after build_artifacts.py)
	$(PY) scripts/export_frontend_data.py

frontend:       ## run the web app on :3000
	cd frontend && npm install && npm run dev

test:           ## frontend typecheck + parity tests
	cd frontend && npm run typecheck && npm test

test-py:        ## Python tests (risk logic, masking, artifacts)
	$(PY) -m pytest -q

.PHONY: help setup-notebook sample notebook run-notebook export frontend test test-py
