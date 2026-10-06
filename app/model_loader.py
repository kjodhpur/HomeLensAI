"""Model loading: fine-tuned DistilBERT from Hugging Face with a TF-IDF fallback.

Configuration (``.streamlit/secrets.toml`` or environment variables):

- ``HF_MODEL_ID``: Hugging Face repository of the fine-tuned model (required for DistilBERT).
- ``HF_TOKEN``: access token, only needed for a private repository.
- ``DISTILBERT_THRESHOLD``: operating threshold, default 0.95 (validated in the notebook).

Any failure while importing or loading the transformer falls back to the TF-IDF
Logistic Regression artifacts shipped in ``artifacts/``.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Callable

import joblib
import streamlit as st

from app.config import (
    ARTIFACTS_DIR,
    DISTILBERT_NAME,
    MAX_LENGTH,
    NOTEBOOK_FACTS,
    TFIDF_NAME,
    get_secret,
)
from app.data_loader import load_metadata
from app.risk_logic import ReviewAnalysis, analyze_review, mask_sensitive_and_leakage

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ActiveModel:
    """The model currently serving review analysis."""

    name: str
    threshold: float
    scorer: Callable[[str], float]
    is_primary: bool
    status_note: str

    def analyze(self, text: str) -> ReviewAnalysis:
        return analyze_review(text, self.scorer, self.threshold, self.name)


@st.cache_resource(show_spinner=False)
def _load_tfidf() -> tuple[object, object]:
    vectorizer = joblib.load(ARTIFACTS_DIR / "homelens_tfidf_vectorizer.joblib")
    model = joblib.load(ARTIFACTS_DIR / "homelens_tfidf_logistic_regression.joblib")
    return vectorizer, model


def _tfidf_model(note: str) -> ActiveModel:
    vectorizer, model = _load_tfidf()

    def score(text: str) -> float:
        matrix = vectorizer.transform([mask_sensitive_and_leakage(text)])
        return float(model.predict_proba(matrix)[0, 1])

    # The threshold must belong to the shipped joblib model (selected on its validation split).
    threshold = float(load_metadata().get("tfidf_threshold", NOTEBOOK_FACTS["tfidf_threshold"]))
    return ActiveModel(TFIDF_NAME, threshold, score, False, note)


@st.cache_resource(show_spinner=False)
def _load_distilbert(model_id: str, token: str | None) -> tuple[object, object]:
    import torch  # noqa: F401  (import errors trigger the fallback)
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(model_id, token=token)
    model = AutoModelForSequenceClassification.from_pretrained(model_id, token=token)
    model.eval()
    return tokenizer, model


def _distilbert_model(model_id: str, token: str | None, threshold: float) -> ActiveModel:
    import torch

    tokenizer, model = _load_distilbert(model_id, token)

    def score(text: str) -> float:
        inputs = tokenizer(
            mask_sensitive_and_leakage(text),
            return_tensors="pt",
            truncation=True,
            max_length=MAX_LENGTH,
        )
        with torch.no_grad():
            logits = model(**inputs).logits
        return float(torch.softmax(logits, dim=1)[0, 1])

    score("Model warm-up check.")
    return ActiveModel(DISTILBERT_NAME, threshold, score, True, "Loaded from Hugging Face")


@st.cache_resource(show_spinner="Loading the review-risk model…")
def get_active_model() -> ActiveModel:
    """Return DistilBERT when configured and loadable, otherwise TF-IDF."""
    model_id = get_secret("HF_MODEL_ID")
    if not model_id:
        return _tfidf_model("HF_MODEL_ID not configured")
    try:
        threshold = float(get_secret("DISTILBERT_THRESHOLD", str(NOTEBOOK_FACTS["distilbert_threshold"])))
        return _distilbert_model(model_id, get_secret("HF_TOKEN"), threshold)
    except Exception as error:  # any import, network, auth or shape failure
        logger.warning("DistilBERT unavailable (%s); using TF-IDF fallback.", type(error).__name__)
        return _tfidf_model(f"DistilBERT unavailable ({type(error).__name__})")
