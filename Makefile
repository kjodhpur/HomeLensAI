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

sync:           ## copy notebook outputs into backend/app/data
	$(PY) scripts/sync_artifacts.py

backend:        ## run the API on :8000
	cd backend && $(PY) -m pip install -q -r requirements-dev.txt && $(PY) -m uvicorn app.main:app --reload --port 8000

frontend:       ## run the web app on :3000
	cd frontend && npm install && npm run dev

test:           ## backend tests + frontend typecheck
	cd backend && $(PY) -m pytest -q
	cd frontend && npm run typecheck

.PHONY: help setup-notebook sample notebook run-notebook sync backend frontend test
