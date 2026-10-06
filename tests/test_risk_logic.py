"""Unit tests for review-level risk logic (no Streamlit, no model files)."""

from __future__ import annotations

import pytest

from app.risk_logic import (
    NO_MATCH,
    RECOMMENDATIONS,
    ROUTINE_MONITORING,
    analyze_review,
    extract_aspects,
    mask_sensitive_and_leakage,
    matched_phrases,
)

NEGATIVE = (
    "The technician was three hours late, charged more than the quote, and the repair "
    "failed again two days later."
)
POSITIVE = "The team arrived on time, explained the work clearly, and finished the installation professionally."


def fixed(probability: float):
    return lambda _text: probability


def test_notebook_example_aspects_and_action() -> None:
    result = analyze_review(NEGATIVE, fixed(0.9946), 0.95, "Fine-tuned DistilBERT")
    assert result.detected_aspects == ["Pricing / Billing", "Timeliness", "Workmanship"]
    assert result.primary_aspect == "Pricing / Billing"
    assert result.management_attention is True
    assert result.recommended_action == RECOMMENDATIONS["Pricing / Billing"]
    assert result.model_used == "Fine-tuned DistilBERT"
    assert result.operating_threshold == 0.95


def test_low_risk_review_gets_routine_monitoring() -> None:
    result = analyze_review(POSITIVE, fixed(0.0019), 0.95, "Fine-tuned DistilBERT")
    assert result.management_attention is False
    assert result.detected_aspects == []
    assert result.recommended_action == ROUTINE_MONITORING


def test_low_risk_review_with_aspect_still_routine() -> None:
    result = analyze_review("Arrived late but did great work.", fixed(0.10), 0.95, "m")
    assert result.detected_aspects == ["Timeliness"]
    assert result.recommended_action == ROUTINE_MONITORING


def test_high_risk_without_dictionary_match_requests_manual_review() -> None:
    result = analyze_review("Absolutely awful from start to end.", fixed(0.99), 0.95, "m")
    assert result.primary_aspect == NO_MATCH
    assert result.recommended_action == RECOMMENDATIONS[NO_MATCH]


def test_threshold_is_inclusive() -> None:
    assert analyze_review("ok", fixed(0.95), 0.95, "m").management_attention is True
    assert analyze_review("ok", fixed(0.9499), 0.95, "m").management_attention is False


def test_empty_text_raises() -> None:
    with pytest.raises(ValueError):
        analyze_review("   ", fixed(0.5), 0.5, "m")


def test_invalid_probability_raises() -> None:
    with pytest.raises(ValueError):
        analyze_review("text", fixed(1.5), 0.5, "m")


@pytest.mark.parametrize(
    ("text", "aspect"),
    [
        ("They NEVER SHOWED up.", "Reliability / No-show"),
        ("He didn't fix the leak.", "Workmanship"),
        ("Total scam!", "Professionalism / Trust"),
        ("We need a follow-up repair.", "Warranty / Follow-up"),
        ("There was water damage everywhere", "Safety / Property Damage"),
        ("They never called back.", "Communication"),
    ],
)
def test_aspect_phrases_match_case_insensitively(text: str, aspect: str) -> None:
    assert aspect in extract_aspects(text)


@pytest.mark.parametrize("text", ["They were scammed", "unprofessionalism", "a no-show"])
def test_aspect_matching_respects_token_boundaries(text: str) -> None:
    assert extract_aspects(text) == []


def test_matched_phrases_reports_hits() -> None:
    assert matched_phrases(NEGATIVE)["Timeliness"] == ["hours late"]


def test_masking_removes_pii_prices_and_star_phrases() -> None:
    masked = mask_sensitive_and_leakage(
        "Call 520-555-1234 or a@b.com, see www.x.com. Paid $1,200.00. Five stars! 1-star."
    )
    for token in ["PHONETOKEN", "EMAILTOKEN", "URLTOKEN", "MONEYTOKEN", "RATINGTOKEN"]:
        assert token in masked
    assert "520" not in masked and "$" not in masked
