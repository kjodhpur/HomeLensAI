"""Read-only loaders for the anonymized dashboard artifacts (never the raw Yelp CSV)."""

from __future__ import annotations

import csv
import json
from functools import lru_cache
from typing import Any

from . import config
from .risk_logic import HIGH_SEVERITY_ASPECTS, RECOMMENDATIONS, RISK_PHRASES

REQUIRED = ("provider_risk_dashboard.csv", "service_risk_summary.csv", "aspect_summary.csv", "model_comparison.csv")


class ArtifactError(RuntimeError):
    """A required artifact is missing or malformed."""


def _num(value: str) -> float | None:
    return float(value) if value not in ("", None) else None


def _read(name: str, required: bool = True) -> list[dict[str, str]]:
    path = config.ARTIFACTS_DIR / name
    if not path.exists():
        if required:
            raise ArtifactError(f"Missing artifact: {name} (run `python scripts/sync_artifacts.py`)")
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def trend_label(delta: float | None) -> str:
    """Label a recent-vs-2020 change in mean model risk (same rule as the Streamlit app)."""
    if delta is None:
        return "Insufficient data"
    if delta > config.TREND_THRESHOLD:
        return "Rising"
    if delta < -config.TREND_THRESHOLD:
        return "Improving"
    return "Steady"


@lru_cache(maxsize=1)
def metadata() -> dict[str, Any]:
    path = config.ARTIFACTS_DIR / "metadata.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


@lru_cache(maxsize=1)
def providers() -> list[dict[str, Any]]:
    """Anonymized provider table (>= 20 reviews each) with yearly history, sorted by risk score."""
    rows = _read("provider_risk_dashboard.csv")
    if rows and ({"name", "business_id"} & set(rows[0])):
        raise ArtifactError("Provider table must be anonymized (no names or business IDs).")
    history: dict[str, list[dict[str, Any]]] = {}
    for r in _read("provider_yearly_risk.csv", required=False):
        history.setdefault(r["provider_code"], []).append(
            {"year": int(r["review_year"]), "reviews": int(r["reviews"]), "risk": round(float(r["mean_risk_probability"]), 4)}
        )
    out = []
    for r in rows:
        delta = _num(r["trend_delta"])
        out.append(
            {
                "code": r["provider_code"],
                "service_group": r["service_group"],
                "reviews": int(r["reviews"]),
                "observed_negative_rate": float(r["observed_negative_rate"]),
                "mean_risk": float(r["mean_risk_probability"]),
                "recent_risk": _num(r["recent_risk_probability"]),
                "trend_delta": delta,
                "trend": trend_label(delta),
                "high_severity_rate": float(r["high_severity_rate"]),
                "top_aspect": r["top_aspect"],
                "risk_score": round(float(r["risk_score"]), 2),
                "risk_tier": r["risk_tier"],
                "recommended_action": r["recommended_action"],
                "recent_reviews": int(float(r["recent_reviews"])),
                "previous_reviews": int(float(r["previous_reviews"])),
                "latest_review": (r.get("latest_review") or "")[:10] or None,
                "history": sorted(history.get(r["provider_code"], []), key=lambda h: h["year"]),
            }
        )
    return sorted(out, key=lambda p: -p["risk_score"])


def provider(code: str) -> dict[str, Any] | None:
    return next((p for p in providers() if p["code"] == code), None)


@lru_cache(maxsize=1)
def services() -> list[dict[str, Any]]:
    return [
        {
            "service_group": r["service_group"],
            "monitored_providers": int(r["eligible_businesses"]),
            "median_risk_score": round(float(r["median_risk_score"]), 2),
            "high_concern_providers": int(r["high_concern_providers"]),
            "median_recent_risk": round(float(r["median_recent_risk"]), 3),
        }
        for r in _read("service_risk_summary.csv")
    ]


@lru_cache(maxsize=1)
def models() -> list[dict[str, Any]]:
    return [{k: (v if k == "model" else float(v)) for k, v in r.items()} for r in _read("model_comparison.csv")]


@lru_cache(maxsize=1)
def timeline() -> list[dict[str, Any]]:
    return [
        {"year": int(r["review_year"]), "reviews": int(r["reviews"]), "negative_rate": round(float(r["negative_rate"]), 4)}
        for r in _read("corpus_timeline.csv", required=False)
    ]


@lru_cache(maxsize=1)
def signal_terms() -> dict[str, list[dict[str, Any]]]:
    rows = _read("tfidf_signal_terms.csv", required=False)
    return {
        "negative": [{"term": r["negative_signal_terms"], "weight": float(r["negative_coefficient"])} for r in rows],
        "positive": [{"term": r["positive_signal_terms"], "weight": float(r["positive_coefficient"])} for r in rows],
    }


@lru_cache(maxsize=1)
def aspects() -> list[dict[str, Any]]:
    """The 8 complaint aspects: corpus statistics + keyword cluster (the phrase dictionary) + recommended action."""
    top_counts: dict[str, int] = {}
    for p in providers():
        top_counts[p["top_aspect"]] = top_counts.get(p["top_aspect"], 0) + 1
    out = []
    for r in _read("aspect_summary.csv"):
        name = r["aspect"]
        out.append(
            {
                "aspect": name,
                "reviews_with_signal": int(r["reviews_with_signal"]),
                "share_of_corpus": float(r["share_of_corpus"]),
                "negative_reviews_with_signal": int(r["negative_reviews_with_signal"]),
                "negative_rate_when_mentioned": float(r["negative_rate_when_mentioned"]),
                "lift": round(float(r["lift_vs_corpus_negative_rate"]), 3),
                "high_severity": name in HIGH_SEVERITY_ASPECTS,
                "keywords": RISK_PHRASES.get(name, []),
                "recommended_action": RECOMMENDATIONS.get(name, ""),
                "providers_led": top_counts.get(name, 0),
            }
        )
    return sorted(out, key=lambda a: -a["lift"])


def _tiers() -> dict[str, int]:
    counts = {t: 0 for t in config.TIER_ORDER}
    for p in providers():
        counts[p["risk_tier"]] = counts.get(p["risk_tier"], 0) + 1
    return counts


def overview() -> dict[str, Any]:
    """Headline numbers, KPI sparklines and portfolio breakdowns for the dashboard header."""
    meta = metadata()
    tl = timeline()
    end_year = int(str(meta.get("date_end", "0000"))[:4]) if meta else 0
    end_month = int(str(meta.get("date_end", "0000-01"))[5:7]) if meta else 12
    full = [t for t in tl if t["reviews"] >= 50 and not (t["year"] == end_year and end_month < 12)]
    shift = None
    if len(full) >= 2:
        a, b = full[-2], full[-1]
        shift = {"from_year": a["year"], "to_year": b["year"], "from_rate": a["negative_rate"], "to_rate": b["negative_rate"],
                 "delta_pts": round((b["negative_rate"] - a["negative_rate"]) * 100, 2)}

    tiers = _tiers()
    high = [p for p in providers() if p["risk_tier"] == "High concern"]
    by_year: dict[int, list[tuple[int, float]]] = {}
    for p in high:
        for h in p["history"]:
            by_year.setdefault(h["year"], []).append((h["reviews"], h["risk"]))
    esc_series = [
        {"x": y, "y": round(sum(n * r for n, r in v) / sum(n for n, _ in v), 4)}
        for y, v in sorted(by_year.items()) if len(v) >= 2 and y >= 2012
    ]
    return {
        "meta": {
            "market": meta.get("market"), "date_start": meta.get("date_start"), "date_end": meta.get("date_end"),
            "core_reviews": meta.get("core_reviews"), "providers": meta.get("providers"),
            "monitored_providers": meta.get("monitored_providers"), "min_reviews": meta.get("min_reviews_for_monitoring", 20),
            "provider_scores_model": meta.get("provider_scores_model"),
        },
        "kpis": {
            "reviews_analyzed": {"value": meta.get("core_reviews"), "series": [{"x": t["year"], "y": t["reviews"]} for t in full],
                                 "providers": meta.get("providers"), "unique_reviewers": meta.get("unique_reviewers")},
            "sentiment_shift": {"shift": shift, "series": [{"x": t["year"], "y": t["negative_rate"]} for t in full]},
            "escalations": {"value": tiers.get("High concern", 0), "elevated": tiers.get("Elevated", 0), "monitored": len(providers()),
                            "series": esc_series, "codes": [p["code"] for p in high]},
        },
        "tiers": tiers,
        "tier_rules": config.TIER_RULES,
        "services": services(),
        "models": models(),
        "timeline": tl,
        "signal_terms": signal_terms(),
    }
