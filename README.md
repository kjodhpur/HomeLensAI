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
artifacts/                                 ← Rithik's anonymized results from the real Yelp run (CSV tables, metadata, TF-IDF model files)
app/ · views/ · streamlit_app.py           ← Rithik's risk logic (app/risk_logic.py) + the Streamlit command center
frontend/                                  ← the Next.js product website + live demo — ONE self-contained app, no separate backend    → Vercel
notebooks/                                 ← analysis notebooks (final project notebook, EDA)
data/                                      ← how to get the Yelp data (not committed) + a synthetic sample for the notebook
scripts/                                   ← build_artifacts.py, export_frontend_data.py, make_sample_data.py
docs/                                      ← TEAM_GUIDE · DATA_CONTRACT · DEPLOYMENT · SUBMISSION
```

```
 Yelp data ──► scripts/build_artifacts.py ──► artifacts/*.csv, *.joblib, metadata.json   (+ app/risk_logic.py)
                                                │
                       ┌────────────────────────┴────────────────────────┐
                       ▼                                                 ▼   scripts/export_frontend_data.py
          Streamlit app (streamlit_app.py)                  frontend/data/*.json  (providers, KPIs, aspects, TF-IDF model, phrase patterns)
                                                                         │
                                                                         ▼   imported by the Next.js app
                                                   frontend/  — pages read the JSON; POST /api/analyze (a Next.js route handler)
                                                                runs a TypeScript port of Rithik's masking + phrase dictionary + TF-IDF model
```

There is **no separate API or backend**. The web app is one Vercel project (root directory `frontend/`) that ships Rithik's data and runs his review analysis itself.
A parity test (`npm test`) checks that the TypeScript port reproduces his Python model's probabilities and complaint aspects. Providers are always anonymized `Provider_XXXX` codes.

## Quick start

> Requires Node 20+ (Python only if you re-export the data). `make help` lists shortcuts.

**1. Run the website and live demo (no Yelp data, no backend, no env vars):**
```bash
cd frontend && npm install && npm run dev      # http://localhost:3000
npm test                                       # parity tests vs Rithik's Python model
npm run typecheck && npm run build
```
After rebuilding `artifacts/` (or editing `app/risk_logic.py`), regenerate the app's data and commit it:
```bash
pip install "scikit-learn==1.8.0" joblib
python scripts/export_frontend_data.py         # artifacts/ + app/risk_logic.py → frontend/data/*.json
```

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
python scripts/export_frontend_data.py   # artifacts/ + app/risk_logic.py → frontend/data/
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
One Vercel project, **Root Directory = `frontend`**, framework Next.js, no environment variables. Steps and troubleshooting: [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md).

## For teammates
* **[`docs/TEAM_GUIDE.md`](docs/TEAM_GUIDE.md)** — who builds what, the backlog, branch/PR workflow, definition of done.
* **[`docs/DATA_CONTRACT.md`](docs/DATA_CONTRACT.md)** — what the web app ships (`frontend/data/`), the analysis route and how it is tested.
* **[`docs/SUBMISSION.md`](docs/SUBMISSION.md)** — rubric → notebook map and the pre-submission checklist.

## Status
| Piece | State |
|---|---|
| Notebook (all 3 layers, EDA, dashboard, export) | ✅ complete; verified end-to-end on the synthetic sample and on two package-version sets (pandas 2.2 / 3.0). **Needs one run on the real Yelp data** (see `docs/SUBMISSION.md`) |
| Web app engine | ✅ Rithik's masking, phrase dictionary and TF-IDF model ported to TypeScript inside the Next.js app; 14 parity tests against his Python outputs |
| Frontend | ✅ product website (home, product, methodology, pricing, Responsible AI, docs, about, FAQ, contact, changelog, legal) plus the live demo at `/demo`: KPI cards, risk leaderboard, aspect radar, evidence feed, triage dock |
| Streamlit app | ✅ five pages, TF-IDF fallback live; DistilBERT activates once the model is on Hugging Face |
| CI | ✅ GitHub Actions: frontend typecheck + parity tests + build, data-export freshness check, notebook smoke run |
| Vercel | one project (root `frontend`) — see `docs/DEPLOYMENT.md` |

## Data & ethics
The Yelp Open Dataset may be used for academic purposes but **not redistributed** — the repo contains only a synthetic sample. Reviews are unverified allegations; keep the disclaimer visible in every UI and slide.
