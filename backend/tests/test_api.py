"""API tests. They run against the vendored artifacts in app/data/artifacts/."""

from __future__ import annotations

import filecmp
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app import artifacts, scoring
from app.main import app

client = TestClient(app)
ROOT = Path(__file__).resolve().parents[2]
NEGATIVE = "The technician was three hours late, charged more than the quote, and the repair failed again two days later."
POSITIVE = "The team arrived on time, explained the work clearly, and finished the installation professionally."


def test_health():
    body = client.get("/api/health").json()
    assert body["status"] == "ok" and body["providers"] > 100 and body["model_available"] is True


def test_providers_are_anonymized_and_have_min_reviews():
    body = client.get("/api/providers").json()
    assert body["total"] == len(body["items"]) > 100
    for p in body["items"]:
        assert p["code"].startswith("Provider_") and p["reviews"] >= 20
        assert "name" not in p and "business_id" not in p
    scores = [p["risk_score"] for p in body["items"]]
    assert scores == sorted(scores, reverse=True)


@pytest.mark.parametrize("tier", ["Stable", "Watch", "Elevated", "High concern"])
def test_tier_filter(tier):
    items = client.get("/api/providers", params={"tier": tier}).json()["items"]
    assert items and all(p["risk_tier"] == tier for p in items)


def test_filters_sort_and_pagination():
    assert client.get("/api/providers", params={"tier": "Nope"}).status_code == 422
    assert client.get("/api/providers", params={"min_reviews": 5}).status_code == 422
    a = client.get("/api/providers", params={"sort": "reviews", "limit": 5}).json()["items"]
    assert [p["reviews"] for p in a] == sorted((p["reviews"] for p in a), reverse=True)
    b = client.get("/api/providers", params={"sort": "reviews", "limit": 5, "offset": 5}).json()["items"]
    assert not {p["code"] for p in a} & {p["code"] for p in b}
    assert client.get("/api/providers", params={"q": "zzzz"}).json()["total"] == 0


def test_trend_labels_match_rule():
    for p in client.get("/api/providers").json()["items"]:
        assert p["trend"] == artifacts.trend_label(p["trend_delta"])


def test_provider_detail_and_404():
    code = client.get("/api/providers", params={"limit": 1}).json()["items"][0]["code"]
    body = client.get(f"/api/providers/{code}").json()
    assert body["code"] == code and body["service_benchmark"]["service_group"] == body["service_group"] and body["history"]
    assert client.get("/api/providers/Provider_0000").status_code == 404


def test_overview_kpis():
    o = client.get("/api/overview").json()
    k = o["kpis"]
    assert k["reviews_analyzed"]["value"] == 17943 and len(k["reviews_analyzed"]["series"]) >= 5
    shift = k["sentiment_shift"]["shift"]
    assert (shift["from_year"], shift["to_year"]) == (2020, 2021) and shift["delta_pts"] == pytest.approx(8.33, abs=0.05)
    assert k["escalations"]["value"] == o["tiers"]["High concern"] == len(k["escalations"]["codes"])
    assert sum(o["tiers"].values()) == k["escalations"]["monitored"]


def test_aspects_cover_all_eight_with_keyword_clusters():
    a = client.get("/api/aspects").json()
    assert len(a) == 8 and all(x["keywords"] and x["lift"] > 1 and x["recommended_action"] for x in a)
    assert {x["aspect"] for x in a if x["high_severity"]} == {"Workmanship", "Safety / Property Damage", "Warranty / Follow-up"}


def test_analyze_complaint():
    r = client.post("/api/analyze", json={"text": NEGATIVE}).json()
    assert r["management_attention"] is True and r["risk_probability"] >= r["operating_threshold"]
    assert set(r["detected_aspects"]) == {"Pricing / Billing", "Timeliness", "Workmanship"}
    assert r["evidence"]["has_dictionary_match"] and r["evidence"]["sentence"] in NEGATIVE
    assert r["sentences"] and r["model"]["name"] == "TF–IDF Logistic Regression"
    w = r["weights"]
    assert w["terms"] and w["logit"] == pytest.approx(w["bias"] + w["explained_positive"] + w["explained_negative"], abs=0.01)
    assert r["recommended_action"]


def test_analyze_positive_is_routine():
    r = client.post("/api/analyze", json={"text": POSITIVE}).json()
    assert r["management_attention"] is False and r["detected_aspects"] == []
    assert "Routine monitoring" in r["recommended_action"]


def test_analyze_masks_sensitive_text():
    r = client.post("/api/analyze", json={"text": "Call me at 520-555-1234, they charged $900 and never showed up."}).json()
    assert r["masking_applied"] is True and "Reliability / No-show" in r["detected_aspects"]


def test_analyze_sentence_spans_reconstruct_text():
    text = "They never showed up. I called four times! Nobody answered."
    r = client.post("/api/analyze", json={"text": text}).json()
    assert [text[s["start"] : s["end"]].strip() for s in r["sentences"]] == [s["text"] for s in r["sentences"]]
    assert len(r["sentences"]) == 3


def test_analyze_validation():
    assert client.post("/api/analyze", json={"text": ""}).status_code == 422
    assert client.post("/api/analyze", json={"text": "   "}).status_code == 422
    assert client.post("/api/analyze", json={"text": "x" * 6000}).status_code == 422


def test_analyze_dictionary_only_fallback(monkeypatch):
    monkeypatch.setattr(scoring, "load_model", lambda: None)
    r = client.post("/api/analyze", json={"text": NEGATIVE}).json()
    assert r["model"]["available"] is False and r["risk_probability"] is None and r["weights"] is None
    assert "Workmanship" in r["detected_aspects"] and r["evidence"]["sentence"]


def test_examples():
    ex = client.get("/api/examples").json()
    assert {e["kind"] for e in ex} == {"complaint", "positive"}


def test_vendored_files_match_sources():
    """backend/app/risk_logic.py and backend/app/data/artifacts/* are copies made by scripts/sync_artifacts.py."""
    if not (ROOT / "app" / "risk_logic.py").exists():
        pytest.skip("repository root not available (backend deployed standalone)")
    assert filecmp.cmp(ROOT / "app" / "risk_logic.py", Path(__file__).resolve().parents[1] / "app" / "risk_logic.py", shallow=False)
    for src in (ROOT / "artifacts").iterdir():
        if src.suffix in {".csv", ".json", ".joblib"}:
            dst = artifacts.config.ARTIFACTS_DIR / src.name
            assert dst.exists() and filecmp.cmp(src, dst, shallow=False), f"{src.name} is stale — run scripts/sync_artifacts.py"
