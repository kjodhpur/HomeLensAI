"""Review-level risk logic shared by the app and the artifact build script.

Everything here mirrors the final project notebook
(notebooks/FinalProject_HomeLensAI.ipynb): the privacy/leakage masking rules,
the complaint-aspect phrase dictionary, and the management recommendations.

The notebook used a spaCy ``PhraseMatcher`` on a blank English tokenizer with
``attr="LOWER"``. This module reproduces the same token-boundary,
case-insensitive matching with compiled regular expressions so the deployed
app does not need spaCy. ``scripts/build_artifacts.py`` verifies that the
aspect counts match the notebook exactly.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import Callable

# --------------------------------------------------------------------------
# Privacy and target-leakage masking (notebook section 4)
# --------------------------------------------------------------------------
MASKING_RULES: list[tuple[str, str]] = [
    (r"(?:https?://|www\.)\S+", " URLTOKEN "),
    (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", " EMAILTOKEN "),
    (r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}\b", " PHONETOKEN "),
    (r"\$\s?\d[\d,]*(?:\.\d{2})?", " MONEYTOKEN "),
    (
        r"\b(?:zero|one|two|three|four|five|first|second|third|fourth|fifth|"
        r"[0-5](?:st|nd|rd|th)?)[- ]?star(?:s)?\b",
        " RATINGTOKEN ",
    ),
]
_COMPILED_MASKS = [(re.compile(p, re.IGNORECASE), r) for p, r in MASKING_RULES]


def mask_sensitive_and_leakage(text: str) -> str:
    """Mask URLs, emails, phones, dollar amounts and explicit star phrases."""
    cleaned = str(text)
    for pattern, replacement in _COMPILED_MASKS:
        cleaned = pattern.sub(replacement, cleaned)
    return re.sub(r"\s+", " ", cleaned).strip()


# --------------------------------------------------------------------------
# Complaint-aspect dictionary (notebook section 10)
# --------------------------------------------------------------------------
RISK_PHRASES: dict[str, list[str]] = {
    "Workmanship": [
        "poor quality", "bad job", "terrible job", "sloppy work", "unfinished work",
        "not finished", "installed incorrectly", "incorrect installation", "repair failed",
        "did not fix", "didn't fix", "still leaking", "stopped working", "made it worse",
        "broke again", "poor workmanship", "damaged the", "damaged my",
    ],
    "Reliability / No-show": [
        "no show", "never showed", "did not show", "didn't show", "never came",
        "did not come", "didn't come", "missed appointment", "cancelled appointment",
        "canceled appointment", "failed to arrive",
    ],
    "Timeliness": [
        "arrived late", "showed up late", "hours late", "days late", "project delayed",
        "missed deadline", "took weeks", "took months", "long wait", "still waiting",
        "slow service",
    ],
    "Pricing / Billing": [
        "overcharged", "charged more", "hidden fee", "hidden fees", "unexpected charge",
        "extra charge", "price changed", "estimate changed", "bait and switch",
        "too expensive", "way too expensive", "rip off", "ripped off",
    ],
    "Communication": [
        "never called back", "did not call back", "didn't call back", "no response",
        "never responded", "did not respond", "didn't respond", "stopped responding",
        "poor communication", "no communication", "would not return my call",
        "wouldn't return my call",
    ],
    "Professionalism / Trust": [
        "very rude", "rude staff", "unprofessional", "dishonest", "lied to me",
        "misleading", "scam", "fraud", "disrespectful", "aggressive behavior",
    ],
    "Safety / Property Damage": [
        "unsafe", "dangerous", "fire hazard", "electrical hazard", "gas leak",
        "water damage", "flooded my", "damaged my property", "mold problem", "safety issue",
    ],
    "Warranty / Follow-up": [
        "warranty not honored", "would not honor", "refused to fix", "would not fix",
        "wouldn't fix", "follow up repair", "follow-up repair", "return visit",
        "under warranty", "warranty claim",
    ],
}

HIGH_SEVERITY_ASPECTS: tuple[str, ...] = (
    "Workmanship",
    "Safety / Property Damage",
    "Warranty / Follow-up",
)

NO_MATCH = "No dictionary match"

RECOMMENDATIONS: dict[str, str] = {
    "Workmanship": "Audit repeat jobs, callbacks, and post-service quality checks.",
    "Reliability / No-show": "Review scheduling, dispatch, and appointment-confirmation controls.",
    "Timeliness": "Investigate cycle-time bottlenecks and customer delay notifications.",
    "Pricing / Billing": "Review estimate accuracy, change-order approvals, and fee disclosure.",
    "Communication": "Strengthen callback ownership, status updates, and escalation procedures.",
    "Professionalism / Trust": "Review conduct complaints and reinforce customer-service standards.",
    "Safety / Property Damage": (
        "Escalate for human review and investigate the reported safety/property-damage signal."
    ),
    "Warranty / Follow-up": "Audit warranty response times, repeat repairs, and closure tracking.",
    NO_MATCH: "Perform manual review and expand the domain phrase dictionary.",
}

ROUTINE_MONITORING = (
    "Routine monitoring. The review is below the management-attention threshold; "
    "no manual investigation is required."
)


def _token_word(token: str) -> str:
    """Regex for one tokenizer token, splitting English contractions like spaCy."""
    match = re.fullmatch(r"(\w+)(n't)", token, flags=re.IGNORECASE)
    if match:
        # spaCy splits "didn't" into "did" + "n't" with no whitespace between.
        return re.escape(match.group(1)) + re.escape(match.group(2))
    return re.escape(token)


def _phrase_pattern(phrase: str) -> str:
    # Split hyphenated words into separate tokens the way spaCy's infix rules do.
    tokens = re.findall(r"[\w']+|[^\w\s]", phrase)
    parts: list[str] = []
    for index, token in enumerate(tokens):
        if index:
            # Hyphens are attached infixes; whitespace separates ordinary tokens.
            joiner = r"\s*" if token == "-" or tokens[index - 1] == "-" else " "
            parts.append(joiner)
        parts.append(_token_word(token))
    return r"(?<!\w)" + "".join(parts) + r"(?!\w)"


ASPECT_PATTERNS: dict[str, re.Pattern[str]] = {
    aspect: re.compile("|".join(_phrase_pattern(p) for p in phrases), re.IGNORECASE)
    for aspect, phrases in RISK_PHRASES.items()
}


def extract_aspects(text: str) -> list[str]:
    """Return the sorted complaint aspects whose phrases appear in ``text``."""
    content = str(text)
    return sorted(a for a, pattern in ASPECT_PATTERNS.items() if pattern.search(content))


def matched_phrases(text: str) -> dict[str, list[str]]:
    """Return the exact phrases matched for each detected aspect (for highlighting)."""
    content = str(text)
    found: dict[str, list[str]] = {}
    for aspect, pattern in ASPECT_PATTERNS.items():
        hits = sorted({m.group(0).lower() for m in pattern.finditer(content)})
        if hits:
            found[aspect] = hits
    return found


# --------------------------------------------------------------------------
# Review analysis (notebook section 13)
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class ReviewAnalysis:
    """Result of analyzing one review."""

    risk_probability: float
    operating_threshold: float
    management_attention: bool
    primary_aspect: str
    detected_aspects: list[str] = field(default_factory=list)
    matched_phrases: dict[str, list[str]] = field(default_factory=dict)
    recommended_action: str = ""
    model_used: str = ""

    def to_dict(self) -> dict[str, object]:
        """Return a plain dictionary (useful for JSON export and tests)."""
        return asdict(self)


def recommend_action(management_attention: bool, aspects: list[str]) -> tuple[str, str]:
    """Pick the primary aspect and the recommended management action.

    - Below the threshold: routine monitoring, never a manual investigation.
    - Above the threshold with a dictionary match: the aspect's action. The
      primary aspect follows the notebook (first detected aspect, sorted).
    - Above the threshold with no dictionary match: manual review.
    """
    primary = aspects[0] if aspects else NO_MATCH
    if not management_attention:
        return primary, ROUTINE_MONITORING
    return primary, RECOMMENDATIONS[primary]


def analyze_review(
    text: str,
    scorer: Callable[[str], float],
    threshold: float,
    model_used: str,
) -> ReviewAnalysis:
    """Score a review, explain it, and recommend a management action.

    Args:
        text: Raw review text. Masking is applied by the scorer.
        scorer: Function returning the negative-risk probability in [0, 1].
        threshold: Operating threshold selected on validation businesses.
        model_used: Human-readable model name for display.

    Raises:
        ValueError: If ``text`` is blank.
    """
    if not str(text).strip():
        raise ValueError("Review text is empty.")
    probability = float(scorer(text))
    if not 0.0 <= probability <= 1.0:
        raise ValueError(f"Scorer returned an invalid probability: {probability}")
    attention = probability >= threshold
    aspects = extract_aspects(text)
    primary, action = recommend_action(attention, aspects)
    return ReviewAnalysis(
        risk_probability=round(probability, 4),
        operating_threshold=round(float(threshold), 4),
        management_attention=attention,
        primary_aspect=primary,
        detected_aspects=aspects,
        matched_phrases=matched_phrases(text),
        recommended_action=action,
        model_used=model_used,
    )
