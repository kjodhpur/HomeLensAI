# Backend (FastAPI)

An HTTP layer over the anonymized `artifacts/` and the review-risk logic. Endpoints and schemas: [`../docs/DATA_CONTRACT.md`](../docs/DATA_CONTRACT.md).

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt        # scikit-learn is pinned to 1.8.0 (matches the joblib files)
uvicorn app.main:app --reload --port 8000  # docs at http://localhost:8000/docs
pytest -q
ruff check ..
```

| File | Purpose |
|---|---|
| `app/main.py` | FastAPI app and routes (`app` is the Vercel entrypoint) |
| `app/artifacts.py` | reads the CSV/JSON artifacts, builds providers, aspects and the overview/KPI series |
| `app/scoring.py` | TF-IDF scoring: per-sentence probabilities, evidence sentence, token weights; dictionary-only fallback |
| `app/risk_logic.py` | **vendored copy** of `../app/risk_logic.py` (aspect dictionary, masking, recommendations) — do not edit here |
| `app/data/artifacts/` | **vendored copy** of `../artifacts/` — do not edit here |
| `tests/` | pytest suite (includes a drift check on the vendored files) |

Refresh the vendored files with `python ../scripts/sync_artifacts.py`. Environment variables: [`.env.example`](.env.example). Deployment: [`../docs/DEPLOYMENT.md`](../docs/DEPLOYMENT.md).
