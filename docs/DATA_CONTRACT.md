# API contract — artifacts → backend → frontend

The single source of data is the repo-level `artifacts/` folder (written by `scripts/build_artifacts.py` from the real Yelp run). `scripts/sync_artifacts.py` vendors it, together with
`app/risk_logic.py`, into `backend/` (Vercel deploys that folder on its own). The backend exposes it over HTTP; the frontend's TypeScript types are in `frontend/lib/types.ts`.
**If you change a field, change the backend (`app/artifacts.py` / `scoring.py`), `frontend/lib/types.ts`, the tests and this file in the same commit.**

Rules inherited from the project (`CLAUDE.md`): providers are **anonymized** (`Provider_XXXX`, never names or business ids); monitoring needs **≥ 20 reviews**; use the wording *review-based risk signal,
management attention, relative concern tier, human investigation* and never claim fraud, liability, verified misconduct or bankruptcy prediction.
Rates are fractions in 0–1. Interactive docs: `http://localhost:8000/docs`.

## Artifacts (`artifacts/`)
| File | Content |
|---|---|
| `provider_risk_dashboard.csv` | one row per monitored provider: `provider_code, service_group, reviews, observed_negative_rate, mean_risk_probability, recent_risk_probability, trend_delta, high_severity_rate, top_aspect, risk_score, risk_tier, recommended_action, recent_reviews, previous_reviews, latest_review` |
| `provider_yearly_risk.csv` | `provider_code, review_year, reviews, mean_risk_probability` |
| `aspect_summary.csv` | per complaint aspect: reviews with signal, share of corpus, negative rate when mentioned, lift vs corpus |
| `service_risk_summary.csv`, `service_group_eda.csv`, `corpus_timeline.csv`, `model_comparison.csv`, `tfidf_signal_terms.csv`, `metadata.json` | benchmark tables, yearly corpus stats, validated model metrics, model terms, run metadata (incl. the TF-IDF threshold) |
| `homelens_tfidf_*.joblib` | the TF-IDF vectorizer and logistic-regression model (scikit-learn **1.8.0**) |

Tiers (relative, by risk score): **Stable** < 50 · **Watch** 50–75 · **Elevated** 75–90 · **High concern** ≥ 90. Trend: change in mean model risk, 2021+ vs 2020 — **Rising** (> +0.05), **Improving** (< −0.05), **Steady**, **Insufficient data**.

## Endpoints
| Method & path | Returns |
|---|---|
| `GET /api/health` | `{status, providers, model, model_available, market}` |
| `GET /api/overview` | `{meta, kpis{reviews_analyzed, sentiment_shift, escalations}, tiers, tier_rules, services[], models[], timeline[], signal_terms}` — each KPI carries a `series` of `{x: year, y}` for its sparkline |
| `GET /api/aspects` | the 8 aspects: `{aspect, reviews_with_signal, share_of_corpus, negative_reviews_with_signal, negative_rate_when_mentioned, lift, high_severity, keywords[], recommended_action, providers_led}` — `keywords` is the phrase dictionary (the "keyword cluster") |
| `GET /api/providers` | `{total, limit, offset, items: Provider[]}`; query: `tier, service_group, aspect, trend, min_reviews (≥20), q, sort (risk_score\|reviews\|recent_risk\|trend_delta), limit (≤500), offset` |
| `GET /api/providers/{code}` | one `Provider` + `service_benchmark` (404 if unknown) |
| `GET /api/examples` | synthetic example reviews (complaint / positive) |
| `POST /api/analyze` `{text}` | review analysis, below |

### `Provider`
`code, service_group, reviews, observed_negative_rate, mean_risk, recent_risk | null, trend_delta | null, trend, high_severity_rate, top_aspect, risk_score (0–100), risk_tier, recommended_action,
recent_reviews, previous_reviews, latest_review | null, history: [{year, reviews, risk}]`

### `POST /api/analyze` response
```jsonc
{
  "model": { "name": "TF–IDF Logistic Regression", "threshold": 0.585, "available": true, "is_primary": false, "note": "…" },
  "risk_probability": 0.9629, "operating_threshold": 0.585, "management_attention": true,
  "primary_aspect": "Pricing / Billing", "detected_aspects": ["Pricing / Billing", "Timeliness", "Workmanship"],
  "matched_phrases": { "Timeliness": ["hours late"] },
  "recommended_action": "Review estimate accuracy, …",          // "Routine monitoring…" when below threshold
  "sentences": [ { "index": 0, "start": 0, "end": 112, "text": "…", "risk_probability": 0.96, "flagged": true,
                   "aspects": ["…"], "matched_phrases": { } } ],  // start/end index into the submitted text
  "evidence": { "index": 0, "sentence": "…", "aspect": "Pricing / Billing", "matched_phrases": { }, "risk_probability": 0.96, "has_dictionary_match": true },
  "weights": { "bias": -0.19, "logit": 3.26, "terms": [ { "term": "failed", "label": "failed", "weight": 0.9 } ], "explained_positive": 3.7, "explained_negative": -0.25 },
  "masking_applied": false, "disclaimer": "…"
}
```
* Text is masked (URLs, emails, phones, dollar amounts, star phrases) before scoring.
* `sentences[].flagged` = sentence-level model probability ≥ the review-level threshold (an approximation: the model was trained on whole reviews).
* `evidence` = the sentence carrying a dictionary match (highest risk first); otherwise the riskiest sentence.
* `weights.terms` are exact logit contributions (tf-idf × coefficient); `logit = bias + Σ all terms`.
* If scikit-learn / the joblib files are unavailable (or `HOMELENS_DISABLE_MODEL=1`) the API degrades to dictionary-only: `model.available=false`, probabilities `null`.
* DistilBERT (the notebook's primary model) is **not** served here; the UI shows `model.name` so the numbers are never mislabelled.
