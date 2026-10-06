# Submission guide — Final Project Deliverables & Grading Rubric

Deliverables: **(1) presentation slides** and **(2) the Python notebook(s) or a GitHub link** — this repository, notebook `notebooks/HomeLensAI_Final_Project.ipynb`.
Presentation: ~12–15 minutes.

## Rubric → where it is addressed in the notebook
| Criterion (weight) | Notebook section | What to point at in the talk |
|---|---|---|
| **Business problem (15 %)** | §1 | stakeholders table, "stars hide the cause", research questions RQ1–RQ4, success criteria, the allegation caveat |
| **EDA (10 %)** | §3 (cleaning log, category audit) and §4 | label imbalance, review length, time/volume, provider long tail, trade table with CIs, log-odds vocabulary |
| **NLP methodology (25 %)** | §5 (3 sentiment models, threshold tuning, bootstrap CIs, provider-held-out check) and §6 (PhraseMatcher + Matcher + EntityRuler, gates, unit tests, audit) | *why* each method; baseline → classical → transformer; rules as explainable layer |
| **Results & business insights (25 %)** | §5.6–5.7, §6.7–6.10, §7 (incl. temporal backtest), §8 dashboard + insights | negative-class recall, aspect lift, "good stars but recurring issue", worsening providers, actions per stakeholder |
| **Presentation (10 %)** | slides | one slide per layer + dashboard demo (the web app is a bonus) |
| **Code clarity & quality (15 %)** | whole notebook + repo | single CONFIG cell, helper functions, unit-tested rules, seeds, caching, docs, CI |

## Before you submit — checklist
The notebook in this repo was developed and verified on a **synthetic sample** (no access to the Yelp files). It runs end-to-end, but the committed copy has **no outputs**, and its commentary
that depends on numbers is computed at run time. So:

1. [ ] Put the Yelp zip files (or `HomeLens_Yelp_HomeServices.csv`) in `data/raw/` (see `data/README.md`). Confirm the data cell prints **data mode: raw_json** (or *extract*) and *no* DEMO banner.
2. [ ] **Check the provider filter** (§3). The proposal expects ≈16,000 reviews from ≈926 true providers after narrowing 23,685 reviews / 1,403 businesses. Compare the cleaning log; if the counts differ a lot, look at the
       "most common categories on EXCLUDED businesses" table and adjust `TRADE_RULES` / `NON_PROVIDER_TOKENS`.
3. [ ] Run on a machine with a **GPU** (NVIDIA CUDA or Apple-silicon) so DistilBERT trains (≈10–20 min). Without a GPU it is skipped and the comparison has two models, not three. If nobody has one, run it once on a lab/cloud GPU box — the predictions are cached in `data/cache/`.
4. [ ] Read every auto-generated *Takeaway* / *Reading the table* paragraph against the real numbers; add a short markdown cell wherever a result surprises you. Check the "Layer 1 gates" and "Success criteria" claims in §1.5 (targets: risk recall ≥ 0.90, audit precision ≥ 0.80).
5. [ ] **Label the aspect audit** (`data/annotation/aspect_audit.csv`, ~120 rows, two people independently), re-run §6.9. If an aspect scores < 80 %, fix its cues and add `RULE_TESTS` rows (§6.5).
6. [ ] Use the "unexplained flagged reviews" phrases in §6.8 to add missing cues — then re-run (the cache invalidates itself when the lexicon changes).
7. [ ] **Kernel → Restart & Run All** must finish with no errors. Then *download the executed notebook* (File → Download → .ipynb) and commit it over `notebooks/HomeLensAI_Final_Project.ipynb` so the graders see outputs
       (or submit the GitHub link *and* an HTML export: `jupyter nbconvert --to html`).
8. [ ] For the live demo run the web app (`cd frontend && npm run dev`, or the Vercel URL). It ships Rithik's real anonymized artifacts; re-run `python scripts/export_frontend_data.py` if you rebuilt `artifacts/` or changed `app/risk_logic.py`.
9. [ ] Make sure no data, keys or `.env` files are committed (`git status`, `.gitignore`).

## Slide outline (12–15 min)
1. Problem & stakeholders (1.5) → 2. Data & cleaning (1) → 3. EDA highlights (2) → 4. Layer 1: three models, recall-first evaluation (2.5) → 5. Layer 2: aspects with evidence (2.5) →
6. Layer 3: provider profiles, backtest (2) → 7. Dashboard demo (2) → 8. Limitations, ethics, next steps (1).
