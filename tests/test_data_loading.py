"""Tests for the shipped artifacts and the TF-IDF fallback model."""

from __future__ import annotations

import joblib
import pandas as pd
import pytest

from app.config import ARTIFACTS_DIR, TIER_ORDER
from app.data_loader import (
    REQUIRED_FILES,
    load_aspects,
    load_model_comparison,
    load_providers,
    missing_artifacts,
    trend_direction,
)
from app.risk_logic import mask_sensitive_and_leakage


def test_required_artifacts_present() -> None:
    assert missing_artifacts() == []
    assert set(REQUIRED_FILES) <= {p.name for p in ARTIFACTS_DIR.iterdir()}


def test_provider_table_is_anonymized_and_complete() -> None:
    providers = load_providers()
    assert len(providers) == 254
    assert providers["reviews"].min() >= 20
    assert providers["provider_code"].str.fullmatch(r"Provider_\d{4}").all()
    assert not {"name", "business_id", "text"} & set(providers.columns)
    assert set(providers["risk_tier"].astype(str)) <= set(TIER_ORDER)
    assert providers["risk_score"].between(0, 100).all()


def test_model_comparison_matches_notebook() -> None:
    table = load_model_comparison().set_index("model")
    assert table.loc["Fine-tuned DistilBERT", "macro_f1"] == pytest.approx(0.973)
    assert table.loc["TF–IDF Logistic Regression", "macro_f1"] == pytest.approx(0.951)
    assert table.loc["TextBlob", "macro_f1"] == pytest.approx(0.785)
    assert table.loc["Fine-tuned DistilBERT", "operating_threshold"] == pytest.approx(0.95)


def test_aspect_counts_match_notebook() -> None:
    counts = load_aspects().set_index("aspect")["reviews_with_signal"].to_dict()
    assert counts["Professionalism / Trust"] == 806
    assert counts["Safety / Property Damage"] == 136


@pytest.mark.parametrize(
    ("delta", "label"),
    [(0.2, "Rising"), (-0.2, "Improving"), (0.01, "Steady"), (float("nan"), "Insufficient data")],
)
def test_trend_direction(delta: float, label: str) -> None:
    assert trend_direction(delta) == label


def test_tfidf_fallback_ranks_complaint_above_praise() -> None:
    vectorizer = joblib.load(ARTIFACTS_DIR / "homelens_tfidf_vectorizer.joblib")
    model = joblib.load(ARTIFACTS_DIR / "homelens_tfidf_logistic_regression.joblib")
    texts = pd.Series([
        "Rude, unprofessional, never showed up and overcharged us. Worst company.",
        "Friendly, professional, on time and reasonably priced. Highly recommend!",
    ]).map(mask_sensitive_and_leakage)
    negative, positive = model.predict_proba(vectorizer.transform(texts))[:, 1]
    assert negative > 0.9 > 0.1 > positive
