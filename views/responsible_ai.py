"""Responsible AI: scope, limitations, oversight and privacy."""

from __future__ import annotations

import streamlit as st

from app import charts
from app.config import NOTEBOOK_FACTS
from app.data_loader import load_optional
from app.ui_components import card_header, icon, info_cards, page_header, pipeline_flow, render_html, section_title

WE_SAY = [
    "Review-based risk signal",
    "Needs management attention",
    "Operational concern and complaint signal",
    "Relative concern tier within this corpus",
    "Prompt for human investigation",
]
WE_NEVER_CLAIM = [
    "Bankruptcy or financial-failure prediction",
    "Legal liability",
    "Verified misconduct or fraud detection",
    "Verified safety violation",
    "A verdict on any individual business",
]


def _list(items: list[str], positive: bool) -> str:
    mark = icon("check", 16, 2.4) if positive else icon("minus", 16, 2.4)
    cls = "yes" if positive else "no"
    return '<ul class="hl-list">' + "".join(f'<li><span class="{cls}">{mark}</span>{item}</li>' for item in items) + "</ul>"


def render() -> None:
    page_header(
        "Responsible AI",
        "Signals for people, not verdicts",
        "HomeLens AI surfaces patterns in customer language so managers know where to look. "
        "Every alert is a starting point for human judgment.",
        pills=[("users", "Human in the loop"), ("lock", "Anonymized providers"), ("eye", "Transparent limits")],
    )

    section_title("Known limitations", "What the data can and cannot tell you.", kicker="Scope")
    info_cards([
        {"icon": "map", "title": "Geographic scope",
         "body": f"Reviews come from {NOTEBOOK_FACTS['market']} only. Patterns may not transfer to other markets.",
         "tag": "One metro area"},
        {"icon": "clock", "title": "Historical scope",
         "body": f"Data runs from {NOTEBOOK_FACTS['date_start']} to {NOTEBOOK_FACTS['date_end']} and may not "
                 "reflect how providers operate today.", "tag": "Ends Jan 2022"},
        {"icon": "users", "title": "Self-selection bias",
         "body": "Yelp reviewers are not a random sample of customers. Very satisfied and very unhappy "
                 "customers are over-represented.", "tag": "Not a survey"},
        {"icon": "star", "title": "Weak star labels",
         "body": "Models learn from star ratings, which are an imperfect proxy for operational risk. "
                 "Three-star reviews were excluded from training.", "tag": "Proxy labels"},
        {"icon": "alert", "title": "Unverified allegations",
         "body": "A review is one customer's account. Detected safety or conduct language is a claim to "
                 "investigate, not a confirmed event.", "tag": "Claims, not facts"},
        {"icon": "scale", "title": "Relative tiers",
         "body": "Provider tiers rank providers against each other within this corpus. They are not "
                 "absolute probabilities of any outcome.", "tag": "Benchmark only"},
    ])

    section_title("Language guardrails", kicker="Terminology")
    a, b = st.columns(2, gap="medium")
    with a:
        with st.container(key="card_say"):
            card_header("How we describe outputs", icon_name="check")
            render_html(_list(WE_SAY, True))
    with b:
        with st.container(key="card_never"):
            card_header("What we never claim", icon_name="alert")
            render_html(_list(WE_NEVER_CLAIM, False))

    section_title("Human oversight workflow", "Every Elevated or High-concern signal goes through a person.",
                  kicker="Oversight")
    pipeline_flow([
        ("radar", "Signal raised", "Model score exceeds the operating threshold"),
        ("eye", "Analyst review", "Read the full review and its context"),
        ("users", "Provider dialogue", "Hear the business's side before acting"),
        ("action", "Proportionate action", "Coaching, process fix, or no action"),
        ("clock", "Monitor & retrain", "Track drift and refresh the model"),
    ])

    section_title("Data privacy and anonymization", kicker="Privacy")
    p1, p2 = st.columns([1, 1.2], gap="medium")
    with p1:
        info_cards([
            {"icon": "lock", "title": "Provider identities masked",
             "body": "Businesses appear only as stable codes such as Provider_0235. Names and Yelp IDs are not "
                     "shipped with the app."},
            {"icon": "shield", "title": "Text masking before modeling",
             "body": "URLs, emails, phone numbers, dollar amounts and explicit star phrases are replaced with "
                     "tokens before any model sees the text."},
            {"icon": "providers", "title": "Volume threshold",
             "body": "Providers need at least 20 reviews before they are monitored, which reduces noisy, "
                     "unfair conclusions from a handful of reviews."},
        ], cols=1)
    timeline = load_optional("corpus_timeline.csv")
    with p2:
        if timeline is not None:
            with st.container(key="card_timeline"):
                card_header("Reviews per year", "The corpus is historical; recent years are thin.", "clock")
                st.plotly_chart(charts.corpus_timeline(timeline), config=charts.PLOTLY_CONFIG, width="stretch")
        with st.container(key="card_secrets"):
            card_header("Secrets and raw data", icon_name="lock")
            st.markdown(
                "- The raw Yelp CSV is **not** deployed; the app reads aggregated artifacts only.\n"
                "- Hugging Face credentials are read from Streamlit secrets and are never displayed.\n"
                "- Review text typed into the analyzer is processed in memory and not stored."
            )
