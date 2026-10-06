# Team guide — how we build the web app

**Architecture in one line:** `artifacts/` (real Yelp results) → FastAPI (`backend/`) → the Next.js liquid-glass dashboard (`frontend/`); the Streamlit app reads the same artifacts. Read the README first, then [`DATA_CONTRACT.md`](DATA_CONTRACT.md).

## Get running in 5 minutes (no Yelp data needed)
```bash
git clone https://github.com/kjodhpur/HomeLensAI.git && cd HomeLensAI
# backend
cd backend && python -m venv .venv && source .venv/bin/activate && pip install -r requirements-dev.txt
uvicorn app.main:app --reload --port 8000        # http://localhost:8000/docs
# frontend (new terminal)
cd frontend && cp .env.example .env.local && npm install && npm run dev      # http://localhost:3000
```
You are looking at the **real anonymized artifacts** in `artifacts/` (copied into `backend/app/data/artifacts/`). After changing `app/risk_logic.py` or rebuilding artifacts: `python scripts/sync_artifacts.py`, then restart the backend.

## Tracks and backlog
Pick a track, open an issue per item, tick them off. Items are ordered by value for the final demo.

### Backend (`backend/`, FastAPI)
- [ ] Add `GET /api/trades` (per-trade mean score, tier counts) for a dashboard chart.
- [ ] Add `GET /api/providers/{code}/similar` — same trade, lower risk (homeowner use-case: "safer alternatives").
- [ ] Response caching headers (`Cache-Control`) — the data only changes when the notebook is re-run.
- [ ] Structured error responses + request logging; `GET /api/health` should report artifact age.
- [ ] Decide on storage if the JSON gets large: Vercel Blob / Supabase table instead of files in the repo (keep the same response shapes).
- [ ] Serve DistilBERT scoring (needs a GPU/inference endpoint, e.g. a Hugging Face Inference Endpoint) behind the same `/api/analyze` shape.
- [ ] Export per-phrase counts from `scripts/build_artifacts.py` so the aspect bubble can show per-keyword frequencies (today it shows the cluster total).

### Frontend (`frontend/`, Next.js + TypeScript)
- [ ] More views from `/api/overview`: tier distribution, service-group benchmark, model-comparison table (the liquid-glass dashboard has the KPI pods, leaderboard, aspect blob, evidence feed and triage dock).
- [ ] Deep-link a provider (`/?provider=Provider_0545`) and share/export the watchlist as CSV.
- [ ] Persist filters in the URL; keyboard navigation for the leaderboard (arrow keys).
- [ ] Mobile layout (the design targets desktop), loading skeletons, an accessibility pass (tiers always carry a text label; keep it that way).
- [ ] Keep the allegation disclaimer visible (the etched footer, `components/DisclaimerEtch.tsx`) — do not remove it.

### Notebook / data (owner: whoever holds the Yelp data)
- [ ] Run the notebook on the real extract (a GPU machine for DistilBERT) and review every computed takeaway (see `SUBMISSION.md`).
- [ ] Label the aspect-audit CSV (two people, independently) and re-run Section 6.9.
- [ ] Rebuild artifacts (`scripts/build_artifacts.py`) and run `python scripts/sync_artifacts.py`; never commit the raw Yelp CSV.

## Working agreement
* **Branches:** `feat/<track>-<short-name>` (e.g. `feat/frontend-trend-chart`). Never push to `main` directly.
* **Pull requests:** small, one concern each; the PR template lists the checks. Every PR gets a **Vercel preview URL** — put it in the PR description with a screenshot for UI changes.
* **CI must be green:** backend `ruff` + `pytest`, frontend `typecheck` + `build`, notebook smoke run. Run `make test` before pushing.
* **Contract changes** (JSON fields) touch the notebook export, `backend`, and `frontend/lib/types.ts` in the *same* PR, and update `DATA_CONTRACT.md`.
* **Never commit:** Yelp data, `.env*` files, API keys. Env vars live in Vercel / local `.env.local`.
* **Definition of done:** works on the sample data, has a test (backend) or a screenshot (frontend), docs updated, preview deploy checked.

## Where things live
| I want to … | Look at |
|---|---|
| change how risk is scored | `scripts/build_artifacts.py` / the final notebook — then rebuild + `scripts/sync_artifacts.py` |
| add a complaint phrase | `app/risk_logic.py` (`RISK_PHRASES`), add a test in `tests/test_risk_logic.py`, then `scripts/sync_artifacts.py` |
| add an API route | `backend/app/main.py` (+ a test in `backend/tests/test_api.py`) |
| add a page | `frontend/app/<route>/page.tsx` (server components fetch via `lib/api.ts`) |
| change a data field | `docs/DATA_CONTRACT.md` → `backend/app` → `frontend/lib/types.ts` |
