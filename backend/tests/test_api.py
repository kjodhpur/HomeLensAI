"""Smoke + behaviour tests. They run against the committed synthetic sample artifacts (app/data/sample/)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app import store
from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok" and body["providers"] > 0


def test_summary_has_models_and_aspects():
    body = client.get("/api/summary").json()
    assert {"dataset", "models", "aspects", "tiers", "meta"} <= body.keys()
    assert len(body["aspects"]) == 8


def test_list_default_sorted_by_rank_and_eligible_only():
    body = client.get("/api/providers?limit=5").json()
    assert body["total"] > 0 and len(body["items"]) <= 5
    ranks = [p["rank"] for p in body["items"]]
    assert ranks == sorted(ranks)
    assert all(p["eligible"] for p in body["items"])


@pytest.mark.parametrize("tier", ["High", "Medium", "Low"])
def test_tier_filter(tier):
    body = client.get(f"/api/providers?tier={tier}&limit=200").json()
    assert all(p["risk_tier"] == tier for p in body["items"])


def test_sort_by_reviews_desc_and_pagination():
    a = client.get("/api/providers?sort=n_reviews&limit=3").json()["items"]
    assert [p["n_reviews"] for p in a] == sorted((p["n_reviews"] for p in a), reverse=True)
    b = client.get("/api/providers?sort=n_reviews&limit=3&offset=3").json()["items"]
    assert not {p["business_id"] for p in a} & {p["business_id"] for p in b}


def test_text_search_and_unknown_filter_values():
    assert client.get("/api/providers?q=zzzz-no-such-name").json()["total"] == 0
    assert client.get("/api/providers?tier=Nope").status_code == 422


def test_provider_detail_and_404():
    first = client.get("/api/providers?limit=1").json()["items"][0]
    detail = client.get(f"/api/providers/{first['business_id']}")
    assert detail.status_code == 200
    body = detail.json()
    assert body["business_id"] == first["business_id"] and "issues" in body and "action_manager" in body
    assert client.get("/api/providers/does-not-exist").status_code == 404


def test_every_recurring_issue_has_evidence():
    for p in store.provider_risk()["providers"]:
        for issue in p["issues"]:
            if p["eligible"] and issue["recurring"]:
                assert issue["evidence"], f"{p['name']} / {issue['aspect']} has no evidence sentence"


def test_aspects_endpoint():
    assert {a["key"] for a in client.get("/api/aspects").json()} == {
        "workmanship", "reliability", "pricing", "communication", "timeliness", "professionalism", "warranty", "safety",
    }


def test_analyze_flags_complaints_and_ignores_praise():
    bad = client.post("/api/analyze", json={"text": "They never showed up and overcharged me. Hidden fees everywhere, total rip off."}).json()
    assert {"reliability", "pricing"} <= set(bad["aspects"])
    good = client.post("/api/analyze", json={"text": "No hidden fees, they were not late at all and honored the warranty. Great work!"}).json()
    assert good["aspects"] == []


def test_analyze_validation():
    assert client.post("/api/analyze", json={"text": ""}).status_code == 422
    assert client.post("/api/analyze", json={"text": "x" * 6000}).status_code == 422
