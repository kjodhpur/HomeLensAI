"""LITE live analyzer for POST /api/analyze.

This is a *demo-grade* port of the notebook's Layer 2: it uses the same exported lexicon (`aspect_lexicon.json`) and
the same gates (negation, sentence sentiment) but NOT the spaCy `Matcher` rules, the `EntityRuler` or the Layer-1
classifier, because those need heavyweight dependencies that do not fit a serverless function. Results are therefore
a subset of what the notebook would flag. For production-grade scoring, run the notebook pipeline offline.
"""

from __future__ import annotations

import re
from typing import Any

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from . import store

_vader = SentimentIntensityAnalyzer()
_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+|\n+")
_WORD = re.compile(r"[a-z']+")


def _compiled() -> list[tuple[str, str, str, re.Pattern[str]]]:
    lex = store.lexicon()
    out = []
    for aspect, spec in lex["aspects"].items():
        for tier in ("strong", "weak", "topic"):
            for cue in spec.get(tier, []):
                out.append((aspect, tier, cue, re.compile(r"(?<![a-z])" + re.escape(cue.lower()) + r"(?![a-z])")))
    return out


_PATTERNS: list[tuple[str, str, str, re.Pattern[str]]] | None = None


def analyze(text: str) -> dict[str, Any]:
    global _PATTERNS
    if _PATTERNS is None:
        _PATTERNS = _compiled()
    lex = store.lexicon()
    negators = set(lex["negators"])
    thresh = lex["neg_sent_threshold"]
    review_compound = _vader.polarity_scores(text)["compound"]
    review_negative = review_compound <= thresh

    hits: dict[tuple[str, int], dict[str, Any]] = {}
    for si, sentence in enumerate(s.strip() for s in _SENT_SPLIT.split(text) if s.strip()):
        low = sentence.lower()
        sent_compound = _vader.polarity_scores(sentence)["compound"]
        for aspect, tier, _cue, pat in _PATTERNS:
            m = pat.search(low)
            if not m:
                continue
            before = _WORD.findall(low[: m.start()])[-2:]
            negated = any(w in negators for w in before)
            spec = lex["aspects"][aspect]
            if tier in ("strong", "weak") and negated:
                continue
            if tier == "topic" and spec.get("negation_cancels_topic") and negated:
                continue
            ambiguous = tier in ("weak", "topic")
            complaint = (tier == "strong") or sent_compound <= thresh
            if ambiguous:
                complaint = complaint and review_negative  # stand-in for "Layer 1 flagged this review"
            key = (aspect, si)
            prev = hits.get(key)
            if prev is None or (complaint, tier == "strong") > (prev["complaint"], prev["tier"] == "strong"):
                hits[key] = {
                    "aspect": aspect, "label": spec["label"], "tier": tier, "cue": sentence[m.start() : m.end()],
                    "sentence": sentence, "sentence_compound": round(sent_compound, 3), "complaint": complaint,
                }
    signals = sorted((h for h in hits.values() if h["complaint"]), key=lambda h: h["sentence_compound"])
    aspects = sorted({h["aspect"] for h in signals}, key=lambda a: -lex["aspects"][a]["severity"])
    return {
        "text_compound": round(review_compound, 3),
        "negative_sentiment": review_negative,
        "aspects": aspects,
        "signals": signals,
        "mode": "lite",
        "note": "Lite analyzer: lexicon + negation + sentiment gates only (no spaCy Matcher/EntityRuler, no Layer-1 classifier).",
        "disclaimer": store.provider_risk()["meta"]["disclaimer"],
    }
