# Web app data & analysis — what the frontend ships and how it is tested

The dashboard is one Next.js app with **no separate backend**. Everything it shows comes from Rithik's work:

| Source (single source of truth) | → exported by `scripts/export_frontend_data.py` to | Used by |
|---|---|---|
| `artifacts/provider_risk_dashboard.csv`, `provider_yearly_risk.csv` | `frontend/data/providers.json` | leaderboard, trajectory chart, triage dock |
| `artifacts/corpus_timeline.csv`, `service_risk_summary.csv`, `model_comparison.csv`, `metadata.json` | `frontend/data/overview.json` | KPI pods and sparklines |
| `artifacts/aspect_summary.csv` + `app/risk_logic.py` (phrases, recommendations) | `frontend/data/aspects.json` | aspect radar blob and bubble |
| `app/risk_logic.py` (masking rules, compiled phrase regexes, thresholds) + `metadata.json` (`tfidf_threshold`) | `frontend/data/risk_config.json` | review analysis |
| `artifacts/homelens_tfidf_*.joblib` | `frontend/data/tfidf_model.json` (vocabulary, idf, coefficients, stop words) | review analysis |
| `app/config.py` `NOTEBOOK_FACTS` | `frontend/data/facts.json` | corpus size, splits and thresholds shown on the website |
| the above, run through his Python code on sample reviews | `frontend/data/golden.json` | `npm test` |

`python scripts/export_frontend_data.py` regenerates all of it; `--check` (used by CI) fails if the committed files are stale.
**Never edit `frontend/data/*.json` by hand** — change `artifacts/` or `app/risk_logic.py` and re-export.

Rules inherited from `CLAUDE.md`: providers are **anonymized** (`Provider_XXXX`, no names or business ids); monitoring needs **≥ 20 reviews**; use *review-based risk signal, management attention,
relative concern tier, human investigation* — never claim fraud, liability, verified misconduct or bankruptcy prediction.
Tiers (by risk score): **Stable** < 50 · **Watch** 50–75 · **Elevated** 75–90 · **High concern** ≥ 90. Trend = change in mean model risk, 2021+ vs 2020 (**Rising** > +0.05, **Improving** < −0.05).

## Types
`frontend/lib/types.ts` (`Provider`, `Overview`, `Aspect`, `AnalyzeResult`, …) describes the JSON. Rates are fractions in 0–1.

## `POST /api/analyze` (a Next.js route handler: `frontend/app/api/analyze/route.ts`)
Body `{ "text": "<3–5000 characters>" }` → `AnalyzeResult`, 400 on invalid input. Implemented in `frontend/lib/engine/` as a TypeScript port of Rithik's code:

| File | Ports |
|---|---|
| `lib/engine/text.ts` | `mask_sensitive_and_leakage`, `extract_aspects` / `matched_phrases`, `recommend_action` (patterns come from `risk_config.json`, not re-typed) |
| `lib/engine/tfidf.ts` | scikit-learn `TfidfVectorizer` (lowercase, accent stripping, English stop words, 1–2-grams, sublinear tf, idf, l2) + logistic regression |
| `lib/engine/analyze.ts` | `analyze_review`, plus the per-sentence breakdown, evidence sentence and token weights shown in the Evidence Feed |

```jsonc
{
  "model": { "name": "TF–IDF Logistic Regression", "threshold": 0.585, "available": true, "is_primary": false, "note": "…" },
  "risk_probability": 0.9629, "operating_threshold": 0.585, "management_attention": true,
  "primary_aspect": "Pricing / Billing", "detected_aspects": ["Pricing / Billing", "Timeliness", "Workmanship"],
  "matched_phrases": { "Timeliness": ["hours late"] },
  "recommended_action": "Review estimate accuracy, …",            // "Routine monitoring…" below the threshold
  "sentences": [ { "index": 0, "start": 0, "end": 112, "text": "…", "risk_probability": 0.96, "flagged": true, "aspects": [], "matched_phrases": {} } ],
  "evidence": { "index": 0, "sentence": "…", "aspect": "…", "matched_phrases": {}, "risk_probability": 0.96, "has_dictionary_match": true },
  "weights": { "bias": -0.19, "logit": 3.26, "terms": [ { "term": "failed", "label": "failed", "weight": 0.9 } ], "explained_positive": 3.7, "explained_negative": -0.25 },
  "masking_applied": false, "disclaimer": "…"
}
```
* Text is masked (URLs, emails, phones, dollar amounts, star phrases) before scoring.
* `sentences[].flagged` = sentence-level probability ≥ the review-level threshold (an approximation: the model was trained on whole reviews).
* `evidence` = the sentence carrying a dictionary match (highest risk first); otherwise the riskiest sentence.
* `weights.terms` are exact logit contributions (tf-idf × coefficient); `logit = bias + Σ all terms`.
* Rithik's primary model, fine-tuned DistilBERT, is **not** bundled (size); the app serves his TF-IDF fallback and always shows `model.name`, so numbers are never mislabelled.

## Parity test
`npm test` (in `frontend/`) runs `tests/engine.test.ts`: for 11 sample reviews it asserts the TypeScript port reproduces Python's probability (±1e-4), decision, primary aspect, detected aspects,
matched phrases, recommended action and sentence probabilities. If you change `app/risk_logic.py` or retrain the model, re-export and re-run it.
