"""HomeLens AI API (FastAPI) — an HTTP layer over the anonymized artifacts and the review-risk logic.

Run locally:   uvicorn app.main:app --reload --port 8000      (from the backend/ folder)
Docs (auto):   http://localhost:8000/docs
Vercel:        detected automatically — `app` in app/main.py is the entrypoint (see docs/DEPLOYMENT.md).
"""

from __future__ import annotations

from typing import Any, Literal

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from . import artifacts, config, scoring
from .examples import EXAMPLES

app = FastAPI(
    title="HomeLens AI API",
    version="0.2.0",
    description=(
        "Review-based risk signals for home-service providers. Providers are anonymized (`Provider_XXXX`); all outputs are "
        "signals for human investigation, not findings about any business."
    ),
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_origin_regex=r"https://.*\.vercel\.app" if config.CORS_ALLOW_VERCEL_PREVIEWS else None,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.exception_handler(artifacts.ArtifactError)
async def _artifact_missing(_, exc: artifacts.ArtifactError):  # pragma: no cover - only when artifacts are absent
    return JSONResponse(status_code=503, content={"detail": str(exc)})


@app.get("/api/health", tags=["meta"])
def health() -> dict[str, Any]:
    model = scoring.load_model()
    return {"status": "ok", "providers": len(artifacts.providers()), "model": model.name if model else None,
            "model_available": model is not None, "market": artifacts.metadata().get("market")}


@app.get("/api/overview", tags=["portfolio"])
def overview() -> dict[str, Any]:
    """KPI pods (with sparkline series), tier counts, service-group benchmark, model comparison, corpus timeline."""
    return artifacts.overview()


@app.get("/api/aspects", tags=["portfolio"])
def aspects() -> list[dict[str, Any]]:
    """The 8 complaint aspects with corpus statistics, keyword cluster (phrase dictionary) and recommended action."""
    return artifacts.aspects()


@app.get("/api/providers", tags=["providers"])
def list_providers(
    tier: Literal["Stable", "Watch", "Elevated", "High concern"] | None = None,
    service_group: str | None = None,
    aspect: str | None = Query(None, description="top complaint aspect, e.g. 'Reliability / No-show'"),
    trend: Literal["Rising", "Steady", "Improving", "Insufficient data"] | None = None,
    min_reviews: int = Query(20, ge=20),
    q: str | None = Query(None, description="substring of the anonymized provider code"),
    sort: Literal["risk_score", "reviews", "recent_risk", "trend_delta"] = "risk_score",
    limit: int = Query(500, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> dict[str, Any]:
    """Anonymized providers with at least 20 reviews, each with its yearly risk history."""
    items = [p for p in artifacts.providers() if p["reviews"] >= min_reviews]
    if tier:
        items = [p for p in items if p["risk_tier"] == tier]
    if service_group:
        items = [p for p in items if p["service_group"] == service_group]
    if aspect:
        items = [p for p in items if p["top_aspect"] == aspect]
    if trend:
        items = [p for p in items if p["trend"] == trend]
    if q:
        items = [p for p in items if q.lower() in p["code"].lower()]
    items = sorted(items, key=lambda p: (p[sort] is None, -(p[sort] or 0)))
    return {"total": len(items), "limit": limit, "offset": offset, "items": items[offset : offset + limit]}


@app.get("/api/providers/{code}", tags=["providers"])
def get_provider(code: str) -> dict[str, Any]:
    p = artifacts.provider(code)
    if p is None:
        raise HTTPException(status_code=404, detail=f"Unknown provider {code!r}")
    peers = [x for x in artifacts.services() if x["service_group"] == p["service_group"]]
    return {**p, "service_benchmark": peers[0] if peers else None}


@app.get("/api/examples", tags=["review analysis"])
def examples() -> list[dict[str, str]]:
    return EXAMPLES


class AnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=3, max_length=config.MAX_ANALYZE_CHARS, examples=[EXAMPLES[0]["text"]])


@app.post("/api/analyze", tags=["review analysis"])
def analyze(req: AnalyzeRequest) -> dict[str, Any]:
    """Score a review: probability vs threshold, complaint aspects, per-sentence breakdown, evidence sentence, token weights."""
    try:
        return scoring.analyze(req.text)
    except ValueError as err:
        raise HTTPException(status_code=422, detail=str(err)) from err
