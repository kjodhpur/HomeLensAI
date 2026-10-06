# HomeLens AI Development Instructions

## Project objective

A polished Streamlit product, **HomeLens AI: Business Risk Command Center**, that converts Yelp
reviews of home-service providers into review-level risk alerts, complaint-aspect explanations,
provider-level monitoring, and recommended management actions.

Run: `streamlit run streamlit_app.py` · Test: `pytest` · Rebuild data: `python scripts/build_artifacts.py`

## Terminology

Use: review-based risk signal, management attention, operational concern, relative concern tier,
complaint signal, human investigation.

Never claim: bankruptcy prediction, legal liability, verified misconduct, verified safety violation,
fraud detection, financial-failure prediction.

## Data rules

- The app reads only `artifacts/`. Never make it depend on the raw CSV in `data/raw/` (git-ignored).
- Provider monitoring requires at least 20 reviews; show only anonymized `Provider_XXXX` codes.
- Secrets come only from `st.secrets` or environment variables (`app/config.get_secret`).
- Validated metrics live in `app/config.NOTEBOOK_FACTS` and `artifacts/model_comparison.csv`.
  Do not invent or recompute performance numbers.

## Modeling

- Primary: fine-tuned DistilBERT from Hugging Face (`HF_MODEL_ID`), threshold 0.95.
- Fallback: TF-IDF Logistic Regression joblib with the threshold in `artifacts/metadata.json`.
- Low-risk reviews get routine monitoring; high-risk reviews with no dictionary match get manual review.

## UI conventions

- All custom markup goes through `ui_components.render_html` (not `st.html`, which strips SVG
  and drops style-only blocks under `st.navigation`). Escape any user text with `esc()`.
- Style a card with `st.container(key="card_<name>")`; the CSS targets `st-key-card*`.
- Tier colors (Stable green, Watch amber, Elevated orange, High concern red) are reserved for risk
  and always appear with a text label. Purple is the single accent for everything else.
- Motion is CSS-only and disabled under `prefers-reduced-motion`.

## Engineering standards

Type hints, docstrings on reusable functions, `st.cache_resource` for models, `st.cache_data` for
tables, clear error states, tests for risk logic, and `requirements.txt` matching imports.
