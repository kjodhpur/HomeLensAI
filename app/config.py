"""Static configuration: paths, brand tokens, risk-tier styling, validated facts."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS_DIR = ROOT / "artifacts"
ASSETS_DIR = ROOT / "assets"

APP_NAME = "HomeLens AI"
APP_TAGLINE = "Business Risk Command Center"

# --------------------------------------------------------------------------
# Brand tokens (mirrored in app/ui_components.py CSS variables)
# --------------------------------------------------------------------------
PURPLE = "#6C47FF"
PURPLE_DARK = "#5A35F0"
PURPLE_SOFT = "#EFEBFF"
NAVY = "#0E1530"
INK = "#141A33"
INK_2 = "#4A5272"
MUTED = "#8A90A8"
GRID = "#ECEEF5"
BASELINE = "#C9CDDC"
SURFACE = "#FFFFFF"

# Model colors: validated as a colorblind-safe categorical set (all pairs).
MODEL_COLORS = {
    "Fine-tuned DistilBERT": PURPLE,
    "TF–IDF Logistic Regression": "#EB6834",
    "TextBlob": "#1BAF7A",
}

# Reserved status palette, always paired with a text label.
TIER_ORDER = ["Stable", "Watch", "Elevated", "High concern"]
TIER_COLORS = {
    "Stable": "#0CA30C",
    "Watch": "#FAB219",
    "Elevated": "#EC835A",
    "High concern": "#D03B3B",
}
TIER_TEXT = {  # AA-contrast text tones on tinted backgrounds
    "Stable": "#0A6B0A",
    "Watch": "#8A5A00",
    "Elevated": "#A6481F",
    "High concern": "#A82424",
}
TIER_BG = {
    "Stable": "#E6F6E6",
    "Watch": "#FFF4DB",
    "Elevated": "#FDEDE5",
    "High concern": "#FBE6E6",
}
TIER_RULES = {
    "Stable": "Score below 50",
    "Watch": "Score 50–75",
    "Elevated": "Score 75–90",
    "High concern": "Score 90 and above",
}

# Trend labels for the provider monitor (recent 2021+ vs. 2020 mean risk).
TREND_THRESHOLD = 0.05
TREND_ORDER = ["Rising", "Steady", "Improving", "Insufficient data"]

# --------------------------------------------------------------------------
# Validated facts from the executed final notebook
# --------------------------------------------------------------------------
NOTEBOOK_FACTS: dict[str, Any] = {
    "candidate_reviews": 23_685,
    "core_reviews": 17_943,
    "providers": 1_054,
    "unique_reviewers": 12_384,
    "monitored_providers": 254,
    "date_start": "Nov 2006",
    "date_end": "Jan 2022",
    "market": "Tucson, AZ",
    "median_words": 83,
    "split": [  # business-held-out partitions
        {"split": "Train", "reviews": 10_411, "businesses": 630, "negative_rate": 0.355},
        {"split": "Validation", "reviews": 3_691, "businesses": 211, "negative_rate": 0.319},
        {"split": "Test", "reviews": 3_331, "businesses": 213, "negative_rate": 0.330},
    ],
    "validation_macro_f1": {"Fine-tuned DistilBERT": 0.970, "TF–IDF Logistic Regression": 0.944},
    "test_negatives": 1_100,
    "test_positives": 2_231,
    "distilbert_threshold": 0.95,
    "tfidf_threshold": 0.62,
    "recall_floor": 0.90,
}

DISTILBERT_NAME = "Fine-tuned DistilBERT"
TFIDF_NAME = "TF–IDF Logistic Regression"
MAX_LENGTH = 256


def get_secret(name: str, default: str | None = None) -> str | None:
    """Read a setting from ``st.secrets`` first, then the environment.

    Never logs or displays the value.
    """
    try:
        import streamlit as st

        if name in st.secrets:
            value = st.secrets[name]
            return str(value) if value is not None else default
    except Exception:  # no secrets.toml, or not running under Streamlit
        pass
    return os.environ.get(name, default)
