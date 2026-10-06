# HomeLens AI — NLP-based risk intelligence for home-service providers

**CIS 509 · Analytics for Unstructured Data · Final course project**
Team: Rithik Roy Thati · Kanha Jodhpurkar · Sankalp Sharma Madgula · Dev Bhattacharyya

HomeLens AI reads free-form Yelp reviews of home-service providers (plumbers, electricians, HVAC, roofers, movers, contractors …) and turns them into
**structured risk intelligence**: *is this review a risk signal? what exactly went wrong (with the evidence sentence)? does it keep happening at this provider, and what should be done?*
Reviews are customer allegations, so every output is a **"complaint signal detected"**, never a finding of wrongdoing.

| Layer | Question | Method |
|---|---|---|
| 1 · Sentiment | Is this review a risk signal? | VADER baseline → TF-IDF + Logistic Regression → fine-tuned DistilBERT (1–2★ vs 4–5★; 3★ held out) |
| 2 · Aspects | *What* went wrong — and show the proof | spaCy `PhraseMatcher` + `Matcher` + `EntityRuler` over 8 aspects (workmanship, reliability, pricing, communication, timeliness, professionalism, warranty, safety) |
| 3 · Providers | Does it keep happening? What now? | recurrence, recent-vs-prior trend (Fisher test), severity-weighted score, tier, recommended action; temporal backtest |

## What is in this repo

```
notebooks/HomeLensAI_Final_Project.ipynb   ← course notebook: full analysis, runs top-to-bottom (also FinalProject_HomeLensAI.ipynb, EDA notebooks)
artifacts/                                 ← anonymized results of the real Yelp run (CSV tables, metadata, TF-IDF model files) — the app's single data source
app/ · views/ · streamlit_app.py           ← risk logic (app/risk_logic.py) + the Streamlit command center
backend/                                   ← FastAPI service over artifacts/ + risk_logic (serves the web app)                    → Vercel project #1
frontend/                                  ← Next.js "liquid glass" dashboard (TypeScript, no UI library)                          → Vercel project #2
data/                                      ← how to get the Yelp data (not committed) + a synthetic sample for the notebook
scripts/                                   ← build_artifacts.py, sync_artifacts.py, make_sample_data.py
docs/                                      ← TEAM_GUIDE · DATA_CONTRACT (API) · DEPLOYMENT · SUBMISSION
```

```
 Yelp data ──► scripts/build_artifacts.py ──► artifacts/*.csv, *.joblib, metadata.json
                                                │
                       ┌────────────────────────┴───────────────┐
                       ▼                                        ▼  scripts/sync_artifacts.py (vendors risk_logic.py + artifacts/)
          Streamlit app (streamlit_app.py)           backend/  FastAPI  (/api/overview, /api/providers, /api/aspects, /api/analyze …)
                                                                 │
                                                                 ▼
                                                    frontend/  Next.js liquid-glass dashboard  ── browser
```

The heavy NLP never runs on Vercel (size and time limits). The API serves precomputed tables and scores single reviews with the small TF-IDF model; DistilBERT stays in the notebook / Streamlit app.
Providers are always shown as anonymized `Provider_XXXX` codes.

## Quick start

> Requires Python 3.10+ and Node 20+. `make help` lists shortcuts.

**1. Run the API + the liquid-glass web app (uses `artifacts/` — no Yelp data needed; start here if you are on the front/back end):**
```bash
# terminal 1 — backend on http://localhost:8000  (interactive docs at /docs)
cd backend && python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload --port 8000
pytest -q                      # 19 tests

# terminal 2 — frontend on http://localhost:3000
cd frontend && cp .env.example .env.local && npm install && npm run dev
```
After changing `app/risk_logic.py` or rebuilding `artifacts/`, run `python scripts/sync_artifacts.py` (the backend deploys with `backend/` as its root, so it carries vendored copies; a test fails if they drift).

**1b. The Streamlit command center:** `pip install -r requirements.txt && streamlit run streamlit_app.py`

**2. Run the notebook (analytics) on the real Yelp data:**
```bash
python -m venv .venv && source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt && python -m spacy download en_core_web_sm
# Drop the Yelp download into data/raw/ — the .zip files exactly as downloaded, NO unzipping needed (see data/README.md)
jupyter lab notebooks/HomeLensAI_Final_Project.ipynb        # Kernel → Restart & Run All
```
Without any data in `data/raw/` the notebook runs on the synthetic sample in DEMO MODE. DistilBERT needs a GPU (NVIDIA CUDA or Apple-silicon MPS) and is skipped automatically otherwise
(`HOMELENS_RUN_DISTILBERT=1` forces it on CPU — slow).

**3. Refresh the web app after rebuilding the artifacts:**
```bash
python scripts/build_artifacts.py    # from the raw Yelp CSV (git-ignored) → artifacts/
python scripts/sync_artifacts.py     # artifacts/ + app/risk_logic.py → backend/
```

## Streamlit command center (`streamlit_app.py`)
A self-contained Streamlit product built on the final notebook's validated results: **Executive Overview**, **Review Analyzer**,
**Provider Monitor**, **Model Performance** and **Responsible AI** pages, with a custom design system (animated metrics and risk gauge,
insight carousel, page transitions). It reads only the anonymized tables in `artifacts/`.

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py        # http://localhost:8501
pytest tests -q                       # 27 tests (risk logic + artifacts)
```

* **Models:** fine-tuned DistilBERT from Hugging Face when `HF_MODEL_ID` is set in `.streamlit/secrets.toml` (template:
  `.streamlit/secrets.toml.example`, also needs `pip install -r requirements-bert.txt`); otherwise it falls back automatically to the
  TF-IDF model in `artifacts/`. The sidebar shows which model is live.
* **Artifacts:** `python scripts/build_artifacts.py` rebuilds `artifacts/` from `data/raw/HomeLens_Yelp_HomeServices.csv`.
* **Deploy:** Streamlit Community Cloud, select repository → branch `main` → main file `streamlit_app.py`, Python 3.12, and paste secrets.
* **Code:** `streamlit_app.py` (navigation), `app/` (risk logic, model loader, charts, UI components), `views/` (one module per page), `tests/`.

## Deploying to Vercel
Two Vercel projects from this one repo (**root directory** `frontend/` and `backend/`). Step-by-step, environment variables and the data-licence note are in [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md).

## For teammates
* **[`docs/TEAM_GUIDE.md`](docs/TEAM_GUIDE.md)** — who builds what, the backlog, branch/PR workflow, definition of done.
* **[`docs/DATA_CONTRACT.md`](docs/DATA_CONTRACT.md)** — the exact JSON schema the backend and frontend share.
* **[`docs/SUBMISSION.md`](docs/SUBMISSION.md)** — rubric → notebook map and the pre-submission checklist.

## Status
| Piece | State |
|---|---|
| Notebook (all 3 layers, EDA, dashboard, export) | ✅ complete; verified end-to-end on the synthetic sample and on two package-version sets (pandas 2.2 / 3.0). **Needs one run on the real Yelp data** (see `docs/SUBMISSION.md`) |
| Backend API | ✅ FastAPI over the real artifacts (overview, providers, aspects, review analysis) + 19 tests |
| Frontend | ✅ liquid-glass dashboard: KPI pods, risk leaderboard, aspect radar blob, evidence feed, action-triage dock |
| Streamlit app | ✅ five pages, TF-IDF fallback live; DistilBERT activates once the model is on Hugging Face |
| CI | ✅ GitHub Actions: backend tests, frontend build, notebook smoke run |
| Vercel | ⏳ **not connected yet** — the two projects must be imported once in the Vercel dashboard (≈5 min, steps in `docs/DEPLOYMENT.md`); the repo is already configured for it |

## Data & ethics
The Yelp Open Dataset may be used for academic purposes but **not redistributed** — the repo contains only a synthetic sample. Reviews are unverified allegations; keep the disclaimer visible in every UI and slide.
