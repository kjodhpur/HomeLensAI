# Deployment (Vercel)

**One** Vercel project. The dashboard is a self-contained Next.js app (`frontend/`): it ships Rithik's anonymized data as static JSON and runs the review analysis in its own route handler.
There is no API project, no backend and **no environment variables**.

## 1. Project settings (Vercel dashboard → the project → Settings)
| Setting | Value |
|---|---|
| Root Directory | `frontend` *(its own Save button; leave "Include source files outside of the Root Directory" off)* |
| Framework Preset | Next.js |
| Build / Install / Output | auto-detect — switch every "Override" off |
| Node.js Version | 22.x *(also pinned in `frontend/package.json`)* |
| Production Branch | `main` |
| Deployment Protection | off, if classmates should open it without a Vercel login |

Every push to `main` builds a Production deployment; other branches and PRs get a Preview URL.

## 2. Check it works
A correct build log shows `Installing dependencies…` and `Running "npm run build"` (~20 s) with a route table containing `○ /` and `ƒ /api/analyze`.
```bash
open https://<project>.vercel.app
curl -s -X POST https://<project>.vercel.app/api/analyze -H 'content-type: application/json' \
  -d '{"text":"They never showed up and overcharged me."}'
```

## 3. Troubleshooting
| Symptom | Cause |
|---|---|
| `404 NOT_FOUND` on every URL, build finishes in ~100 ms | Root Directory is not `frontend` (Vercel built the repo root, which has no `package.json`) |
| 404 although the build compiled Next.js | Framework Preset is "Other" — set it to Next.js |
| Build fails with "Cannot find module '@/data/…json'" | `frontend/data/` is missing — run `python scripts/export_frontend_data.py` and commit |
| Login page instead of the site | Deployment Protection is on |

## 4. Data
`frontend/data/` holds only **anonymized aggregates** (provider codes, scores, yearly risk) and the small TF-IDF model — no raw Yelp reviews, names or business ids.
`/api/analyze` scores text the *visitor* pastes; the bundled example reviews are synthetic. Update flow:
`python scripts/build_artifacts.py` → `python scripts/export_frontend_data.py` → commit → push; Vercel redeploys.

## Notes
* DistilBERT is not bundled (size); the UI labels the model that produced each score.
* Rollbacks: Deployments → *Promote to Production* on an earlier deployment.
