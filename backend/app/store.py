"""Loads and caches the JSON artifacts written by notebooks/HomeLensAI_Final_Project.ipynb (Section 9)."""

from __future__ import annotations

import json
from functools import cache, lru_cache
from pathlib import Path
from typing import Any

from . import config


class DataNotFoundError(RuntimeError):
    pass


def _locate(name: str) -> Path:
    """Real artifacts (data/<name>) take precedence over the committed synthetic sample (data/sample/<name>)."""
    for candidate in (config.DATA_DIR / name, config.DATA_DIR / "sample" / name):
        if candidate.exists():
            return candidate
    raise DataNotFoundError(
        f"{name} not found in {config.DATA_DIR} or {config.DATA_DIR / 'sample'}. "
        "Run the notebook and `python scripts/sync_artifacts.py`, or see docs/TEAM_GUIDE.md."
    )


@cache
def _load(name: str) -> Any:
    return json.loads(_locate(name).read_text(encoding="utf-8"))


def provider_risk() -> dict[str, Any]:
    return _load("provider_risk.json")


def summary() -> dict[str, Any]:
    return _load("summary.json")


def lexicon() -> dict[str, Any]:
    return _load("aspect_lexicon.json")


@lru_cache(maxsize=1)
def providers_by_id() -> dict[str, dict[str, Any]]:
    return {p["business_id"]: p for p in provider_risk()["providers"]}


def reload() -> None:
    """Drop caches (used by tests and by a future /admin/reload route)."""
    _load.cache_clear()
    providers_by_id.cache_clear()
