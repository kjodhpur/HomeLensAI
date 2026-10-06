# HomeLens AI: Business Risk Command Center

A Streamlit product that turns unstructured Yelp reviews of home-service providers into
review-level risk signals, complaint-aspect explanations, anonymized provider monitoring,
and recommended management actions.

> **Business question:** Can NLP identify, classify, and explain operational and reputational
> business-risk signals in Yelp reviews so home-service managers can prioritize corrective action?

CIS 509 Analytics for Unstructured Data · Team HomeLensAI:
Rithik Roy Thati · Kanha Jodhpurkar · Sankalp Sharma Madgula · Dev Bhattacharyya

## Pages

| Page | What it shows |
|---|---|
| **Executive Overview** | Headline metrics, auto-advancing insight briefing, concern-tier distribution, service-group benchmark, strongest complaint signals, pipeline |
| **Review Analyzer** | Paste or pick a review → animated risk gauge, attention decision, complaint chips, primary issue, recommended action, model used |
| **Provider Monitor** | Filters (service group, tier, minimum reviews, aspect, trend), anonymized watchlist, provider detail panel with yearly trend, CSV export |
| **Model Performance** | TextBlob vs TF–IDF vs DistilBERT on business-held-out test data, scorecard, business interpretation, evaluation design |
| **Responsible AI** | Scope and limitations, language guardrails, human-oversight workflow, privacy and anonymization |

## Validated results (from `notebooks/FinalProject_HomeLensAI.ipynb`)

| Model | Threshold | Macro F1 | Neg. precision | Neg. recall | Neg. F1 | Avg. precision | ROC-AUC |
|---|---|---|---|---|---|---|---|
| Fine-tuned DistilBERT | 0.95 | **0.973** | 0.972 | 0.955 | 0.963 | 0.993 | 0.996 |
| TF–IDF Logistic Regression | 0.62 | 0.951 | 0.950 | 0.917 | 0.933 | 0.984 | 0.991 |
| TextBlob | 0.405 | 0.785 | 0.630 | 0.909 | 0.744 | 0.848 | 0.911 |

17,943 core reviews · 1,054 providers · 254 monitored providers (≥20 reviews) · Tucson, AZ · Nov 2006 – Jan 2022.

## Run locally

```bash
python -m venv .venv
.venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
pip install -r requirements-dev.txt
streamlit run streamlit_app.py
pytest
```

Without Hugging Face secrets the app runs on the TF–IDF fallback (the sidebar shows **TF–IDF fallback**).

## Enable DistilBERT

1. Upload the notebook's `/content/HomeLensAI_DistilBERT` folder to a Hugging Face model repository
   (private is fine).
2. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and fill in `HF_MODEL_ID`
   (and `HF_TOKEN` for a private repository).
3. Restart the app. The sidebar shows **DistilBERT online**. Any loading failure falls back to TF–IDF.

## Deploy on Streamlit Community Cloud

1. Push this repository to GitHub (the raw CSV and secrets are git-ignored).
2. At [share.streamlit.io](https://share.streamlit.io), select **Create app**, then choose this repository, branch `main`,
   and main file `streamlit_app.py`. Under **Advanced settings**, choose Python 3.12.
3. Paste the contents of your `secrets.toml` into **Secrets**.
4. Deploy. Each push to `main` redeploys automatically.

## Project structure

```
streamlit_app.py          entry point: theme, navigation, sidebar
app/
  config.py               paths, brand tokens, tier colors, validated notebook facts
  risk_logic.py           masking, complaint-aspect matcher, analyze_review()
  model_loader.py         DistilBERT (Hugging Face) with TF–IDF fallback
  data_loader.py          cached artifact loaders
  charts.py               Plotly figures
  ui_components.py        CSS design system, animated cards, gauge, carousel
views/                    one module per page
artifacts/                anonymized tables + TF–IDF joblib model (no raw text)
scripts/build_artifacts.py  rebuilds artifacts/ from the raw CSV
notebooks/                final and EDA notebooks
tests/                    pytest suite
```

## About the artifacts

`scripts/build_artifacts.py` reproduces the notebook pipeline on CPU. Category filtering, provider
codes and complaint-aspect counts match the notebook exactly. Two values come from this local rebuild:

- **TF–IDF fallback model.** The current scikit-learn draws a different business-held-out split than
  Colab, so the shipped model uses its own validation-selected threshold (0.585). The app always reports
  the notebook's validated metrics.
- **Provider risk tiers.** Scores come from TF–IDF probabilities (126 Stable, 75 Watch, 47 Elevated,
  6 High concern). The notebook's DistilBERT-based run gave 123 / 78 / 45 / 8. To show the notebook
  version, copy the Colab `HomeLensAI_outputs` CSVs into `artifacts/` and update
  `provider_scores_model` in `artifacts/metadata.json`.

## Responsible use

Outputs are review-based risk signals for human investigation. They are not predictions of bankruptcy,
legal liability, verified misconduct, verified safety violations, or fraud.
