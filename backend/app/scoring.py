"""Review scoring with the shipped TF-IDF Logistic Regression model.

DistilBERT (the notebook's primary model) is too heavy for a serverless function, so the API serves the TF-IDF model whose
validation-selected threshold is stored in ``metadata.json``. The response always says which model produced the numbers.
Falls back to dictionary-only analysis when scikit-learn / the joblib files are unavailable.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from . import artifacts, config
from .risk_logic import (
    NO_MATCH,
    ROUTINE_MONITORING,
    analyze_review,
    extract_aspects,
    mask_sensitive_and_leakage,
    matched_phrases,
    recommend_action,
)

_SENTENCE = re.compile(r"[^.!?\n]+(?:[.!?]+|\n|$)")
# Masking placeholders end up in the vocabulary; show them as what they stand for.
TOKEN_LABELS = {
    "moneytoken": "[$ amount]", "phonetoken": "[phone number]", "emailtoken": "[email]", "urltoken": "[link]", "ratingtoken": "[star phrase]",
}


@dataclass(frozen=True)
class Model:
    name: str
    threshold: float
    vectorizer: object
    classifier: object

    def score(self, text: str) -> float:
        x = self.vectorizer.transform([mask_sensitive_and_leakage(text)])  # type: ignore[attr-defined]
        return float(self.classifier.predict_proba(x)[0, 1])  # type: ignore[attr-defined]


@lru_cache(maxsize=1)
def load_model() -> Model | None:
    if not config.MODEL_ENABLED:
        return None
    try:
        import joblib

        vec = joblib.load(config.ARTIFACTS_DIR / "homelens_tfidf_vectorizer.joblib")
        clf = joblib.load(config.ARTIFACTS_DIR / "homelens_tfidf_logistic_regression.joblib")
        threshold = float(artifacts.metadata().get("tfidf_threshold", 0.62))
        return Model(config.TFIDF_NAME, threshold, vec, clf)
    except Exception:  # missing file, version mismatch, sklearn not installed
        return None


def split_sentences(text: str) -> list[tuple[int, int]]:
    """Character spans (start, end) of the sentences in ``text`` (whitespace-only spans dropped)."""
    spans = [(m.start(), m.end()) for m in _SENTENCE.finditer(text) if m.group(0).strip()]
    return spans[: config.MAX_SENTENCES]


def token_weights(model: Model, text: str, top: int = 7) -> dict[str, Any]:
    """Per-term contributions to the review's logit (tf-idf value x coefficient) — exact for a linear model."""
    x = model.vectorizer.transform([mask_sensitive_and_leakage(text)])  # type: ignore[attr-defined]
    names = model.vectorizer.get_feature_names_out()  # type: ignore[attr-defined]
    coef = model.classifier.coef_[0]  # type: ignore[attr-defined]
    bias = float(model.classifier.intercept_[0])  # type: ignore[attr-defined]
    row = x.tocoo()
    terms = [{"term": names[j], "label": TOKEN_LABELS.get(names[j], names[j]), "weight": round(float(v * coef[j]), 4)}
             for j, v in zip(row.col, row.data, strict=True)]
    pos = sorted((t for t in terms if t["weight"] > 0), key=lambda t: -t["weight"])[:top]
    neg = sorted((t for t in terms if t["weight"] < 0), key=lambda t: t["weight"])[: max(3, top - 3)]
    total = bias + sum(t["weight"] for t in terms)
    return {"bias": round(bias, 4), "logit": round(total, 4), "terms": pos + neg,
            "explained_positive": round(sum(t["weight"] for t in terms if t["weight"] > 0), 4),
            "explained_negative": round(sum(t["weight"] for t in terms if t["weight"] < 0), 4)}


def analyze(text: str) -> dict[str, Any]:
    """Score one review: probability, decision, aspects, per-sentence breakdown, evidence sentence and token weights."""
    if not text.strip():
        raise ValueError("Review text is empty.")
    model = load_model()
    masked_changed = mask_sensitive_and_leakage(text) != re.sub(r"\s+", " ", text).strip()

    sentences: list[dict[str, Any]] = []
    for i, (a, b) in enumerate(split_sentences(text)):
        s = text[a:b]
        phrases = matched_phrases(s)
        sentences.append(
            {
                "index": i, "start": a, "end": b, "text": s.strip(),
                "risk_probability": round(model.score(s), 4) if model else None,
                "flagged": False, "aspects": sorted(phrases), "matched_phrases": phrases,
            }
        )

    if model:
        result = analyze_review(text, model.score, model.threshold, model.name).to_dict()
        for s in sentences:
            s["flagged"] = s["risk_probability"] >= model.threshold
        probability, threshold, attention = result["risk_probability"], result["operating_threshold"], result["management_attention"]
    else:
        aspects = extract_aspects(text)
        primary, _ = recommend_action(True, aspects)
        result = {
            "primary_aspect": primary, "detected_aspects": aspects, "matched_phrases": matched_phrases(text),
            "recommended_action": recommend_action(True, aspects)[1] if aspects else ROUTINE_MONITORING, "model_used": "Dictionary only",
        }
        probability = threshold = attention = None

    # Evidence = the sentence that carries the dictionary match (highest risk first); otherwise the riskiest sentence.
    matched = [s for s in sentences if s["aspects"]]
    pool = matched or sentences
    evidence = None
    if pool:
        best = max(pool, key=lambda s: (s["risk_probability"] or 0.0, len(s["matched_phrases"])))
        evidence = {"index": best["index"], "sentence": best["text"], "aspect": best["aspects"][0] if best["aspects"] else NO_MATCH,
                    "matched_phrases": best["matched_phrases"], "risk_probability": best["risk_probability"],
                    "has_dictionary_match": bool(best["aspects"])}

    return {
        "model": {"name": model.name if model else "Dictionary only", "threshold": threshold, "available": model is not None,
                  "is_primary": False,
                  "note": "Served model: TF–IDF Logistic Regression (the notebook's DistilBERT is not deployed in this API)." if model
                  else "Scoring model unavailable; showing dictionary complaint signals only."},
        "risk_probability": probability,
        "operating_threshold": threshold,
        "management_attention": attention,
        "primary_aspect": result["primary_aspect"],
        "detected_aspects": result["detected_aspects"],
        "matched_phrases": result["matched_phrases"],
        "recommended_action": result["recommended_action"],
        "sentences": sentences,
        "evidence": evidence,
        "weights": token_weights(model, text) if model else None,
        "masking_applied": masked_changed,
        "disclaimer": config.DISCLAIMER,
    }
