# Team guide — the web app

**Architecture in one line:** Rithik's `artifacts/` + `app/risk_logic.py` → `scripts/export_frontend_data.py` → `frontend/data/*.json` → one Next.js app (pages + a `/api/analyze` route handler). No separate backend.
Read the README first, then [`DATA_CONTRACT.md`](DATA_CONTRACT.md).

## Get running in 2 minutes
```bash
git clone https://github.com/kjodhpur/HomeLensAI.git && cd HomeLensAI/frontend
npm install && npm run dev          # http://localhost:3000
npm test                            # parity tests vs Rithik's Python model
```
No data download, no env vars, no second service. The app shows the **real anonymized artifacts**. After rebuilding `artifacts/` or editing `app/risk_logic.py`:
`python scripts/export_frontend_data.py` (needs `scikit-learn==1.8.0`, `joblib`), commit the changed `frontend/data/*.json`.

## Backlog (frontend)
- [ ] More views from `overview.json`: tier distribution, service-group benchmark, model-comparison table.
- [ ] Deep-link a provider (`/?provider=Provider_0545`); export the filtered watchlist as CSV.
- [ ] Persist leaderboard filters in the URL; keyboard navigation (arrow keys) in the leaderboard.
- [ ] Mobile layout (the design targets desktop), loading skeletons, an accessibility pass (tiers always carry a text label — keep it that way).
- [ ] Per-keyword frequencies in the aspect bubble — needs `scripts/build_artifacts.py` to export per-phrase counts (today it shows cluster totals).
- [ ] DistilBERT scoring: would need a hosted inference endpoint (e.g. Hugging Face); the route handler could call it and fall back to the bundled TF-IDF model.
- [ ] Keep the allegation disclaimer visible (`components/DisclaimerEtch.tsx`) — do not remove it.

## Working agreement
* **Branches:** `feat/<short-name>`; small PRs; every PR gets a Vercel preview URL (add a screenshot for UI changes). Merging to `main` deploys to production.
* **CI must be green:** frontend `typecheck` + `npm test` + `build`, `export_frontend_data.py --check`, notebook smoke run. Run `make test` before pushing.
* **Data changes** go through `artifacts/` / `app/risk_logic.py` and a re-export — never edit `frontend/data/*.json` by hand.
* **Never commit:** the raw Yelp CSV/zips, `.env*` files, API keys.
* **Definition of done:** works with the real artifacts, a test (engine) or a screenshot (UI), docs updated, preview deploy checked.

## Where things live
| I want to … | Look at |
|---|---|
| change how risk is scored / a complaint phrase | `app/risk_logic.py`, `scripts/build_artifacts.py`, then `export_frontend_data.py` + `npm test` |
| change the review analysis behaviour | `frontend/lib/engine/*.ts` (keep parity with Python; add a golden sample in `scripts/export_frontend_data.py`) |
| add a page / component | `frontend/app/`, `frontend/components/` |
| change colours, glass, easings | `frontend/app/base.css` (tokens at the top), `frontend/app/site.css` (website), `frontend/app/demo/demo.css` (demo) |
| change a data field | `scripts/export_frontend_data.py` → `frontend/lib/types.ts` → components |
