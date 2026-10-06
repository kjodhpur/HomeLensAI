# Data contract — notebook → backend → frontend

The notebook (Section 9) writes three JSON files. `scripts/sync_artifacts.py` copies them into `backend/app/data/`; the backend serves them; the frontend's TypeScript types live in
`frontend/lib/types.ts`. **If you change a field, change all three places (notebook export, backend, `types.ts`) in the same PR.**
Committed examples (synthetic data) are in `backend/app/data/sample/`.

All rates are fractions in **0–1**, not percentages. Dates are ISO `YYYY-MM-DD`. `null` means "not computable" (e.g. too few reviews).

## `provider_risk.json`
```jsonc
{
  "meta": {
    "generated_at": "2026-10-06T06:07:34Z",
    "data_mode": "sample" | "yelp",
    "reference_date": "2022-01-17",      // latest review date: "today" for this dataset
    "recent_months": 24,                 // recent window; the prior window is the 24 months before it
    "min_reviews": 20,                   // providers below this are eligible=false
    "recurrence_min": 3,                 // an issue is "recurring" at >= 3 distinct flagged reviews
    "risk_threshold": 0.7276,            // P(risk) at/above which a review is "flagged" (Layer 1)
    "scorer": "tfidf_logreg_oof",
    "score_weights": { "neg_rate_lb": 0.35, "recent_neg_rate": 0.25, "severity": 0.25, "recurrence": 0.15 },
    "n_reviews": 1166, "n_providers_total": 40, "n_providers_eligible": 26,
    "disclaimer": "Complaint signals detected …"      // show this in the UI
  },
  "providers": [ Provider, … ]           // eligible providers first, sorted by rank
}
```

### `Provider`
| Field | Type | Notes |
|---|---|---|
| `business_id` | string | Yelp business id (stable key; used in URLs) |
| `name`, `trade`, `city`, `state` | string | `trade` is one of the 9 trade groups from the notebook's `TRADE_RULES` |
| `categories` | string[] | raw Yelp categories |
| `eligible` | bool | `n_reviews >= min_reviews`; when false `risk_score`, `rank` are `null`, `risk_tier = "Insufficient data"`, and issues carry no evidence |
| `n_reviews`, `n_flagged` | int | all reviews / reviews flagged as a risk signal |
| `avg_stars`, `yelp_stars` | number | mean of this dataset's review stars / Yelp's own business rating (may be `null`) |
| `neg_rate` | number | `n_flagged / n_reviews` |
| `recent`, `prior` | `{n, neg_rate}` | window counts; `neg_rate` is `null` when `n < 5` |
| `trend` | `{direction, delta, p_value}` | `direction ∈ worsening \| improving \| stable \| insufficient data`; `delta = recent − prior`; Fisher exact p |
| `risk_score` | number 0–100 \| null | ranking aid, **not** a probability |
| `risk_tier` | `High \| Medium \| Low \| Insufficient data` | top 15 % / next 25 % / rest of eligible providers; safety rule can lift a tier |
| `rank` | int \| null | 1 = highest risk |
| `safety_escalation` | bool | ≥ 2 reviews with a safety signal |
| `issues` | `Issue[]` | sorted by count desc; includes non-recurring ones (`recurring=false`) |
| `action_manager`, `action_homeowner` | string | rule-based recommendation for each audience |
| `history` | `{year, n, neg_rate, avg_stars}[]` | one row per year with reviews — feeds the trend line chart |

### `Issue`
| Field | Type | Notes |
|---|---|---|
| `aspect` | one of `workmanship, reliability, pricing, communication, timeliness, professionalism, warranty, safety` | |
| `label`, `severity` | string, number 0–1 | display name; severity weight used in the score |
| `n_reviews` | int | distinct flagged reviews containing this aspect |
| `share_of_flagged` | number | `n_reviews / provider.n_flagged` |
| `recurring` | bool | `n_reviews >= recurrence_min` |
| `evidence` | `{review_id, date, stars, cue, sentence}[]` | up to 2 most-negative evidence sentences, one per review. **This is review text — see the licence note in `DEPLOYMENT.md`.** |

## `summary.json`
`meta` (same as above), `dataset {n_reviews, n_providers, date_min, date_max, star_distribution, median_words}`, `tiers {High, Medium, Low: int}`,
`trend_counts {worsening, improving, stable, insufficient data: int}`, `models[]` (one row per model × operating point: `model`, `operating point`, `macro F1`, `weighted F1`,
`risk precision`, `risk recall`, `risk F1`, `no-risk precision`, `no-risk recall`, `ROC AUC`, `PR AUC`), `aspects[]` (`key, label, severity, description, share_in_risk_reviews,
share_in_satisfied_reviews, flagged_reviews`), `trades[]` (`trade, providers, reviews, risk_rate`), `disclaimer`.

## `aspect_lexicon.json`
The Layer-2 lexicon (`aspects.<key> = {label, severity, description, strong[], weak[], topic[], negation_cancels_topic?}`), `negators[]` and `neg_sent_threshold`. The backend's
`/api/analyze` uses it for the lite live analyzer; the notebook is the single source of truth — **edit the lexicon in the notebook, not here.**

## HTTP API (backend)
| Method & path | Returns |
|---|---|
| `GET /api/health` | `{status, data_mode, generated_at, providers}` |
| `GET /api/summary` | `summary.json` |
| `GET /api/aspects` | `[{key, label, severity, description}]` |
| `GET /api/providers` | `{total, limit, offset, items: ProviderListItem[]}` — query: `q, trade, tier, trend, aspect, eligible_only (default true), sort (rank\|risk_score\|n_reviews\|neg_rate\|avg_stars\|name), order, limit (≤200), offset` |
| `GET /api/providers/{business_id}` | full `Provider` (404 if unknown) |
| `POST /api/analyze` `{text}` | lite aspect analysis of a pasted review (`signals[]` with evidence sentences) |

Interactive docs: `http://localhost:8000/docs`.
