"""Runtime configuration, read from environment variables (see .env.example)."""

from __future__ import annotations

import os
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent

# Vendored copy of the repo-level ``artifacts/`` folder (written by ``python scripts/sync_artifacts.py``).
ARTIFACTS_DIR = Path(os.environ.get("HOMELENS_ARTIFACTS_DIR", APP_DIR / "data" / "artifacts"))

# Comma-separated list of browser origins allowed to call the API directly (the Next.js app normally proxies via
# rewrites, so this only matters for local tools and for a frontend deployed on a different domain).
CORS_ORIGINS = [o.strip() for o in os.environ.get("CORS_ORIGINS", "http://localhost:3000").split(",") if o.strip()]
# Allow any *.vercel.app preview URL (set CORS_ALLOW_VERCEL_PREVIEWS=0 to disable).
CORS_ALLOW_VERCEL_PREVIEWS = os.environ.get("CORS_ALLOW_VERCEL_PREVIEWS", "1") == "1"

# Set HOMELENS_DISABLE_MODEL=1 to serve dictionary-only analysis (e.g. if scikit-learn is unavailable).
MODEL_ENABLED = os.environ.get("HOMELENS_DISABLE_MODEL", "0") != "1"

MAX_ANALYZE_CHARS = 5000
MAX_SENTENCES = 40

# Mirrors app/config.py of the Streamlit app.
TIER_ORDER = ["Stable", "Watch", "Elevated", "High concern"]
TIER_RULES = {"Stable": "Score below 50", "Watch": "Score 50–75", "Elevated": "Score 75–90", "High concern": "Score 90 and above"}
TREND_THRESHOLD = 0.05  # recent (2021+) vs 2020 change in mean model risk
TFIDF_NAME = "TF–IDF Logistic Regression"
DISCLAIMER = (
    "Review-based risk signals for human investigation. They do not verify customer allegations "
    "or establish misconduct, liability or safety violations."
)
