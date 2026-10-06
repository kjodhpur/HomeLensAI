"""Executive Overview: headline metrics, tiers, benchmark, complaint signals."""

from __future__ import annotations

import streamlit as st

from app import charts
from app.config import NOTEBOOK_FACTS
from app.data_loader import load_aspects, load_metadata, load_providers, load_service_summary, tier_counts
from app.ui_components import (
    card_header,
    insight_carousel,
    metric_cards,
    note,
    page_header,
    pipeline_flow,
    section_title,
    tier_distribution,
)


def render() -> None:
    providers = load_providers()
    services = load_service_summary()
    aspects = load_aspects()
    meta = load_metadata()
    counts = tier_counts(providers)

    page_header(
        "HomeLens AI · Review-Based Operational Risk Intelligence",
        "Business Risk Command Center",
        "Detect emerging service issues, prioritize management attention, and connect "
        "customer language to corrective action.",
        pills=[
            ("map", f"{NOTEBOOK_FACTS['market']} home services"),
            ("clock", f"{NOTEBOOK_FACTS['date_start']} – {NOTEBOOK_FACTS['date_end']}"),
            ("shield", "Business-held-out evaluation"),
            ("lock", "Anonymized providers"),
        ],
    )

    metric_cards([
        {"label": "Reviews analyzed", "value": NOTEBOOK_FACTS["core_reviews"], "icon": "reviews",
         "caption": "Core home-service Yelp reviews"},
        {"label": "Providers", "value": NOTEBOOK_FACTS["providers"], "icon": "providers",
         "caption": "Businesses in the core subset"},
        {"label": "DistilBERT macro F1", "value": 0.973, "kind": "dec3", "icon": "target",
         "caption": "On businesses unseen in training"},
        {"label": "Providers monitored", "value": NOTEBOOK_FACTS["monitored_providers"], "icon": "radar",
         "caption": "With at least 20 reviews"},
    ])

    # ---- Key insights carousel -------------------------------------------
    top_group = services.iloc[0]
    top_aspect = aspects.sort_values("lift_vs_corpus_negative_rate", ascending=False).iloc[0]
    elevated_plus = int(counts["Elevated"] + counts["High concern"])
    section_title("Key insights", "Auto-advancing briefing. Hover to pause.", kicker="Briefing")
    insight_carousel([
        (f"{top_aspect['lift_vs_corpus_negative_rate']:.1f}×",
         f"{top_aspect['aspect']} is the strongest complaint signal",
         f"Reviews mentioning it are negative {top_aspect['negative_rate_when_mentioned']:.0%} of the time, "
         "far above the corpus baseline."),
        (f"{elevated_plus}",
         "Providers need management attention",
         f"{counts['Elevated']} Elevated and {counts['High concern']} High-concern providers out of "
         f"{len(providers)} monitored. Tiers are relative to this corpus."),
        (f"{top_group['median_risk_score']:.0f}",
         f"{top_group['service_group']} leads the risk benchmark",
         f"Median relative risk score across {int(top_group['eligible_businesses'])} monitored providers, "
         "the highest of any service group."),
        ("+2.2 pts",
         "DistilBERT beats the TF–IDF baseline",
         "Macro F1 0.973 vs 0.951, with negative recall rising from 0.917 to 0.955: fewer missed complaints."),
        ("0",
         "Business overlap across train, validation and test",
         "Every provider appears in exactly one partition, so scores reflect performance on new businesses."),
    ])

    # ---- Tiers + benchmark -------------------------------------------------
    section_title("Where to focus", "Relative concern tiers and service-group benchmark.", kicker="Portfolio")
    left, right = st.columns([1, 1.15], gap="medium")
    with left:
        with st.container(key="card_tiers"):
            card_header("Provider concern tiers", f"{len(providers)} providers with ≥20 reviews", "layers")
            tier_distribution(counts.to_dict())
            st.plotly_chart(charts.tier_by_group(providers), config=charts.PLOTLY_CONFIG, width="stretch")
    with right:
        with st.container(key="card_benchmark"):
            card_header("Service-group risk benchmark", "Median relative provider risk score (0–100)", "scale")
            st.plotly_chart(charts.service_benchmark(services), config=charts.PLOTLY_CONFIG, width="stretch")

    # ---- Complaint signals + executive interpretation -------------------------
    section_title("Why customers complain", "Complaint aspects and what they mean for operations.", kicker="Signals")
    chart_col, text_col = st.columns([1.35, 1], gap="medium")
    with chart_col:
        with st.container(key="card_complaints"):
            card_header("Strongest complaint signals",
                        "How much more often a review is negative when the aspect is mentioned", "alert")
            st.plotly_chart(charts.aspect_lift(aspects), config=charts.PLOTLY_CONFIG, width="stretch")
    trust = aspects.set_index("aspect").loc["Professionalism / Trust"]
    with text_col:
        with st.container(key="card_interp_1"):
            card_header("Conduct drives complaints", icon_name="users")
            st.markdown(
                f"Professionalism and trust language appears in **{int(trust['reviews_with_signal']):,}** reviews, "
                f"and **{trust['negative_rate_when_mentioned']:.0%}** of them are negative. "
                "Communication and no-shows follow closely."
            )
        with st.container(key="card_interp_2"):
            card_header("Concentrated, not universal", icon_name="target")
            st.markdown(
                f"Only **{counts['High concern']}** providers reach High concern, and "
                f"**{counts['Stable'] / len(providers):.0%}** are Stable, so attention can be targeted."
            )
        with st.container(key="card_interp_3"):
            card_header("Act on the cause", icon_name="action")
            st.markdown(
                "Each alert maps its leading complaint category to a **specific operational action**, "
                "not just a sentiment score."
            )

    section_title("How a review becomes an action", kicker="Pipeline")
    pipeline_flow([
        ("reviews", "Review text", "Customer narrative from Yelp"),
        ("lock", "Privacy masking", "Phones, emails, prices, star phrases"),
        ("cpu", "Risk classification", "DistilBERT, TF–IDF fallback"),
        ("spark", "Aspect explanation", "8 complaint categories"),
        ("layers", "Provider aggregation", "Relative tiers and trends"),
        ("action", "Management action", "Human-reviewed next step"),
    ])
    scores_model = meta.get("provider_scores_model")
    if scores_model:
        note(f"Provider tiers in this build are computed from {scores_model} review scores. "
             "Tiers are a relative benchmark within this historical Tucson corpus.")
