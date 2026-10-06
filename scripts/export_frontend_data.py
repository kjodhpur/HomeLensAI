"""Export Rithik's artifacts + risk logic into static JSON for the Next.js app (frontend/data/).

The web app has NO separate backend. It imports these JSON files and runs a TypeScript port of the review analysis
(masking, complaint-phrase dictionary, TF-IDF logistic regression) inside its own route handler. Single sources of truth stay:

    artifacts/*.csv, *.joblib, metadata.json   (scripts/build_artifacts.py)      -> providers / overview / aspects / model
    app/risk_logic.py                          (masking rules, phrase dictionary) -> risk_config.json

    python scripts/export_frontend_data.py            # write frontend/data/*.json
    python scripts/export_frontend_data.py --check    # fail if the committed files are stale (used by CI)

`golden.json` holds Python's outputs for sample reviews; `npm test` in frontend/ asserts the TypeScript port reproduces them.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import risk_logic as rl  # noqa: E402
from app.config import NOTEBOOK_FACTS  # noqa: E402

ARTIFACTS = ROOT / "artifacts"
OUT = ROOT / "frontend" / "data"

TIER_ORDER = ["Stable", "Watch", "Elevated", "High concern"]
TIER_RULES = {"Stable": "Score below 50", "Watch": "Score 50–75", "Elevated": "Score 75–90", "High concern": "Score 90 and above"}
TREND_THRESHOLD = 0.05  # same as app/config.py
TFIDF_NAME = "TF–IDF Logistic Regression"
DISCLAIMER = (
    "Review-based risk signals for human investigation. They do not verify customer allegations "
    "or establish misconduct, liability or safety violations."
)
EXAMPLES = [  # synthetic, same set as the Streamlit analyzer (views/review_analyzer.py)
    {"id": "overcharged", "label": "Overcharged", "kind": "complaint",
     "text": "The technician was three hours late, charged more than the quote, and the repair failed again two days later."},
    {"id": "no-show", "label": "No-show", "kind": "complaint",
     "text": "They never showed for the scheduled appointment. I called four times and they never called back. "
             "When someone finally answered, the manager was very rude and unprofessional."},
    {"id": "property-damage", "label": "Property damage", "kind": "complaint",
     "text": "After the water heater install we found water damage under the cabinet. The company refused to fix it "
             "and said it was not under warranty. Completely dishonest experience."},
    {"id": "on-time", "label": "On time", "kind": "positive",
     "text": "The team arrived on time, explained the work clearly, and finished the installation professionally."},
    {"id": "follow-up", "label": "Great follow-up", "kind": "positive",
     "text": "Fair price, honest estimate, and the owner checked in a week later to make sure everything was still working. "
             "Highly recommend them for any plumbing job."},
]
GOLDEN_EXTRA = [
    "They NEVER SHOWED up and didn't call back. Total scam!",
    "Great work. Café était très bon, and the crew was professional.",
    "Call me at 520-555-1234, they charged $900 and the repair failed again.",
    "The unit is under warranty but they would not honor the warranty claim. Unsafe wiring left a fire hazard.",
    "Absolutely awful from start to end.",
    "ok",
]


def _read(name: str) -> list[dict[str, str]]:
    with (ARTIFACTS / name).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _num(v: str) -> float | None:
    return float(v) if v not in ("", None) else None


def trend_label(delta: float | None) -> str:
    if delta is None:
        return "Insufficient data"
    return "Rising" if delta > TREND_THRESHOLD else "Improving" if delta < -TREND_THRESHOLD else "Steady"


def providers() -> list[dict[str, Any]]:
    rows = _read("provider_risk_dashboard.csv")
    assert not ({"name", "business_id"} & set(rows[0])), "provider table must be anonymized"
    hist: dict[str, list[dict[str, Any]]] = {}
    for r in _read("provider_yearly_risk.csv"):
        hist.setdefault(r["provider_code"], []).append(
            {"year": int(r["review_year"]), "reviews": int(r["reviews"]), "risk": round(float(r["mean_risk_probability"]), 4)})
    out = []
    for r in rows:
        d = _num(r["trend_delta"])
        out.append({
            "code": r["provider_code"], "service_group": r["service_group"], "reviews": int(r["reviews"]),
            "observed_negative_rate": float(r["observed_negative_rate"]), "mean_risk": round(float(r["mean_risk_probability"]), 4),
            "recent_risk": None if _num(r["recent_risk_probability"]) is None else round(_num(r["recent_risk_probability"]), 4),
            "trend_delta": None if d is None else round(d, 4), "trend": trend_label(d),
            "high_severity_rate": round(float(r["high_severity_rate"]), 4), "top_aspect": r["top_aspect"],
            "risk_score": round(float(r["risk_score"]), 2), "risk_tier": r["risk_tier"], "recommended_action": r["recommended_action"],
            "recent_reviews": int(float(r["recent_reviews"])), "previous_reviews": int(float(r["previous_reviews"])),
            "latest_review": (r.get("latest_review") or "")[:10] or None,
            "history": sorted(hist.get(r["provider_code"], []), key=lambda h: h["year"]),
        })
    return sorted(out, key=lambda p: -p["risk_score"])


def aspects(provs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    led: dict[str, int] = {}
    for p in provs:
        led[p["top_aspect"]] = led.get(p["top_aspect"], 0) + 1
    out = []
    for r in _read("aspect_summary.csv"):
        a = r["aspect"]
        out.append({
            "aspect": a, "reviews_with_signal": int(r["reviews_with_signal"]), "share_of_corpus": round(float(r["share_of_corpus"]), 5),
            "negative_reviews_with_signal": int(r["negative_reviews_with_signal"]),
            "negative_rate_when_mentioned": round(float(r["negative_rate_when_mentioned"]), 4),
            "lift": round(float(r["lift_vs_corpus_negative_rate"]), 3), "high_severity": a in rl.HIGH_SEVERITY_ASPECTS,
            "keywords": rl.RISK_PHRASES.get(a, []), "recommended_action": rl.RECOMMENDATIONS.get(a, ""), "providers_led": led.get(a, 0),
        })
    return sorted(out, key=lambda a: -a["lift"])


def overview(provs: list[dict[str, Any]], meta: dict[str, Any]) -> dict[str, Any]:
    tl = [{"year": int(r["review_year"]), "reviews": int(r["reviews"]), "negative_rate": round(float(r["negative_rate"]), 4)}
          for r in _read("corpus_timeline.csv")]
    end_year, end_month = int(meta["date_end"][:4]), int(meta["date_end"][5:7])
    full = [t for t in tl if t["reviews"] >= 50 and not (t["year"] == end_year and end_month < 12)]
    shift = None
    if len(full) >= 2:
        a, b = full[-2], full[-1]
        shift = {"from_year": a["year"], "to_year": b["year"], "from_rate": a["negative_rate"], "to_rate": b["negative_rate"],
                 "delta_pts": round((b["negative_rate"] - a["negative_rate"]) * 100, 2)}
    tiers = {t: 0 for t in TIER_ORDER}
    for p in provs:
        tiers[p["risk_tier"]] += 1
    high = [p for p in provs if p["risk_tier"] == "High concern"]
    by_year: dict[int, list[tuple[int, float]]] = {}
    for p in high:
        for h in p["history"]:
            by_year.setdefault(h["year"], []).append((h["reviews"], h["risk"]))
    esc = [{"x": y, "y": round(sum(n * r for n, r in v) / sum(n for n, _ in v), 4)} for y, v in sorted(by_year.items()) if len(v) >= 2 and y >= 2012]
    services = [{"service_group": r["service_group"], "monitored_providers": int(r["eligible_businesses"]),
                 "median_risk_score": round(float(r["median_risk_score"]), 2), "high_concern_providers": int(r["high_concern_providers"]),
                 "median_recent_risk": round(float(r["median_recent_risk"]), 3)} for r in _read("service_risk_summary.csv")]
    models = [{k: (v if k == "model" else float(v)) for k, v in r.items()} for r in _read("model_comparison.csv")]
    return {
        "meta": {"market": meta["market"], "date_start": meta["date_start"], "date_end": meta["date_end"], "core_reviews": meta["core_reviews"],
                 "providers": meta["providers"], "monitored_providers": meta["monitored_providers"],
                 "min_reviews": meta.get("min_reviews_for_monitoring", 20), "provider_scores_model": meta.get("provider_scores_model")},
        "kpis": {
            "reviews_analyzed": {"value": meta["core_reviews"], "series": [{"x": t["year"], "y": t["reviews"]} for t in full],
                                 "providers": meta["providers"], "unique_reviewers": meta["unique_reviewers"]},
            "sentiment_shift": {"shift": shift, "series": [{"x": t["year"], "y": t["negative_rate"]} for t in full]},
            "escalations": {"value": tiers["High concern"], "elevated": tiers["Elevated"], "monitored": len(provs), "series": esc,
                            "codes": [p["code"] for p in high]},
        },
        "tiers": tiers, "tier_rules": TIER_RULES, "services": services, "models": models,
    }


def risk_config(meta: dict[str, Any]) -> dict[str, Any]:
    return {
        "masking_rules": [{"source": p.pattern, "replacement": rep} for p, rep in rl._COMPILED_MASKS],  # all IGNORECASE
        "aspect_patterns": {a: p.pattern for a, p in rl.ASPECT_PATTERNS.items()},                        # compiled by risk_logic
        "high_severity_aspects": list(rl.HIGH_SEVERITY_ASPECTS), "no_match": rl.NO_MATCH, "recommendations": rl.RECOMMENDATIONS,
        "routine_monitoring": rl.ROUTINE_MONITORING, "threshold": float(meta["tfidf_threshold"]), "model_name": TFIDF_NAME, "disclaimer": DISCLAIMER,
    }


def tfidf_model() -> dict[str, Any]:
    import joblib
    from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

    vec = joblib.load(ARTIFACTS / "homelens_tfidf_vectorizer.joblib")
    clf = joblib.load(ARTIFACTS / "homelens_tfidf_logistic_regression.joblib")
    p = vec.get_params()
    assert (p["lowercase"], p["strip_accents"], p["stop_words"], p["ngram_range"], p["norm"], p["sublinear_tf"], p["use_idf"], p["binary"]) == \
        (True, "unicode", "english", (1, 2), "l2", True, True, False), "vectorizer settings changed — update frontend/lib/engine/tfidf.ts"
    assert p["token_pattern"] == r"(?u)\b\w\w+\b" and list(clf.classes_) == [0, 1]
    names = vec.get_feature_names_out()
    return {"terms": [str(t) for t in names], "idf": [round(float(x), 6) for x in vec.idf_], "coef": [round(float(x), 6) for x in clf.coef_[0]],
            "intercept": round(float(clf.intercept_[0]), 6), "stop_words": sorted(ENGLISH_STOP_WORDS)}


_SENT = re.compile(r"[^.!?\n]+(?:[.!?]+|\n|$)")


def golden(meta: dict[str, Any]) -> list[dict[str, Any]]:
    """Python's own outputs for sample reviews; the TypeScript port must reproduce them (frontend `npm test`)."""
    import joblib

    vec = joblib.load(ARTIFACTS / "homelens_tfidf_vectorizer.joblib")
    clf = joblib.load(ARTIFACTS / "homelens_tfidf_logistic_regression.joblib")
    thr = float(meta["tfidf_threshold"])

    def score(t: str) -> float:
        return float(clf.predict_proba(vec.transform([rl.mask_sensitive_and_leakage(t)]))[0, 1])

    out = []
    for text in [e["text"] for e in EXAMPLES] + GOLDEN_EXTRA:
        res = rl.analyze_review(text, score, thr, TFIDF_NAME)
        sents = [text[m.start():m.end()] for m in _SENT.finditer(text) if m.group(0).strip()]
        out.append({"text": text, "risk_probability": res.risk_probability, "management_attention": res.management_attention,
                    "primary_aspect": res.primary_aspect, "detected_aspects": res.detected_aspects, "matched_phrases": res.matched_phrases,
                    "recommended_action": res.recommended_action,
                    "sentence_probabilities": [round(score(s), 6) for s in sents], "sentences": [s.strip() for s in sents],
                    "raw_probability": score(text)})
    return out


def build() -> dict[str, str]:
    meta = json.loads((ARTIFACTS / "metadata.json").read_text(encoding="utf-8"))
    provs = providers()
    files = {
        "providers.json": provs, "aspects.json": aspects(provs), "overview.json": overview(provs, meta), "examples.json": EXAMPLES,
        "risk_config.json": risk_config(meta), "tfidf_model.json": tfidf_model(), "golden.json": golden(meta),
        "facts.json": NOTEBOOK_FACTS,  # validated notebook facts (app/config.py): splits, thresholds, recall floor
    }
    return {name: json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n" for name, data in files.items()}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="exit non-zero if frontend/data is out of date")
    args = ap.parse_args()
    built = build()
    if args.check:
        stale = [n for n, s in built.items() if not (OUT / n).exists() or (OUT / n).read_text(encoding="utf-8") != s]
        if stale:
            raise SystemExit(f"frontend/data is stale: {stale} — run `python scripts/export_frontend_data.py` and commit")
        print("frontend/data is up to date")
        return
    OUT.mkdir(parents=True, exist_ok=True)
    for name, s in built.items():
        (OUT / name).write_text(s, encoding="utf-8")
        print(f"wrote frontend/data/{name}  ({len(s) / 1024:,.0f} KB)")


if __name__ == "__main__":
    main()
