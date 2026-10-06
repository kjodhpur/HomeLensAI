"""HomeLens AI API (FastAPI).

Run locally:   uvicorn app.main:app --reload --port 8000      (from the backend/ folder)
Docs (auto):   http://localhost:8000/docs
Vercel:        detected automatically — `app` in app/main.py is the entrypoint (see docs/DEPLOYMENT.md).
"""

from __future__ import annotations

from typing import Any, Literal

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from . import analyzer, config, store

app = FastAPI(
    title="HomeLens AI API",
    version="0.1.0",
    description=(
        "Serves provider-level risk intelligence derived from customer reviews. "
        "All outputs are *complaint signals detected in reviews* — unverified allegations, not findings of wrongdoing."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_origin_regex=r"https://.*\.vercel\.app" if config.CORS_ALLOW_VERCEL_PREVIEWS else None,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.exception_handler(store.DataNotFoundError)
async def _data_missing(_, exc: store.DataNotFoundError):  # pragma: no cover - exercised only when artifacts are absent
    from fastapi.responses import JSONResponse

    return JSONResponse(status_code=503, content={"detail": str(exc)})


# ---------------------------------------------------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------------------------------------------------
LIST_FIELDS = (
    "business_id", "name", "trade", "city", "state", "eligible", "n_reviews", "avg_stars", "neg_rate", "risk_score", "risk_tier", "rank",
    "safety_escalation",
)


def _list_item(p: dict[str, Any]) -> dict[str, Any]:
    """Light-weight projection used by the list endpoint (no evidence sentences / history → small payload)."""
    item = {k: p[k] for k in LIST_FIELDS}
    item["trend"] = p["trend"]["direction"]
    item["recent_neg_rate"] = p["recent"]["neg_rate"]
    item["prior_neg_rate"] = p["prior"]["neg_rate"]
    item["top_issues"] = [{"aspect": i["aspect"], "label": i["label"], "n_reviews": i["n_reviews"], "recurring": i["recurring"]} for i in p["issues"][:3]]
    return item


# ---------------------------------------------------------------------------------------------------------------------
# routes
# ---------------------------------------------------------------------------------------------------------------------
@app.get("/api/health", tags=["meta"])
def health() -> dict[str, Any]:
    meta = store.provider_risk()["meta"]
    return {"status": "ok", "data_mode": meta["data_mode"], "generated_at": meta["generated_at"], "providers": meta["n_providers_total"]}


@app.get("/api/summary", tags=["meta"])
def summary() -> dict[str, Any]:
    """Dataset facts, model metrics, tier counts, aspect prevalence and trade breakdown for the dashboard header."""
    return store.summary()


@app.get("/api/aspects", tags=["meta"])
def aspects() -> list[dict[str, Any]]:
    """The 8-aspect taxonomy (label, severity, description) — handy for filter chips and legends."""
    return [
        {"key": k, "label": v["label"], "severity": v["severity"], "description": v["description"]}
        for k, v in store.lexicon()["aspects"].items()
    ]


@app.get("/api/providers", tags=["providers"])
def list_providers(
    q: str | None = Query(None, description="case-insensitive substring of the provider name"),
    trade: str | None = None,
    tier: Literal["High", "Medium", "Low", "Insufficient data"] | None = None,
    trend: Literal["worsening", "improving", "stable", "insufficient data"] | None = None,
    aspect: str | None = Query(None, description="only providers with a recurring issue of this aspect, e.g. 'safety'"),
    eligible_only: bool = True,
    sort: Literal["rank", "risk_score", "n_reviews", "neg_rate", "avg_stars", "name"] = "rank",
    order: Literal["asc", "desc"] | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> dict[str, Any]:
    items = store.provider_risk()["providers"]
    if eligible_only:
        items = [p for p in items if p["eligible"]]
    if q:
        items = [p for p in items if q.lower() in p["name"].lower()]
    if trade:
        items = [p for p in items if p["trade"] == trade]
    if tier:
        items = [p for p in items if p["risk_tier"] == tier]
    if trend:
        items = [p for p in items if p["trend"]["direction"] == trend]
    if aspect:
        items = [p for p in items if any(i["aspect"] == aspect and i["recurring"] for i in p["issues"])]

    default_desc = sort in {"risk_score", "n_reviews", "neg_rate"}
    desc = (order == "desc") if order else default_desc
    key = (lambda p: p["name"].lower()) if sort == "name" else (lambda p: (p[sort] is None, p[sort]))
    items = sorted(items, key=key, reverse=desc)
    if desc:  # keep providers with a missing value (None) at the end regardless of direction
        items = [p for p in items if p.get(sort) is not None] + [p for p in items if p.get(sort) is None]
    return {"total": len(items), "limit": limit, "offset": offset, "items": [_list_item(p) for p in items[offset : offset + limit]]}


@app.get("/api/providers/{business_id}", tags=["providers"])
def get_provider(business_id: str) -> dict[str, Any]:
    """Full provider profile including recurring issues with evidence sentences, trend, actions and yearly history."""
    provider = store.providers_by_id().get(business_id)
    if provider is None:
        raise HTTPException(status_code=404, detail=f"Unknown provider {business_id!r}")
    return provider


class AnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=3, max_length=config.MAX_ANALYZE_CHARS, examples=["They never called back and charged $600 more than quoted."])


@app.post("/api/analyze", tags=["live demo"])
def analyze(req: AnalyzeRequest) -> dict[str, Any]:
    """Paste a review, get aspect complaint signals with evidence sentences (LITE port of the notebook's Layer 2)."""
    return analyzer.analyze(req.text)
