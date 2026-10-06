"""Cached loaders for the dashboard artifacts (never the raw Yelp CSV)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import streamlit as st

from app.config import ARTIFACTS_DIR, TIER_ORDER, TREND_THRESHOLD

REQUIRED_FILES = [
    "provider_risk_dashboard.csv",
    "service_risk_summary.csv",
    "aspect_summary.csv",
    "model_comparison.csv",
]


class ArtifactError(RuntimeError):
    """Raised when a required artifact is missing or malformed."""


def missing_artifacts(directory: Path = ARTIFACTS_DIR) -> list[str]:
    """Return the required artifact filenames that are not present."""
    return [name for name in REQUIRED_FILES if not (directory / name).exists()]


def _read_csv(name: str, **kwargs: Any) -> pd.DataFrame:
    path = ARTIFACTS_DIR / name
    if not path.exists():
        raise ArtifactError(f"Missing artifact: artifacts/{name}")
    return pd.read_csv(path, **kwargs)


def trend_direction(delta: float) -> str:
    """Label a recent-vs-2020 change in mean model risk."""
    if pd.isna(delta):
        return "Insufficient data"
    if delta > TREND_THRESHOLD:
        return "Rising"
    if delta < -TREND_THRESHOLD:
        return "Improving"
    return "Steady"


@st.cache_data(show_spinner=False)
def load_providers() -> pd.DataFrame:
    """Anonymized provider risk table with derived trend and tier ordering."""
    df = _read_csv("provider_risk_dashboard.csv")
    expected = {"provider_code", "service_group", "reviews", "risk_score", "risk_tier", "top_aspect"}
    if not expected.issubset(df.columns):
        raise ArtifactError("provider_risk_dashboard.csv is missing required columns.")
    if "name" in df.columns or "business_id" in df.columns:
        raise ArtifactError("Provider table must be anonymized (no names or business IDs).")
    df["risk_tier"] = pd.Categorical(df["risk_tier"], categories=TIER_ORDER, ordered=True)
    df["trend"] = df["trend_delta"].apply(trend_direction)
    if "latest_review" in df.columns:
        df["latest_review"] = pd.to_datetime(df["latest_review"], errors="coerce")
    return df.sort_values("risk_score", ascending=False).reset_index(drop=True)


@st.cache_data(show_spinner=False)
def load_service_summary() -> pd.DataFrame:
    return _read_csv("service_risk_summary.csv")


@st.cache_data(show_spinner=False)
def load_aspects() -> pd.DataFrame:
    return _read_csv("aspect_summary.csv")


@st.cache_data(show_spinner=False)
def load_model_comparison() -> pd.DataFrame:
    return _read_csv("model_comparison.csv")


@st.cache_data(show_spinner=False)
def load_optional(name: str) -> pd.DataFrame | None:
    """Load a supplementary artifact; return None when it is absent."""
    path = ARTIFACTS_DIR / name
    return pd.read_csv(path) if path.exists() else None


@st.cache_data(show_spinner=False)
def load_metadata() -> dict[str, Any]:
    path = ARTIFACTS_DIR / "metadata.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def tier_counts(providers: pd.DataFrame) -> pd.Series:
    """Provider counts per tier in display order (zero-filled)."""
    return providers["risk_tier"].value_counts().reindex(TIER_ORDER, fill_value=0).astype(int)


def safe_pct(value: float) -> str:
    return "—" if value is None or (isinstance(value, float) and np.isnan(value)) else f"{value:.0%}"
