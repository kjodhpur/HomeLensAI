# Team guide — how we build the web app

**Architecture in one line:** the notebook produces three JSON files → FastAPI serves them → Next.js shows them. Read the README first, then [`DATA_CONTRACT.md`](DATA_CONTRACT.md).

## Get running in 5 minutes (no Yelp data needed)
```bash
git clone https://github.com/kjodhpur/HomeLensAI.git && cd HomeLensAI
# backend
cd backend && python -m venv .venv && source .venv/bin/activate && pip install -r requirements-dev.txt
uvicorn app.main:app --reload --port 8000        # http://localhost:8000/docs
# frontend (new terminal)
cd frontend && cp .env.example .env.local && npm install && npm run dev      # http://localhost:3000
```
You are looking at **synthetic sample data** (`backend/app/data/sample/`). When the real notebook run finishes: `python scripts/sync_artifacts.py` and restart the backend — the app switches to the
real data automatically (real files take precedence over `sample/`).

## Tracks and backlog
Pick a track, open an issue per item, tick them off. Items are ordered by value for the final demo.

### Backend (`backend/`, FastAPI)
- [ ] Add `GET /api/trades` (per-trade mean score, tier counts) for a dashboard chart.
- [ ] Add `GET /api/providers/{id}/similar` — same trade, lower risk (homeowner use-case: "safer alternatives").
- [ ] Response caching headers (`Cache-Control`) — the data only changes when the notebook is re-run.
- [ ] Structured error responses + request logging; `GET /api/health` should report artifact age.
- [ ] Decide on storage if the JSON gets large: Vercel Blob / Supabase table instead of files in the repo (keep the same response shapes).
- [ ] Extend the lite analyzer (`app/analyzer.py`) toward parity with the notebook (token patterns), and add tests for every new rule.

### Frontend (`frontend/`, Next.js + TypeScript)
- [ ] Dashboard charts (see `/api/summary`): tier donut, aspect prevalence bars, trend scatter (prior vs recent), model comparison table. A lightweight option: `recharts`.
- [ ] Provider page: yearly negative-rate line chart from `history`; evidence cards with the matched cue highlighted; "manager / homeowner" toggle for the action text.
- [ ] Filters in the URL (already server-side via query string) + sortable columns + pagination (`offset`).
- [ ] Mobile layout, loading/empty/error states, accessibility pass (colour is never the only signal for tiers).
- [ ] Keep the disclaimer visible on every page (it is in the footer — do not remove it).

### Notebook / data (owner: whoever holds the Yelp data)
- [ ] Run the notebook on the real extract (Colab T4 for DistilBERT) and review every computed takeaway (see `SUBMISSION.md`).
- [ ] Label the aspect-audit CSV (two people, independently) and re-run Section 6.9.
- [ ] `python scripts/sync_artifacts.py`, commit nothing from `data/processed/` (see licence note in `DEPLOYMENT.md`).

## Working agreement
* **Branches:** `feat/<track>-<short-name>` (e.g. `feat/frontend-trend-chart`). Never push to `main` directly.
* **Pull requests:** small, one concern each; the PR template lists the checks. Every PR gets a **Vercel preview URL** — put it in the PR description with a screenshot for UI changes.
* **CI must be green:** backend `ruff` + `pytest`, frontend `typecheck` + `build`, notebook smoke run. Run `make test` before pushing.
* **Contract changes** (JSON fields) touch the notebook export, `backend`, and `frontend/lib/types.ts` in the *same* PR, and update `DATA_CONTRACT.md`.
* **Never commit:** Yelp data, `data/processed/*`, `.env*` files, API keys. Env vars live in Vercel / local `.env.local`.
* **Definition of done:** works on the sample data, has a test (backend) or a screenshot (frontend), docs updated, preview deploy checked.

## Where things live
| I want to … | Look at |
|---|---|
| change how risk is scored | notebook Section 7 (`SCORE_WEIGHTS`, `profile_table`, `add_scores`) — then re-export |
| add a complaint phrase | notebook Section 6.1 (`ASPECTS`) and add a row to `RULE_TESTS` in 6.5 |
| add an API route | `backend/app/main.py` (+ a test in `backend/tests/test_api.py`) |
| add a page | `frontend/app/<route>/page.tsx` (server components fetch via `lib/api.ts`) |
| change a data field | `docs/DATA_CONTRACT.md` → notebook §9 → `backend` → `frontend/lib/types.ts` |
