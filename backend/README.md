# Backend (FastAPI)

Serves the JSON artifacts produced by the analytics notebook. See [`../docs/DATA_CONTRACT.md`](../docs/DATA_CONTRACT.md) for the endpoints and schemas.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload --port 8000      # docs at http://localhost:8000/docs
pytest -q
ruff check ..
```

| File | Purpose |
|---|---|
| `app/main.py` | FastAPI app and routes (`app` is the Vercel entrypoint) |
| `app/store.py` | loads + caches the JSON files (`data/<file>` wins over `data/sample/<file>`) |
| `app/analyzer.py` | lite live analyzer behind `POST /api/analyze` |
| `app/config.py` | env-var configuration (`HOMELENS_DATA_DIR`, `CORS_ORIGINS`) |
| `app/data/sample/` | committed synthetic artifacts (used by tests and when no real data is present) |
| `tests/` | pytest suite — add a test with every route |

Environment variables: see [`.env.example`](.env.example). Deployment: [`../docs/DEPLOYMENT.md`](../docs/DEPLOYMENT.md).
