"""Review Analyzer: score one review, explain it, and recommend an action."""

from __future__ import annotations

import streamlit as st

from app.model_loader import get_active_model
from app.risk_logic import ReviewAnalysis
from app.ui_components import (
    card_header,
    chips,
    decision_block,
    empty_state,
    esc,
    fmt_threshold,
    highlighted_review,
    icon,
    model_pill,
    note,
    page_header,
    render_html,
    risk_gauge,
)

# Synthetic examples (no real provider names).
PRESETS: dict[str, tuple[str, str]] = {
    "preset_neg_1": (
        "Overcharged",
        "The technician was three hours late, charged more than the quote, and the repair failed "
        "again two days later.",
    ),
    "preset_neg_2": (
        "No-show",
        "They never showed for the scheduled appointment. I called four times and they never called "
        "back. When someone finally answered, the manager was very rude and unprofessional.",
    ),
    "preset_neg_3": (
        "Property damage",
        "After the water heater install we found water damage under the cabinet. The company refused "
        "to fix it and said it was not under warranty. Completely dishonest experience.",
    ),
    "preset_pos_1": (
        "On time",
        "The team arrived on time, explained the work clearly, and finished the installation professionally.",
    ),
    "preset_pos_2": (
        "Great follow-up",
        "Fair price, honest estimate, and the owner checked in a week later to make sure everything was "
        "still working. Highly recommend them for any plumbing job.",
    ),
}

STATE_TEXT = "analyzer_text"
STATE_RESULT = "analyzer_result"


def _load_preset(key: str) -> None:
    st.session_state[STATE_TEXT] = PRESETS[key][1]
    st.session_state.pop(STATE_RESULT, None)


def _clear() -> None:
    st.session_state[STATE_TEXT] = ""
    st.session_state.pop(STATE_RESULT, None)


def render() -> None:
    model = get_active_model()
    st.session_state.setdefault(STATE_TEXT, "")

    page_header(
        "Review Analyzer",
        "Score a review in seconds",
        "Paste a customer review to see its risk probability, the decision at the operating threshold, "
        "the complaint signals behind it, and the recommended management action.",
        pills=[("cpu", model.name), ("target", f"Threshold {fmt_threshold(model.threshold)}"), ("lock", "Text is masked before scoring")],
    )
    st.write("")

    left, right = st.columns([1, 1.05], gap="large")

    with left:
        with st.container(key="card_input"):
            card_header("Customer review", "Write your own or start from an example.", "reviews")
            render_html('<div class="hl-kicker" style="margin:4px 0 6px">Complaint examples</div>')
            neg_cols = st.columns(3)
            for col, key in zip(neg_cols, ["preset_neg_1", "preset_neg_2", "preset_neg_3"], strict=True):
                col.button(PRESETS[key][0], key=key, on_click=_load_preset, args=(key,), width="stretch")
            render_html('<div class="hl-kicker" style="margin:8px 0 6px;color:#0A6B0A">Positive examples</div>')
            pos_cols = st.columns(2)
            for col, key in zip(pos_cols, ["preset_pos_1", "preset_pos_2"], strict=True):
                col.button(PRESETS[key][0], key=key, on_click=_load_preset, args=(key,), width="stretch")

            text = st.text_area(
                "Review text",
                key=STATE_TEXT,
                height=210,
                max_chars=5000,
                placeholder="e.g. The crew showed up two days late and left the job unfinished…",
            )
            b1, b2 = st.columns([3, 1])
            analyze = b1.button("Analyze review", type="primary", icon=":material/bolt:", width="stretch",
                                disabled=not text.strip())
            b2.button("Clear", on_click=_clear, width="stretch", type="secondary")
            note("Analysis runs on masked text: phone numbers, emails, URLs, dollar amounts and "
                 "explicit star phrases are replaced before scoring.", "lock")

        if analyze and text.strip():
            with st.spinner("Scoring review…"):
                try:
                    st.session_state[STATE_RESULT] = (model.analyze(text), text)
                except Exception as error:  # surface a friendly message, keep the app alive
                    st.session_state.pop(STATE_RESULT, None)
                    st.error(f"The review could not be analyzed ({type(error).__name__}). Please try again.")

    with right:
        stored = st.session_state.get(STATE_RESULT)
        with st.container(key="card_result"):
            if stored is None:
                empty_state("Results appear here",
                            "Choose an example or paste a review, then select Analyze review.")
                return
            _render_result(*stored)


def _render_result(result: ReviewAnalysis, text: str) -> None:
    primary = result.model_used.startswith("Fine-tuned")
    render_html(
        f'<div class="hl-result-head"><div class="hl-card-title">{icon("radar", 18)}Risk assessment</div>'
        f"{model_pill(result.model_used, primary)}</div>"
        + risk_gauge(result.risk_probability, result.operating_threshold)
        + decision_block(result.management_attention)
        + f"""<div class="hl-kv">
            <div><div class="k">Primary issue</div><div class="v">{esc(result.primary_aspect)}</div></div>
            <div><div class="k">Probability vs threshold</div>
            <div class="v">{result.risk_probability:.4f} / {fmt_threshold(result.operating_threshold)}</div></div></div>"""
        + '<div class="hl-kicker" style="margin:6px 0 8px">Detected complaint signals</div>'
        + chips(result.detected_aspects, primary=result.primary_aspect if result.detected_aspects else None)
        + f"""<div class="hl-action"><span class="ic">{icon("action", 20)}</span><div>
            <div class="k">Recommended management action</div><div class="v">{esc(result.recommended_action)}</div></div></div>"""
    )
    if result.matched_phrases:
        with st.expander("Show matched phrases in the review", icon=":material/format_quote:"):
            render_html(highlighted_review(text, result.matched_phrases))
    note("This is a review-based risk signal for human investigation. It does not verify the "
         "customer's allegations or establish misconduct.", "shield")
