"""Runtime configuration, read from environment variables (see .env.example)."""

from __future__ import annotations

import os
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent

# Where the JSON artifacts live. `provider_risk.json` here wins over `sample/provider_risk.json`.
DATA_DIR = Path(os.environ.get("HOMELENS_DATA_DIR", APP_DIR / "data"))

# Comma-separated list of browser origins allowed to call the API directly (the Next.js app normally proxies via
# rewrites, so this only matters for local tools and for a frontend deployed on a different domain).
CORS_ORIGINS = [o.strip() for o in os.environ.get("CORS_ORIGINS", "http://localhost:3000").split(",") if o.strip()]
# Allow any *.vercel.app preview URL (set CORS_ALLOW_VERCEL_PREVIEWS=0 to disable).
CORS_ALLOW_VERCEL_PREVIEWS = os.environ.get("CORS_ALLOW_VERCEL_PREVIEWS", "1") == "1"

MAX_ANALYZE_CHARS = 5000
