# Deployment (Vercel)

One GitHub repo → **two Vercel projects**, because the repo is a monorepo with two apps:

| Vercel project | Root Directory | Framework | Runs |
|---|---|---|---|
| `homelensai-api` | `backend` | FastAPI (Python, auto-detected from `app/main.py`) | the REST API |
| `homelensai-web` | `frontend` | Next.js (auto-detected) | the dashboard |

The notebook is **not** deployed — it is the offline analytics pipeline. Its three JSON outputs are the only thing the API needs.

## 1. Connect (one-time, in the Vercel dashboard — projects are NOT imported yet)
In Vercel → *Add New… → Project → Import* the GitHub repo `kjodhpur/HomeLensAI`, **twice**, setting *Root Directory* to `backend` the first time and `frontend` the second.
Suggested names: `homelensai-api` and `homelensai-web`. Leave build/install commands on their defaults. Grant the Vercel GitHub app access to the repo if prompted.
Until `main` contains the code, preview-deploy this branch (it builds on every push); production deploys start once the work is merged to `main`. (The Vercel Git integration then builds every push: `main` → Production, every other branch and PR → a Preview URL.)

## 2. Environment variables
| Project | Variable | Value | Notes |
|---|---|---|---|
| web | `API_BASE_URL` | `https://<api-project-domain>` (no trailing slash) | used by server components **and** the `/api/*` rewrite; set for Production *and* Preview |
| api | `CORS_ORIGINS` | `https://<web-project-domain>` | only needed if browsers call the API directly; the web app proxies `/api/*` itself |
| api | `HOMELENS_DATA_DIR` | *(optional)* | only if the JSON files live outside `backend/app/data/` |

After changing a variable, **redeploy** (Deployments → ⋯ → Redeploy) — Vercel reads env vars at build time.
Locally the same names go in `frontend/.env.local` and `backend/.env`.

## 3. Check it works
```bash
curl https://<api-project-domain>/api/health            # {"status":"ok","data_mode":"sample",…}
curl https://<api-project-domain>/docs                  # interactive API docs
open https://<web-project-domain>                        # dashboard with the SAMPLE banner
```
If the dashboard shows "Could not load data", `API_BASE_URL` is missing or points at the wrong project. Preview deployments of a branch use *Preview* env vars — make sure they are set too.
If a preview of the API returns 401, **Vercel Deployment Protection** is on for previews: either use the production URL for `API_BASE_URL`, or turn protection off for the API project (Settings → Deployment Protection).

## 4. Putting the real data online — read the licence note first
`backend/app/data/*.json` (real results) is **git-ignored on purpose**. The files contain review sentences from the Yelp Open Dataset, whose licence does not allow redistributing the data.
Options, safest first:
1. **Demo with the synthetic sample** (default — it is committed and deployed automatically). Show real numbers in the notebook/slides only.
2. Deploy the real JSON from a **private** repository / private Vercel project only, after checking the Yelp terms (academic use is generally fine; public redistribution is not). To do so remove the `backend/app/data/*.json` line from `.gitignore`, run `python scripts/sync_artifacts.py`, and commit.
3. Strip the `evidence[].sentence` text from the export (keep counts, scores and trends) and serve only the aggregates.

## 5. Updating the deployed data
`notebook → python scripts/sync_artifacts.py → git commit → push`. Vercel redeploys the API automatically with the new files.

## Notes
* Vercel Python functions have a **~250 MB** size limit and short execution limits — the reason spaCy/DistilBERT stay in the notebook and the API only depends on `fastapi` and `vaderSentiment`.
* `POST /api/analyze` is a *lite* analyzer for demos; for production-grade scoring run the notebook pipeline offline.
* Rollbacks: Vercel → Deployments → *Promote to Production* on an earlier deployment.
