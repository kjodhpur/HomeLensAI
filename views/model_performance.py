"""Model Performance: validated comparison of TextBlob, TF-IDF and DistilBERT."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from app import charts
from app.config import NOTEBOOK_FACTS
from app.data_loader import load_metadata, load_model_comparison, load_optional
from app.ui_components import card_header, esc, info_cards, note, page_header, pipeline_flow, render_html, section_title, stat_row

DISTIL, TFIDF, BLOB = "Fine-tuned DistilBERT", "TF–IDF Logistic Regression", "TextBlob"


def _scorecard(comparison: pd.DataFrame) -> pd.DataFrame:
    """Metrics as rows, models as columns (fits a narrow card)."""
    table = comparison.set_index("model").reindex([DISTIL, TFIDF, BLOB])
    table = table[["operating_threshold", *charts.METRIC_LABELS]].T
    table.index = ["Threshold", *charts.METRIC_LABELS.values()]
    return table.rename(columns=charts.SHORT_MODEL_NAMES)


def _term(term: str) -> str:
    return {"moneytoken": "[dollar amount]", "ratingtoken": "[star phrase]"}.get(term, term)


def render() -> None:
    comparison = load_model_comparison()
    metrics = comparison.set_index("model")
    distil, tfidf = metrics.loc[DISTIL], metrics.loc[TFIDF]

    page_header(
        "Model Performance",
        "Why DistilBERT is the primary model",
        "Three approaches evaluated on businesses never seen in training. Thresholds were selected on "
        "validation businesses, and the test set was used once.",
        pills=[("shield", "Business-held-out test"), ("target", f"{NOTEBOOK_FACTS['split'][2]['reviews']:,} test reviews"),
               ("providers", f"{NOTEBOOK_FACTS['split'][2]['businesses']} unseen businesses")],
    )

    missed_distil = (1 - distil["negative_recall"]) * NOTEBOOK_FACTS["test_negatives"]
    missed_tfidf = (1 - tfidf["negative_recall"]) * NOTEBOOK_FACTS["test_negatives"]
    st.write("")
    stat_row([
        ("Macro F1", f"{distil['macro_f1']:.3f}",
         f'<span class="hl-up">+{(distil["macro_f1"] - tfidf["macro_f1"]) * 100:.1f} pts</span> vs TF–IDF ({tfidf["macro_f1"]:.3f})'),
        ("Negative recall", f"{distil['negative_recall']:.3f}",
         f'~{missed_tfidf - missed_distil:.0f} fewer missed complaints per {NOTEBOOK_FACTS["test_negatives"]:,} negatives'),
        ("Negative precision", f"{distil['negative_precision']:.3f}",
         f"Fewer unnecessary escalations than TF–IDF ({tfidf['negative_precision']:.3f})"),
    ])

    section_title("Head-to-head comparison", "Held-out test metrics for each model.", kicker="Evidence")
    chart_col, table_col = st.columns([1.25, 1], gap="medium")
    with chart_col:
        with st.container(key="card_dotplot"):
            card_header("Metric comparison", "Each row is one metric. The right-most dot is the best model.", "target")
            st.plotly_chart(charts.model_dot_plot(comparison), config=charts.PLOTLY_CONFIG, width="stretch")
    with table_col:
        with st.container(key="card_scorecard"):
            card_header("Scorecard", "Best value per metric highlighted.", "layers")
            table = _scorecard(comparison)
            styled = (
                table.style.format("{:.3f}")
                .highlight_max(axis=1, subset=(list(charts.METRIC_LABELS.values()), slice(None)),
                               props="background-color:#EFEBFF;color:#4B2BD6;font-weight:700")
            )
            st.dataframe(styled, width="stretch", height=287)
            st.caption("Operating thresholds were chosen on validation businesses to reach at least "
                       f"{NOTEBOOK_FACTS['recall_floor']:.0%} negative recall with the highest precision.")
            render_html(
                f"""<div class="hl-kv"><div><div class="k">Validation macro F1 · DistilBERT</div>
                <div class="v">{NOTEBOOK_FACTS['validation_macro_f1'][DISTIL]:.3f}</div></div>
                <div><div class="k">Validation macro F1 · TF–IDF</div>
                <div class="v">{NOTEBOOK_FACTS['validation_macro_f1'][TFIDF]:.3f}</div></div></div>"""
            )

    section_title("Business interpretation", kicker="So what")
    info_cards([
        {"icon": "target", "title": "Finds more real complaints",
         "body": f"Negative recall rises from {tfidf['negative_recall']:.3f} to {distil['negative_recall']:.3f}, "
                 "so fewer service failures slip past managers.", "tag": "Recall"},
        {"icon": "check", "title": "Fewer false alarms",
         "body": f"Negative precision of {distil['negative_precision']:.3f} keeps escalations focused on reviews "
                 "that genuinely describe a problem.", "tag": "Precision"},
        {"icon": "cpu", "title": "Reads context, not keywords",
         "body": "DistilBERT captures word order, so mixed reviews like “friendly tech, but the repair "
                 "failed again” are scored correctly.", "tag": "Context"},
        {"icon": "alert", "title": "Generic sentiment is not enough",
         "body": f"TextBlob reaches recall {metrics.loc[BLOB, 'negative_recall']:.3f} only by flagging many "
                 f"positive reviews (precision {metrics.loc[BLOB, 'negative_precision']:.3f}).", "tag": "Baseline"},
        {"icon": "layers", "title": "A resilient fallback",
         "body": f"TF–IDF (macro F1 {tfidf['macro_f1']:.3f}) is fast and explainable, and serves the app "
                 "automatically if DistilBERT cannot load.", "tag": "Fallback"},
        {"icon": "scale", "title": "Selected on validation",
         "body": "The deployment model was chosen from validation results, not test results, which keeps "
                 "the reported test scores honest.", "tag": "Governance"},
    ])

    section_title("Evaluation design", "How the test protects against leakage.", kicker="Method")
    split = NOTEBOOK_FACTS["split"]
    pipeline_flow([
        ("lock", "Mask leakage", "Star phrases, prices and PII removed from text"),
        ("star", "Weak labels", "1–2 stars = risk; 4–5 = positive; 3 excluded"),
        ("providers", f"Train · {split[0]['reviews']:,}", f"{split[0]['businesses']} businesses"),
        ("target", f"Validate · {split[1]['reviews']:,}", f"{split[1]['businesses']} businesses; tune C and threshold"),
        ("shield", f"Test · {split[2]['reviews']:,}", f"{split[2]['businesses']} unseen businesses, used once"),
    ])

    terms = load_optional("tfidf_signal_terms.csv")
    if terms is not None:
        section_title("What the TF–IDF model listens for", "Strongest learned terms in the shipped fallback model.",
                      kicker="Explainability")
        with st.container(key="card_terms"):
            neg = "".join(f'<span class="hl-chip" style="--i:{i}">{esc(_term(t))}</span>'
                          for i, t in enumerate(terms["negative_signal_terms"].head(12)))
            pos = "".join(f'<span class="hl-chip muted" style="--i:{i}">{esc(_term(t))}</span>'
                          for i, t in enumerate(terms["positive_signal_terms"].head(12)))
            render_html(f'<div class="hl-kicker" style="margin-bottom:8px">Risk signals</div><div class="hl-chips">{neg}</div>'
                    f'<div class="hl-kicker" style="margin:14px 0 8px;color:#0A6B0A">Positive signals</div>'
                    f'<div class="hl-chips">{pos}</div>')

    meta = load_metadata()
    if meta.get("tfidf_rebuild_test_macro_f1"):
        note(
            "All metrics above are the validated results from the executed project notebook. The TF–IDF "
            f"fallback shipped with this app was rebuilt locally (threshold {meta['tfidf_threshold']:.3f}) "
            "on a re-drawn business-held-out split."
        )
