# Deployment (Vercel)

One GitHub repo → **two Vercel projects**, because the repo is a monorepo with two apps:

| Vercel project | Root Directory | Framework | Runs |
|---|---|---|---|
| `homelensai-api` | `backend` | FastAPI (Python, auto-detected from `app/main.py`) | the REST API |
| `homelensai-web` | `frontend` | Next.js (auto-detected) | the dashboard |

The notebook and the Streamlit app are **not** deployed here. The API only needs the vendored `artifacts/` and `risk_logic.py`.

## 1. Connect (one-time, in the Vercel dashboard — projects are NOT imported yet)
In Vercel → *Add New… → Project → Import* the GitHub repo `kjodhpur/HomeLensAI`, **twice**, setting *Root Directory* to `backend` the first time and `frontend` the second.
Suggested names: `homelensai-api` and `homelensai-web`. Leave build/install commands on their defaults. Grant the Vercel GitHub app access to the repo if prompted.
Until `main` contains the code, preview-deploy this branch (it builds on every push); production deploys start once the work is merged to `main`. (The Vercel Git integration then builds every push: `main` → Production, every other branch and PR → a Preview URL.)

## 2. Environment variables
| Project | Variable | Value | Notes |
|---|---|---|---|
| web | `API_BASE_URL` | `https://<api-project-domain>` (no trailing slash) | used by server components **and** the `/api/*` rewrite; set for Production *and* Preview |
| api | `CORS_ORIGINS` | `https://<web-project-domain>` | only needed if browsers call the API directly; the web app proxies `/api/*` itself |
| api | `HOMELENS_ARTIFACTS_DIR` | *(optional)* | only if the artifacts live outside `backend/app/data/artifacts/` |
| api | `HOMELENS_DISABLE_MODEL` | *(optional)* `1` | serve dictionary-only analysis (no scikit-learn) |

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

## 4. Data on Vercel
The deployed API ships `backend/app/data/artifacts/` — **anonymized aggregates** (provider codes, scores, yearly risk) and the small TF-IDF model; it contains no raw Yelp reviews, names or business ids.
The `/api/analyze` endpoint scores text the *visitor* pastes; the bundled example reviews are synthetic. Update flow: `python scripts/build_artifacts.py` → `python scripts/sync_artifacts.py` → commit → push, and Vercel redeploys.

## 5. Size and runtime
The API needs `scikit-learn==1.8.0` (+ numpy/scipy) to score reviews — roughly 200–250 MB unpacked, inside Vercel's Python function limit. If a build ever exceeds it, set
`HOMELENS_DISABLE_MODEL=1` (the API then serves dictionary-only analysis) or move scoring to a separate service. `backend/requirements.txt` pins scikit-learn to the version that wrote the joblib files.

## Notes
* DistilBERT stays out of the API (size/time limits); the web UI always labels the model that produced a score.
* Rollbacks: Vercel → Deployments → *Promote to Production* on an earlier deployment.
