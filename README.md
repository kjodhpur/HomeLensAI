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
notebooks/HomeLensAI_Final_Project.ipynb   ← THE course deliverable: full analysis, runs top-to-bottom
data/                                      ← how to get the Yelp data (not committed) + a synthetic sample
backend/                                   ← FastAPI service that serves the notebook's JSON outputs      → Vercel project #1
frontend/                                  ← Next.js (App Router, TypeScript) dashboard                   → Vercel project #2
scripts/                                   ← make_sample_data.py, sync_artifacts.py
docs/                                      ← TEAM_GUIDE · DATA_CONTRACT · DEPLOYMENT · SUBMISSION
```

```
 Yelp data ──► notebook (offline analytics: spaCy, scikit-learn, DistilBERT)
                  │  Section 9 writes 3 JSON files  (docs/DATA_CONTRACT.md)
                  ▼
   scripts/sync_artifacts.py ──► backend/app/data/*.json
                                       │  FastAPI  (/api/providers, /api/providers/{id}, /api/summary, /api/analyze …)
                                       ▼
                                 frontend (Next.js)  ── browser
```

The heavy NLP never runs on Vercel (size and time limits): the notebook is the **offline pipeline**, the API is a thin **serving layer** over its outputs.

## Quick start

> Requires Python 3.10+ and Node 20+. `make help` lists shortcuts.

**1. Run the API + web app on the sample data (no Yelp data needed — start here if you are on the front/back end):**
```bash
# terminal 1 — backend on http://localhost:8000  (interactive docs at /docs)
cd backend && python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload --port 8000
pytest -q                      # 13 tests

# terminal 2 — frontend on http://localhost:3000
cd frontend && cp .env.example .env.local && npm install && npm run dev
```

**2. Run the notebook (analytics):**
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && python -m spacy download en_core_web_sm
# put HomeLens_Yelp_HomeServices.csv in data/raw/   (see data/README.md) — otherwise it runs on the synthetic sample in DEMO MODE
jupyter lab notebooks/HomeLensAI_Final_Project.ipynb
```
On **Google Colab**: `!git clone https://github.com/kjodhpur/HomeLensAI.git`, open the notebook, upload the CSV to `HomeLensAI/data/raw/`, switch to a **T4 GPU runtime** for DistilBERT
(skipped automatically without a GPU), and uncomment the install cell at the top.

**3. Refresh the web app after a real notebook run:**
```bash
python scripts/sync_artifacts.py     # data/processed/*.json → backend/app/data/
```

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
| Backend API | ✅ scaffold with 6 endpoints + tests; ready to extend |
| Frontend | ✅ scaffold (dashboard, provider detail, live review analyzer); charts and polish are open tasks |
| CI | ✅ GitHub Actions: backend tests, frontend build, notebook smoke run |
| Vercel | see `docs/DEPLOYMENT.md` |

## Data & ethics
The Yelp Open Dataset may be used for academic purposes but **not redistributed** — the repo contains only a synthetic sample. Reviews are unverified allegations; keep the disclaimer visible in every UI and slide.
