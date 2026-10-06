"""Reusable UI building blocks: global CSS, animated cards, gauge, chips, carousel.

All custom markup is rendered with ``st.html`` (sanitized, no scripts). Motion
is CSS-only and is disabled under ``prefers-reduced-motion``.
"""

from __future__ import annotations

import html
import math
import re
from typing import Iterable, Sequence

import streamlit as st

from app.config import TIER_BG, TIER_COLORS, TIER_ORDER, TIER_RULES, TIER_TEXT

# --------------------------------------------------------------------------
# Icons (inline SVG, 24px grid, stroke-based)
# --------------------------------------------------------------------------
_ICON_PATHS = {
    "reviews": '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/><path d="M8 9h8M8 13h5"/>',
    "providers": '<path d="M3 21h18M5 21V8l7-5 7 5v13"/><path d="M9 21v-6h6v6"/>',
    "target": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.5"/>',
    "radar": '<path d="M12 3a9 9 0 1 0 9 9"/><path d="M12 7a5 5 0 1 0 5 5"/><path d="m12 12 7-7"/>',
    "map": '<path d="M9 4 3 6v14l6-2 6 2 6-2V4l-6 2-6-2z"/><path d="M9 4v14M15 6v14"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "users": '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20a6.5 6.5 0 0 1 13 0"/><path d="M16 4.5a3.5 3.5 0 0 1 0 7M21.5 20a6.5 6.5 0 0 0-4-6"/>',
    "star": '<path d="m12 3 2.8 5.7 6.2.9-4.5 4.4 1 6.2L12 17.3 6.5 20.2l1-6.2L3 9.6l6.2-.9z"/>',
    "alert": '<path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/><path d="M12 9v4M12 17h.01"/>',
    "eye": '<path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
    "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/>',
    "lock": '<rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>',
    "spark": '<path d="M12 3v4M12 17v4M3 12h4M17 12h4M5.6 5.6l2.8 2.8M15.6 15.6l2.8 2.8M5.6 18.4l2.8-2.8M15.6 8.4l2.8-2.8"/>',
    "check": '<path d="m5 12 5 5L20 7"/>',
    "trend_up": '<path d="m3 17 6-6 4 4 8-8"/><path d="M14 7h7v7"/>',
    "trend_down": '<path d="m3 7 6 6 4-4 8 8"/><path d="M14 17h7v-7"/>',
    "minus": '<path d="M5 12h14"/>',
    "action": '<path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>',
    "layers": '<path d="m12 2 10 5-10 5L2 7z"/><path d="m2 17 10 5 10-5M2 12l10 5 10-5"/>',
    "cpu": '<rect x="5" y="5" width="14" height="14" rx="2"/><rect x="9" y="9" width="6" height="6"/><path d="M9 2v3M15 2v3M9 19v3M15 19v3M2 9h3M2 15h3M19 9h3M19 15h3"/>',
    "scale": '<path d="M12 3v18M5 21h14M3 7h18"/><path d="m6 7-3 7a3 3 0 0 0 6 0zM18 7l-3 7a3 3 0 0 0 6 0z"/>',
    "filter": '<path d="M3 4h18l-7 9v6l-4 2v-8z"/>',
    "info": '<circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7.5h.01"/>',
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
}


def icon(name: str, size: int = 20, stroke: float = 1.8) -> str:
    """Return an inline SVG icon."""
    path = _ICON_PATHS.get(name, _ICON_PATHS["info"])
    return (
        f'<svg class="hl-ico" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
        f'stroke="currentColor" stroke-width="{stroke}" stroke-linecap="round" '
        f'stroke-linejoin="round" aria-hidden="true">{path}</svg>'
    )


def render_html(markup: str) -> None:
    """Render trusted, app-generated HTML (including inline SVG).

    ``st.html`` sanitizes away ``<svg>``, so markup goes through
    ``st.markdown``. Whitespace is collapsed so the Markdown parser never
    mistakes indented HTML for a code block. Never pass user text unescaped.
    """
    st.markdown(re.sub(r"\s*\n\s*", " ", markup).strip(), unsafe_allow_html=True)


def fmt_threshold(value: float) -> str:
    """0.585 -> '0.585', 0.95 -> '0.95' (no misleading rounding)."""
    return f"{value:.3f}".rstrip("0").rstrip(".")


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


# --------------------------------------------------------------------------
# Global stylesheet
# --------------------------------------------------------------------------
_CSS = """
<style>
:root {
  --hl-purple: #6C47FF; --hl-purple-2: #5A35F0; --hl-purple-soft: #EFEBFF; --hl-purple-ink: #4B2BD6;
  --hl-navy: #0E1530; --hl-navy-2: #172049; --hl-ink: #141A33; --hl-ink-2: #4A5272; --hl-muted: #6E7591;
  --hl-bg: #F4F5FA; --hl-card: #FFFFFF; --hl-line: #E3E6F0; --hl-line-2: #EEF0F6;
  --hl-good: #0CA30C; --hl-warn: #FAB219; --hl-serious: #EC835A; --hl-crit: #D03B3B;
  --hl-shadow-sm: 0 1px 2px rgba(20,26,51,.05), 0 1px 3px rgba(20,26,51,.06);
  --hl-shadow: 0 1px 2px rgba(20,26,51,.04), 0 8px 24px -6px rgba(20,26,51,.10);
  --hl-shadow-lg: 0 2px 4px rgba(20,26,51,.04), 0 18px 40px -12px rgba(52,30,160,.28);
  --hl-ease: cubic-bezier(.16,1,.3,1);
  --hl-head: 'Plus Jakarta Sans', Inter, 'Segoe UI', system-ui, sans-serif;
}

/* ---------- Canvas ---------- */
[data-testid="stAppViewContainer"] { background:
  radial-gradient(1200px 500px at 85% -10%, rgba(108,71,255,.07), transparent 60%),
  radial-gradient(900px 400px at -10% 0%, rgba(14,21,48,.04), transparent 60%), var(--hl-bg); }
[data-testid="stHeader"] { background: transparent; }
[data-testid="stMainBlockContainer"] { padding-top: 2.2rem; padding-bottom: 4rem; max-width: 1360px; }
h1, h2, h3, h4 { font-family: var(--hl-head); letter-spacing: -.02em; color: var(--hl-ink); }
.hl-ico { flex-shrink: 0; }

/* ---------- Motion: page slide + staggered rise ---------- */
@keyframes hl-page-in { from { opacity: 0; transform: translateX(36px); } to { opacity: 1; transform: none; } }
@keyframes hl-rise { from { opacity: 0; transform: translateY(16px) scale(.985); } to { opacity: 1; transform: none; } }
@keyframes hl-fade { from { opacity: 0; } to { opacity: 1; } }
@keyframes hl-grow-x { from { transform: scaleX(0); } to { transform: scaleX(1); } }
@keyframes hl-pulse { 0% { box-shadow: 0 0 0 0 currentColor; } 70% { box-shadow: 0 0 0 7px transparent; } 100% { box-shadow: 0 0 0 0 transparent; } }
@keyframes hl-shimmer { from { background-position: -200% 0; } to { background-position: 200% 0; } }
@keyframes hl-float { 0%,100% { transform: translate(0,0); } 50% { transform: translate(-18px, 10px); } }
.hl-page { animation: hl-page-in .65s var(--hl-ease) both; }
.hl-rise { animation: hl-rise .7s var(--hl-ease) both; animation-delay: calc(var(--i, 0) * 70ms + 80ms); }
[data-testid="stMainBlockContainer"] [data-testid="stPlotlyChart"],
[data-testid="stMainBlockContainer"] [data-testid="stDataFrame"] { animation: hl-rise .8s var(--hl-ease) .18s both; }
[class*="st-key-card"] { animation: hl-rise .7s var(--hl-ease) both; }

/* ---------- Hero header ---------- */
.hl-hero { position: relative; overflow: hidden; border-radius: 22px; padding: 30px 34px 28px;
  background: linear-gradient(120deg, #0E1530 0%, #1C1F5C 55%, #3B22A8 100%); color: #fff;
  box-shadow: var(--hl-shadow-lg); margin-bottom: 6px; }
.hl-hero::before, .hl-hero::after { content: ""; position: absolute; border-radius: 50%; filter: blur(8px); pointer-events: none; }
.hl-hero::before { width: 420px; height: 420px; right: -120px; top: -220px;
  background: radial-gradient(circle, rgba(143,116,255,.55), transparent 65%); animation: hl-float 12s ease-in-out infinite; }
.hl-hero::after { width: 300px; height: 300px; right: 220px; bottom: -220px;
  background: radial-gradient(circle, rgba(255,209,102,.20), transparent 65%); animation: hl-float 15s ease-in-out infinite reverse; }
.hl-hero-grid { position: absolute; inset: 0; opacity: .12; pointer-events: none;
  background-image: linear-gradient(rgba(255,255,255,.5) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.5) 1px, transparent 1px);
  background-size: 34px 34px; mask-image: linear-gradient(100deg, transparent 35%, #000 100%); -webkit-mask-image: linear-gradient(100deg, transparent 35%, #000 100%); }
.hl-hero > * { position: relative; z-index: 1; }
.hl-eyebrow { display: inline-flex; align-items: center; gap: 8px; font-size: 12px; font-weight: 600; letter-spacing: .12em;
  text-transform: uppercase; color: #C9BDFF; }
.hl-eyebrow .dot { width: 7px; height: 7px; border-radius: 50%; background: #A995FF; color: rgba(169,149,255,.6); animation: hl-pulse 2.4s infinite; }
.hl-hero h1 { color: #fff; font-size: clamp(1.7rem, 2.6vw, 2.35rem); font-weight: 800; margin: 10px 0 8px; padding: 0; line-height: 1.15; }
.hl-hero p.hl-sub { color: #D5D9EE; font-size: 1.02rem; max-width: 760px; margin: 0; line-height: 1.55; }
.hl-pills { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 18px; }
.hl-pill { display: inline-flex; align-items: center; gap: 6px; padding: 6px 12px; border-radius: 999px; font-size: 12.5px; font-weight: 500;
  color: #E9E6FF; background: rgba(255,255,255,.08); border: 1px solid rgba(255,255,255,.14); backdrop-filter: blur(6px); }
.hl-pill .hl-ico { opacity: .8; }

/* ---------- Section titles ---------- */
.hl-section { display: flex; align-items: flex-end; justify-content: space-between; gap: 12px; margin: 26px 0 12px; }
.hl-section h3 { font-size: 1.12rem; font-weight: 700; margin: 0; padding: 0; }
.hl-section p { margin: 3px 0 0; color: var(--hl-muted); font-size: .9rem; }
.hl-kicker { font-size: 11.5px; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; color: var(--hl-purple); }

/* ---------- Metric cards with count-up ---------- */
@property --hl-n { syntax: '<integer>'; initial-value: 0; inherits: true; }
@property --hl-k { syntax: '<integer>'; initial-value: 0; inherits: true; }
@property --hl-r { syntax: '<integer>'; initial-value: 0; inherits: true; }
@counter-style hl-pad3 { system: extends decimal; pad: 3 "0"; }
@keyframes hl-count { from { --hl-n: 0; } }
.hl-count { --hl-n: var(--to); animation: hl-count 1.8s var(--hl-ease) .15s both; font-variant-numeric: tabular-nums; }
.hl-count.int::after { counter-reset: n var(--hl-n); content: counter(n); }
.hl-count.thou { --hl-k: calc(var(--hl-n) / 1000 - 0.5); --hl-r: calc(var(--hl-n) - var(--hl-k) * 1000); }
.hl-count.thou::after { counter-reset: k var(--hl-k) r var(--hl-r); content: counter(k) "," counter(r, hl-pad3); }
.hl-count.dec3::after { counter-reset: n var(--hl-n); content: "0." counter(n, hl-pad3); }
.hl-sr { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; }

.hl-metrics { display: grid; grid-template-columns: repeat(4, minmax(0,1fr)); gap: 16px; margin-top: 18px; }
@media (max-width: 1100px) { .hl-metrics { grid-template-columns: repeat(2, minmax(0,1fr)); } }
@media (max-width: 560px) { .hl-metrics { grid-template-columns: 1fr; } }
.hl-metric { position: relative; background: var(--hl-card); border: 1px solid var(--hl-line); border-radius: 16px; padding: 18px 18px 16px;
  box-shadow: var(--hl-shadow-sm); transition: transform .35s var(--hl-ease), box-shadow .35s var(--hl-ease), border-color .35s; overflow: hidden; }
.hl-metric::before { content: ""; position: absolute; left: 0; right: 0; top: 0; height: 3px; transform-origin: left;
  background: linear-gradient(90deg, var(--hl-purple), #A995FF); animation: hl-grow-x 1s var(--hl-ease) .35s both; }
.hl-metric:hover { transform: translateY(-4px); box-shadow: var(--hl-shadow-lg); border-color: #D6CCFF; }
.hl-metric-top { display: flex; align-items: center; justify-content: space-between; color: var(--hl-muted); font-size: 13px; font-weight: 600; }
.hl-metric-icon { width: 36px; height: 36px; border-radius: 10px; display: grid; place-items: center; background: var(--hl-purple-soft); color: var(--hl-purple); }
.hl-metric-value { font-family: var(--hl-head); font-weight: 800; font-size: 2.05rem; color: var(--hl-ink); margin: 10px 0 2px; letter-spacing: -.03em; line-height: 1.1; }
.hl-metric-cap { color: var(--hl-muted); font-size: 12.5px; }

/* ---------- Generic card ---------- */
.hl-card { background: var(--hl-card); border: 1px solid var(--hl-line); border-radius: 18px; padding: 20px 22px; box-shadow: var(--hl-shadow-sm); }
[class*="st-key-card"] { background: var(--hl-card); border: 1px solid var(--hl-line); border-radius: 18px; padding: 18px 20px 14px;
  box-shadow: var(--hl-shadow-sm); transition: box-shadow .35s var(--hl-ease); }
[class*="st-key-card"]:hover { box-shadow: var(--hl-shadow); }
.hl-card-title { display: flex; align-items: center; gap: 10px; font-family: var(--hl-head); font-weight: 700; font-size: 1rem; color: var(--hl-ink); margin: 0 0 2px; }
.hl-card-sub { color: var(--hl-muted); font-size: 13px; margin: 0 0 10px; }

/* ---------- Tier distribution ---------- */
.hl-seg { display: flex; height: 14px; border-radius: 8px; overflow: hidden; gap: 2px; background: var(--hl-line-2); margin: 14px 0 16px; }
.hl-seg span { display: block; height: 100%; transform-origin: left; animation: hl-grow-x 1.1s var(--hl-ease) both; }
.hl-tiers { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; }
.hl-tier { border-radius: 14px; padding: 12px 12px 10px; border: 1px solid transparent; transition: transform .3s var(--hl-ease); }
.hl-tier:hover { transform: translateY(-3px); }
.hl-tier .lbl { display: flex; align-items: center; gap: 7px; font-size: 12.5px; font-weight: 700; }
.hl-tier .lbl i { width: 9px; height: 9px; border-radius: 3px; display: inline-block; }
.hl-tier .num { font-family: var(--hl-head); font-size: 1.6rem; font-weight: 800; color: var(--hl-ink); margin-top: 4px; line-height: 1.1; }
.hl-tier .rule { font-size: 11.5px; color: var(--hl-muted); }

/* ---------- Badges & chips ---------- */
.hl-badge { display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px; border-radius: 999px; font-size: 12.5px; font-weight: 700; white-space: nowrap; }
.hl-badge i { width: 8px; height: 8px; border-radius: 50%; display: inline-block; }
.hl-chips { display: flex; flex-wrap: wrap; gap: 8px; }
.hl-chip { display: inline-flex; align-items: center; gap: 6px; padding: 6px 12px; border-radius: 10px; font-size: 13px; font-weight: 600;
  background: var(--hl-purple-soft); color: var(--hl-purple-ink); border: 1px solid #DDD3FF; animation: hl-rise .5s var(--hl-ease) both;
  animation-delay: calc(var(--i, 0) * 90ms + 300ms); }
.hl-chip.primary { background: var(--hl-purple); color: #fff; border-color: var(--hl-purple); box-shadow: 0 6px 16px -6px rgba(108,71,255,.6); }
.hl-chip.muted { background: #F1F3F8; color: var(--hl-ink-2); border-color: var(--hl-line); }

/* ---------- Insight carousel ---------- */
.hl-carousel { position: relative; overflow: hidden; border-radius: 18px; background: var(--hl-card); border: 1px solid var(--hl-line); box-shadow: var(--hl-shadow-sm); }
.hl-track { display: flex; width: calc(var(--n) * 100%); }
.hl-slide { width: calc(100% / var(--n)); padding: 22px 26px 40px; display: grid; grid-template-columns: auto 1fr; gap: 18px; align-items: center; }
.hl-slide-num { font-family: var(--hl-head); font-size: 2.6rem; font-weight: 800; letter-spacing: -.04em; line-height: 1;
  background: linear-gradient(135deg, var(--hl-purple), #A995FF); -webkit-background-clip: text; background-clip: text; color: transparent; min-width: 120px; }
.hl-slide h4 { margin: 0 0 4px; padding: 0; font-size: 1.05rem; }
.hl-slide p { margin: 0; color: var(--hl-ink-2); font-size: .93rem; line-height: 1.5; }
.hl-dots { position: absolute; left: 26px; bottom: 16px; display: flex; gap: 6px; }
.hl-dots span { width: 22px; height: 4px; border-radius: 4px; background: var(--hl-line); overflow: hidden; position: relative; }
.hl-dots span::after { content: ""; position: absolute; inset: 0; background: var(--hl-purple); transform-origin: left; transform: scaleX(0); }
.hl-carousel:hover .hl-track, .hl-carousel:hover .hl-dots span::after { animation-play-state: paused; }
.hl-carousel-tag { position: absolute; right: 18px; bottom: 12px; font-size: 11.5px; color: var(--hl-muted); }

/* ---------- Pipeline flow ---------- */
.hl-flow { display: grid; grid-template-columns: repeat(var(--n), minmax(0,1fr)); gap: 10px; }
@media (max-width: 900px) { .hl-flow { grid-template-columns: repeat(2, minmax(0,1fr)); } }
.hl-step { position: relative; background: var(--hl-card); border: 1px solid var(--hl-line); border-radius: 14px; padding: 14px 14px 12px; box-shadow: var(--hl-shadow-sm); }
.hl-step .n { font-size: 11px; font-weight: 800; color: var(--hl-purple); letter-spacing: .08em; }
.hl-step .t { font-weight: 700; font-size: 13.5px; color: var(--hl-ink); margin-top: 6px; }
.hl-step .d { font-size: 12px; color: var(--hl-muted); margin-top: 3px; line-height: 1.4; }
.hl-step .ic { width: 32px; height: 32px; border-radius: 9px; display: grid; place-items: center; background: var(--hl-purple-soft); color: var(--hl-purple); }
.hl-step-head { display: flex; align-items: center; justify-content: space-between; }

/* ---------- Analyzer ---------- */
.hl-result-head { display: flex; align-items: center; justify-content: space-between; gap: 10px; flex-wrap: wrap; }
.hl-gauge-wrap { display: grid; place-items: center; position: relative; margin: 26px auto 0; max-width: 300px; }
.hl-gauge-wrap svg { width: 100%; height: auto; overflow: visible; }
@keyframes hl-gauge { from { stroke-dashoffset: 100; } }
.hl-gauge-arc { animation: hl-gauge 1.4s var(--hl-ease) .1s both; }
.hl-gauge-center { position: absolute; left: 0; right: 0; bottom: 30px; text-align: center; }
.hl-gauge-val { font-family: var(--hl-head); font-size: 2.6rem; font-weight: 800; color: var(--hl-ink); letter-spacing: -.04em; line-height: 1; }
.hl-gauge-val small { font-size: 1.2rem; font-weight: 700; color: var(--hl-ink-2); }
.hl-gauge-cap { font-size: 12px; color: var(--hl-muted); text-align: center; margin-top: -2px; }
.hl-decision { display: flex; align-items: center; gap: 14px; border-radius: 14px; padding: 14px 16px; margin: 14px 0 6px; animation: hl-rise .6s var(--hl-ease) .25s both; }
.hl-decision .ic { width: 40px; height: 40px; border-radius: 12px; display: grid; place-items: center; color: #fff; }
.hl-decision .t { font-family: var(--hl-head); font-weight: 800; font-size: 1.05rem; }
.hl-decision .d { font-size: 12.5px; color: var(--hl-ink-2); }
.hl-kv { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin: 12px 0; }
.hl-kv > div { background: #F7F8FC; border: 1px solid var(--hl-line-2); border-radius: 12px; padding: 10px 12px; }
.hl-kv .k { font-size: 11.5px; color: var(--hl-muted); font-weight: 600; text-transform: uppercase; letter-spacing: .06em; }
.hl-kv .v { font-weight: 700; color: var(--hl-ink); font-size: 14.5px; margin-top: 2px; }
.hl-action { display: flex; gap: 12px; border-radius: 14px; padding: 14px 16px; margin-top: 12px;
  background: linear-gradient(135deg, #F3EFFF, #FBFAFF); border: 1px solid #DDD3FF; animation: hl-rise .6s var(--hl-ease) .45s both; }
.hl-action .ic { color: var(--hl-purple); margin-top: 1px; }
.hl-action .k { font-size: 11.5px; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; color: var(--hl-purple); }
.hl-action .v { color: var(--hl-ink); font-weight: 600; font-size: 14.5px; margin-top: 2px; line-height: 1.45; }
.hl-note { display: flex; gap: 10px; align-items: flex-start; font-size: 12.5px; color: var(--hl-ink-2); background: #F7F8FC;
  border: 1px dashed #D5D9E8; border-radius: 12px; padding: 10px 12px; margin-top: 12px; line-height: 1.45; }
.hl-note .hl-ico { color: var(--hl-muted); margin-top: 1px; }
.hl-quote { font-size: 14px; line-height: 1.65; color: var(--hl-ink-2); background: #FAFBFE; border-left: 3px solid var(--hl-purple);
  border-radius: 0 12px 12px 0; padding: 12px 16px; margin-top: 10px; }
.hl-quote mark { background: linear-gradient(transparent 55%, rgba(108,71,255,.22) 55%); color: var(--hl-ink); font-weight: 600; padding: 0 1px; }
.hl-empty { text-align: center; padding: 46px 20px; color: var(--hl-muted); }
.hl-empty .ring { width: 74px; height: 74px; border-radius: 22px; margin: 0 auto 14px; display: grid; place-items: center;
  background: var(--hl-purple-soft); color: var(--hl-purple); animation: hl-float 6s ease-in-out infinite; }
.hl-empty h4 { color: var(--hl-ink); margin: 0 0 4px; padding: 0; font-size: 1.05rem; }
.hl-model-pill { display: inline-flex; align-items: center; gap: 7px; font-size: 12px; font-weight: 600; color: var(--hl-ink-2);
  background: #F3F4F9; border: 1px solid var(--hl-line); border-radius: 999px; padding: 4px 10px; }
.hl-model-pill i { width: 7px; height: 7px; border-radius: 50%; display: inline-block; }

/* ---------- Provider detail ---------- */
.hl-prov-head { display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-wrap: wrap; }
.hl-prov-code { font-family: var(--hl-head); font-size: 1.35rem; font-weight: 800; color: var(--hl-ink); letter-spacing: -.02em; }
.hl-prov-group { color: var(--hl-muted); font-size: 13px; }
.hl-score { display: flex; align-items: baseline; gap: 6px; margin: 12px 0 4px; }
.hl-score b { font-family: var(--hl-head); font-size: 2.4rem; font-weight: 800; letter-spacing: -.04em; color: var(--hl-ink); line-height: 1; }
.hl-score span { color: var(--hl-muted); font-size: 13px; }
.hl-bar { height: 8px; border-radius: 6px; background: var(--hl-line-2); overflow: hidden; }
.hl-bar span { display: block; height: 100%; border-radius: 6px; transform-origin: left; animation: hl-grow-x 1s var(--hl-ease) .1s both; }
.hl-trend { display: inline-flex; align-items: center; gap: 5px; font-weight: 700; font-size: 13px; }

/* ---------- Info cards (Responsible AI) ---------- */
.hl-grid { display: grid; grid-template-columns: repeat(var(--cols, 3), minmax(0,1fr)); gap: 14px; }
@media (max-width: 1000px) { .hl-grid { grid-template-columns: repeat(2, minmax(0,1fr)); } }
@media (max-width: 620px) { .hl-grid { grid-template-columns: 1fr; } }
.hl-info { background: var(--hl-card); border: 1px solid var(--hl-line); border-radius: 16px; padding: 18px; box-shadow: var(--hl-shadow-sm);
  transition: transform .35s var(--hl-ease), box-shadow .35s var(--hl-ease), border-color .35s; }
.hl-info:hover { transform: translateY(-4px); box-shadow: var(--hl-shadow); border-color: #D6CCFF; }
.hl-info .ic { width: 38px; height: 38px; border-radius: 11px; display: grid; place-items: center; background: var(--hl-purple-soft); color: var(--hl-purple); margin-bottom: 12px; }
.hl-info h4 { font-size: .98rem; margin: 0 0 4px; padding: 0; }
.hl-info p { margin: 0; color: var(--hl-ink-2); font-size: 13.5px; line-height: 1.5; }
.hl-info .tag { display: inline-block; margin-top: 10px; font-size: 11.5px; font-weight: 700; color: var(--hl-purple); background: var(--hl-purple-soft); padding: 3px 8px; border-radius: 6px; }
.hl-list { margin: 0; padding: 0; list-style: none; }
.hl-list li { display: flex; gap: 10px; align-items: flex-start; padding: 9px 0; border-bottom: 1px solid var(--hl-line-2); font-size: 14px; color: var(--hl-ink-2); line-height: 1.45; }
.hl-list li:last-child { border-bottom: 0; }
.hl-list .yes { color: var(--hl-good); } .hl-list .no { color: var(--hl-crit); }
.hl-stat-row { display: grid; grid-template-columns: repeat(3, minmax(0,1fr)); gap: 12px; }
@media (max-width: 800px) { .hl-stat-row { grid-template-columns: 1fr; } }
.hl-stat { background: var(--hl-card); border: 1px solid var(--hl-line); border-radius: 16px; padding: 16px 18px; box-shadow: var(--hl-shadow-sm); }
.hl-stat .k { font-size: 12.5px; color: var(--hl-muted); font-weight: 600; }
.hl-stat .v { font-family: var(--hl-head); font-size: 1.7rem; font-weight: 800; color: var(--hl-ink); letter-spacing: -.03em; margin-top: 2px; }
.hl-stat .d { font-size: 12.5px; color: var(--hl-ink-2); margin-top: 2px; }
.hl-up { color: #0A7A0A; font-weight: 700; }

/* ---------- Buttons ---------- */
.stButton > button, .stDownloadButton > button, [data-testid="stFormSubmitButton"] > button {
  border-radius: 12px; font-weight: 600; letter-spacing: .005em; min-height: 42px; padding: 0 18px;
  transition: transform .18s var(--hl-ease), box-shadow .25s var(--hl-ease), background .25s, border-color .25s, color .25s; }
button[data-testid="stBaseButton-primary"] { position: relative; overflow: hidden; border: 0;
  background: linear-gradient(135deg, #7B5BFF 0%, #6C47FF 45%, #5A35F0 100%); background-size: 160% 160%;
  box-shadow: 0 1px 0 rgba(255,255,255,.25) inset, 0 8px 20px -8px rgba(108,71,255,.75); color: #fff; }
button[data-testid="stBaseButton-primary"]::after { content: ""; position: absolute; inset: 0; pointer-events: none;
  background: linear-gradient(110deg, transparent 30%, rgba(255,255,255,.35) 50%, transparent 70%); background-size: 200% 100%; opacity: 0; transition: opacity .3s; }
button[data-testid="stBaseButton-primary"]:hover { transform: translateY(-2px); background-position: 100% 50%;
  box-shadow: 0 1px 0 rgba(255,255,255,.25) inset, 0 14px 28px -10px rgba(108,71,255,.85); color: #fff; }
button[data-testid="stBaseButton-primary"]:hover::after { opacity: 1; animation: hl-shimmer 1.2s linear; }
button[data-testid="stBaseButton-primary"]:active { transform: translateY(0) scale(.98); }
button[data-testid="stBaseButton-secondary"] { background: #fff; border: 1px solid var(--hl-line); color: var(--hl-ink); box-shadow: var(--hl-shadow-sm); }
button[data-testid="stBaseButton-secondary"]:hover { border-color: var(--hl-purple); color: var(--hl-purple-ink); background: #FBFAFF;
  transform: translateY(-2px); box-shadow: 0 8px 18px -10px rgba(108,71,255,.55); }
button[data-testid="stBaseButton-secondary"]:active { transform: scale(.98); }
button[data-testid="stBaseButton-tertiary"] { color: var(--hl-muted); }
button[data-testid="stBaseButton-tertiary"]:hover { color: var(--hl-purple); }
.stButton > button:focus-visible, .stDownloadButton > button:focus-visible { outline: 3px solid rgba(108,71,255,.35); outline-offset: 2px; }
/* Preset example buttons: compact chips */
[class*="st-key-preset"] button { min-height: 36px; border-radius: 999px; font-size: 13px; padding: 0 14px; }
[class*="st-key-preset_neg"] button { border-color: #F3D3C7; }
[class*="st-key-preset_pos"] button { border-color: #CDEBCF; }

/* ---------- Inputs ---------- */
[data-testid="stTextArea"] textarea { font-size: 15px; line-height: 1.6; border-radius: 14px; }
[data-testid="stTextArea"] textarea:focus { box-shadow: 0 0 0 4px rgba(108,71,255,.14); }
[data-testid="stWidgetLabel"] p { font-weight: 600; color: var(--hl-ink-2); font-size: 13px; }

/* ---------- Tabs ---------- */
[data-baseweb="tab-list"] { gap: 6px; border-bottom: 1px solid var(--hl-line); }
[data-baseweb="tab"] { border-radius: 10px 10px 0 0; padding: 8px 14px; font-weight: 600; transition: color .2s, background .2s; }
[data-baseweb="tab"]:hover { background: var(--hl-purple-soft); }
[data-baseweb="tab-highlight"] { background: var(--hl-purple); height: 3px; border-radius: 3px; transition: transform .45s var(--hl-ease), width .45s var(--hl-ease); }
[data-baseweb="tab-panel"] { animation: hl-page-in .5s var(--hl-ease) both; }

/* ---------- Sidebar ---------- */
[data-testid="stSidebar"] { background: linear-gradient(185deg, #0E1530 0%, #111A3D 55%, #17154A 100%); border-right: 1px solid #1F2A55; }
[data-testid="stSidebar"] * { color: #C9CFE6; }
[data-testid="stSidebarNav"] { padding-top: 6px; }
[data-testid="stSidebarNavLink"] { border-radius: 10px; margin: 2px 0; padding: 8px 12px; transition: background .25s, transform .25s var(--hl-ease); }
[data-testid="stSidebarNavLink"]:hover { background: rgba(255,255,255,.06); transform: translateX(3px); }
[data-testid="stSidebarNavLink"][aria-current="page"] { background: linear-gradient(90deg, rgba(108,71,255,.38), rgba(108,71,255,.10));
  box-shadow: inset 3px 0 0 #A995FF; }
[data-testid="stSidebarNavLink"][aria-current="page"] * { color: #FFFFFF !important; font-weight: 700; }
[data-testid="stSidebarNavSeparator"] { border-color: #253058; }
[data-testid="stLogo"] { height: 2.4rem; max-width: 100%; }
.hl-side-card { border-radius: 14px; padding: 12px 14px; background: rgba(255,255,255,.04); border: 1px solid rgba(255,255,255,.08); margin-bottom: 10px; }
.hl-side-k { font-size: 10.5px; letter-spacing: .14em; text-transform: uppercase; font-weight: 700; color: #8D96C2 !important; margin-bottom: 8px; }
.hl-side-status { display: flex; align-items: center; gap: 9px; font-weight: 700; color: #FFFFFF !important; font-size: 13.5px; }
.hl-side-status i { width: 9px; height: 9px; border-radius: 50%; display: inline-block; animation: hl-pulse 2.2s infinite; }
.hl-side-sub { font-size: 12px; color: #9AA3CC !important; margin-top: 4px; }
.hl-side-row { display: flex; justify-content: space-between; font-size: 12.5px; padding: 4px 0; }
.hl-side-row b { color: #FFFFFF !important; font-weight: 700; }
[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"] { border-radius: 10px; border: 1px solid rgba(169,149,255,.35); background: rgba(108,71,255,.12); }
[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"]:hover { background: rgba(108,71,255,.25); }

/* ---------- Data table & misc ---------- */
[data-testid="stDataFrame"] { border-radius: 14px; overflow: hidden; border: 1px solid var(--hl-line); }
[data-testid="stExpander"] details { border-radius: 14px; border-color: var(--hl-line); background: #fff; }
[data-testid="stAlert"] { border-radius: 14px; }
hr { border-color: var(--hl-line); }

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation: none !important; transition: none !important; }
  .hl-track { width: auto !important; flex-direction: column; }
  .hl-slide { width: auto !important; }
  .hl-dots { display: none; }
}
</style>
"""


def inject_css() -> None:
    """Inject the global design system. Call once per run.

    ``st.markdown`` is used because style-only ``st.html`` calls are routed to
    an event container that ``st.navigation`` clears on page changes.
    """
    st.markdown(_CSS, unsafe_allow_html=True)


# --------------------------------------------------------------------------
# Page-level blocks
# --------------------------------------------------------------------------
def page_header(eyebrow: str, title: str, subtitle: str, pills: Sequence[tuple[str, str]] = ()) -> None:
    """Hero banner. ``pills`` is a list of (icon, label)."""
    pill_html = "".join(f'<span class="hl-pill">{icon(i, 14)}{esc(t)}</span>' for i, t in pills)
    render_html(
        f"""<div class="hl-page"><section class="hl-hero"><div class="hl-hero-grid"></div>
        <div class="hl-eyebrow"><span class="dot"></span>{esc(eyebrow)}</div>
        <h1>{esc(title)}</h1><p class="hl-sub">{esc(subtitle)}</p>
        <div class="hl-pills">{pill_html}</div></section></div>"""
    )


def section_title(title: str, subtitle: str = "", kicker: str = "") -> None:
    kick = f'<div class="hl-kicker">{esc(kicker)}</div>' if kicker else ""
    sub = f"<p>{esc(subtitle)}</p>" if subtitle else ""
    render_html(f'<div class="hl-section hl-rise"><div>{kick}<h3>{esc(title)}</h3>{sub}</div></div>')


def card_header(title: str, subtitle: str = "", icon_name: str | None = None) -> None:
    ic = f'<span class="hl-metric-icon" style="width:30px;height:30px">{icon(icon_name, 16)}</span>' if icon_name else ""
    sub = f'<p class="hl-card-sub">{esc(subtitle)}</p>' if subtitle else ""
    render_html(f'<div class="hl-card-title">{ic}{esc(title)}</div>{sub}')


def _count_span(value: float, kind: str) -> str:
    """Animated number. kind: 'thou' (>= 1,000 integer), 'int', or 'dec3' (0.xxx)."""
    if kind == "dec3":
        target, text = int(round(value * 1000)), f"{value:.3f}"
    else:
        target = int(round(value))
        kind = "thou" if target >= 1000 else "int"
        text = f"{target:,}"
    return (
        f'<span class="hl-sr">{text}</span>'
        f'<span class="hl-count {kind}" style="--to:{target}" aria-hidden="true"></span>'
    )


def metric_cards(items: Iterable[dict]) -> None:
    """Row of animated KPI cards. Each item: label, value, kind, caption, icon."""
    cards = []
    for index, item in enumerate(items):
        cards.append(
            f"""<div class="hl-metric hl-rise" style="--i:{index}">
              <div class="hl-metric-top"><span>{esc(item['label'])}</span>
              <span class="hl-metric-icon">{icon(item.get('icon', 'spark'), 18)}</span></div>
              <div class="hl-metric-value">{_count_span(item['value'], item.get('kind', 'int'))}</div>
              <div class="hl-metric-cap">{esc(item.get('caption', ''))}</div></div>"""
        )
    render_html(f'<div class="hl-metrics">{"".join(cards)}</div>')


def stat_row(items: Iterable[tuple[str, str, str]]) -> None:
    """Compact stat tiles: (label, value, detail-html)."""
    tiles = "".join(
        f'<div class="hl-stat hl-rise" style="--i:{i}"><div class="k">{esc(k)}</div>'
        f'<div class="v">{esc(v)}</div><div class="d">{d}</div></div>'
        for i, (k, v, d) in enumerate(items)
    )
    render_html(f'<div class="hl-stat-row">{tiles}</div>')


def tier_badge(tier: str) -> str:
    color, bg, txt = TIER_COLORS.get(tier, "#999"), TIER_BG.get(tier, "#eee"), TIER_TEXT.get(tier, "#333")
    return f'<span class="hl-badge" style="background:{bg};color:{txt}"><i style="background:{color}"></i>{esc(tier)}</span>'


def tier_distribution(counts: dict[str, int]) -> None:
    """Segmented bar plus four tier tiles (count, share, rule)."""
    total = max(sum(counts.values()), 1)
    segs, tiles = [], []
    for index, tier in enumerate(TIER_ORDER):
        n = int(counts.get(tier, 0))
        share = n / total
        segs.append(
            f'<span title="{esc(tier)}: {n}" style="width:{share * 100:.2f}%;background:{TIER_COLORS[tier]};'
            f'animation-delay:{index * 120 + 200}ms"></span>'
        )
        tiles.append(
            f"""<div class="hl-tier hl-rise" style="--i:{index};background:{TIER_BG[tier]}">
              <div class="lbl" style="color:{TIER_TEXT[tier]}"><i style="background:{TIER_COLORS[tier]}"></i>{esc(tier)}</div>
              <div class="num">{_count_span(n, 'int')}</div>
              <div class="rule">{share:.0%} of monitored · {esc(TIER_RULES[tier])}</div></div>"""
        )
    render_html(f'<div class="hl-seg">{"".join(segs)}</div><div class="hl-tiers">{"".join(tiles)}</div>')


def insight_carousel(slides: Sequence[tuple[str, str, str]], seconds: float = 5.0) -> None:
    """Auto-advancing slide carousel (CSS only; pauses on hover).

    ``slides``: (big number, headline, body).
    """
    n = len(slides)
    if n == 0:
        return
    cycle = seconds * n
    move = 100 / n  # percent of the cycle per slide
    panels = n + 1  # a clone of the first slide makes the loop seamless
    frames = []
    for i in range(n):
        start, hold_end = i * move, (i + 1) * move - move * 0.14
        frames.append(f"{start:.3f}%, {hold_end:.3f}% {{ transform: translateX({-i * 100 / panels:.4f}%); }}")
    frames.append(f"100% {{ transform: translateX({-n * 100 / panels:.4f}%); }}")
    dot_on, dot_off = move * 0.86, move
    css = (
        f"<style>@keyframes hl-slides {{ {' '.join(frames)} }}"
        f"@keyframes hl-dot {{ 0% {{ transform: scaleX(0); }} {dot_on:.3f}% {{ transform: scaleX(1); }}"
        f" {dot_off:.3f}% {{ transform: scaleX(0); }} 100% {{ transform: scaleX(0); }} }}"
        f".hl-track {{ animation: hl-slides {cycle:.1f}s cubic-bezier(.77,0,.18,1) infinite; }}"
        f".hl-dots span::after {{ animation: hl-dot {cycle:.1f}s linear infinite; }}</style>"
    )
    slide_html = "".join(
        f'<div class="hl-slide"><div class="hl-slide-num">{esc(big)}</div>'
        f"<div><h4>{esc(head)}</h4><p>{esc(body)}</p></div></div>"
        for big, head, body in [*slides, slides[0]]
    )
    dots = "".join(f'<span style="--d:{i}"></span>' for i in range(n))
    dot_delays = "".join(
        f".hl-dots span:nth-child({i + 1})::after {{ animation-delay: {i * seconds:.2f}s; }}" for i in range(n)
    )
    st.markdown(f"{css}<style>{dot_delays}</style>", unsafe_allow_html=True)
    render_html(
        f'<div class="hl-carousel hl-rise" style="--n:{n}" aria-roledescription="carousel">'
        f'<div class="hl-track" style="--n:{panels}">{slide_html}</div>'
        f'<div class="hl-dots">{dots}</div><div class="hl-carousel-tag">Hover to pause</div></div>'
    )


def pipeline_flow(steps: Sequence[tuple[str, str, str]]) -> None:
    """Numbered process steps: (icon, title, description)."""
    items = "".join(
        f"""<div class="hl-step hl-rise" style="--i:{i}"><div class="hl-step-head">
          <span class="ic">{icon(ic, 17)}</span><span class="n">STEP {i + 1:02d}</span></div>
          <div class="t">{esc(t)}</div><div class="d">{esc(d)}</div></div>"""
        for i, (ic, t, d) in enumerate(steps)
    )
    render_html(f'<div class="hl-flow" style="--n:{len(steps)}">{items}</div>')


def info_cards(cards: Sequence[dict], cols: int = 3) -> None:
    """Grid of icon cards: icon, title, body, optional tag."""
    items = "".join(
        f"""<div class="hl-info hl-rise" style="--i:{i}"><div class="ic">{icon(c['icon'], 19)}</div>
          <h4>{esc(c['title'])}</h4><p>{esc(c['body'])}</p>
          {f'<span class="tag">{esc(c["tag"])}</span>' if c.get('tag') else ''}</div>"""
        for i, c in enumerate(cards)
    )
    render_html(f'<div class="hl-grid" style="--cols:{cols}">{items}</div>')


def note(text: str, icon_name: str = "info") -> None:
    render_html(f'<div class="hl-note">{icon(icon_name, 16)}<span>{esc(text)}</span></div>')


# --------------------------------------------------------------------------
# Review analyzer components
# --------------------------------------------------------------------------
def _gauge_color(probability: float, threshold: float) -> str:
    if probability >= threshold:
        return TIER_COLORS["High concern"]
    if probability >= 0.5:
        return TIER_COLORS["Watch"]
    return TIER_COLORS["Stable"]


def risk_gauge(probability: float, threshold: float) -> str:
    """Animated semicircle gauge with a threshold marker."""
    p = min(max(probability, 0.0), 1.0)
    color = _gauge_color(p, threshold)
    cx, cy, r = 120, 116, 96

    def point(t: float, radius: float) -> tuple[float, float]:
        angle = math.pi * (1 - t)
        return cx + radius * math.cos(angle), cy - radius * math.sin(angle)

    x1, y1 = point(threshold, r - 16)
    x2, y2 = point(threshold, r + 14)
    lx, ly = point(threshold, r + 26)
    arc = f"M{cx - r} {cy} A{r} {r} 0 0 1 {cx + r} {cy}"
    ticks = "".join(
        f'<line x1="{point(t, r - 22)[0]:.1f}" y1="{point(t, r - 22)[1]:.1f}" '
        f'x2="{point(t, r - 18)[0]:.1f}" y2="{point(t, r - 18)[1]:.1f}" stroke="#C9CDDC" stroke-width="1.5"/>'
        for t in (0, .25, .5, .75, 1)
    )
    pct = p * 100
    shown = f"{pct:.1f}" if 0 < pct < 1 or 99 < pct < 100 else f"{pct:.0f}"
    return f"""
    <div class="hl-gauge-wrap">
      <svg viewBox="0 0 240 140" role="img" aria-label="Risk probability {shown} percent; threshold {threshold:.0%}">
        <defs><linearGradient id="hlg" x1="0" x2="1"><stop offset="0" stop-color="{color}" stop-opacity=".55"/>
          <stop offset="1" stop-color="{color}"/></linearGradient></defs>
        <path d="{arc}" fill="none" stroke="#EEF0F6" stroke-width="18" stroke-linecap="round"/>
        {ticks}
        <path class="hl-gauge-arc" d="{arc}" fill="none" stroke="url(#hlg)" stroke-width="18" stroke-linecap="round"
          pathLength="100" stroke-dasharray="100" style="stroke-dashoffset:{100 - pct:.2f}"/>
        <line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#141A33" stroke-width="2.5" stroke-linecap="round"/>
        <text x="{lx:.1f}" y="{ly:.1f}" text-anchor="middle" font-size="10" font-weight="700" fill="#4A5272">{fmt_threshold(threshold)}</text>
        <text x="{cx - r}" y="{cy + 18}" text-anchor="middle" font-size="10" fill="#8A90A8">0%</text>
        <text x="{cx + r}" y="{cy + 18}" text-anchor="middle" font-size="10" fill="#8A90A8">100%</text>
      </svg>
      <div class="hl-gauge-center"><div class="hl-gauge-val">{shown}<small>%</small></div></div>
    </div><div class="hl-gauge-cap">Risk probability · marker shows the {fmt_threshold(threshold)} threshold</div>"""


def decision_block(attention: bool) -> str:
    if attention:
        bg, ic_bg, title, desc, ic = "#FBE6E6", TIER_COLORS["High concern"], "Management attention", \
            "Above the operating threshold. Route to a manager for human investigation.", "alert"
        color = "#A82424"
    else:
        bg, ic_bg, title, desc, ic = "#E6F6E6", TIER_COLORS["Stable"], "Routine monitoring", \
            "Below the operating threshold. No escalation required.", "check"
        color = "#0A6B0A"
    return (
        f'<div class="hl-decision" style="background:{bg}"><span class="ic" style="background:{ic_bg}">{icon(ic, 20, 2.2)}</span>'
        f'<div><div class="t" style="color:{color}">{title}</div><div class="d">{desc}</div></div></div>'
    )


def chips(items: Sequence[str], primary: str | None = None, empty: str = "No complaint phrases detected") -> str:
    if not items:
        return f'<div class="hl-chips"><span class="hl-chip muted">{esc(empty)}</span></div>'
    out = "".join(
        f'<span class="hl-chip {"primary" if item == primary else ""}" style="--i:{i}">{esc(item)}</span>'
        for i, item in enumerate(items)
    )
    return f'<div class="hl-chips">{out}</div>'


def highlighted_review(text: str, phrases: dict[str, list[str]], limit: int = 900) -> str:
    """Escape the review and highlight matched complaint phrases."""
    body = text if len(text) <= limit else text[:limit].rsplit(" ", 1)[0] + "…"
    safe = html.escape(body, quote=False)
    all_phrases = sorted({p for hits in phrases.values() for p in hits}, key=len, reverse=True)
    if all_phrases:
        pattern = re.compile("|".join(re.escape(html.escape(p, quote=False)) for p in all_phrases), re.IGNORECASE)
        safe = pattern.sub(lambda m: f"<mark>{m.group(0)}</mark>", safe)
    return f'<div class="hl-quote">{safe}</div>'


def model_pill(name: str, primary: bool) -> str:
    color = TIER_COLORS["Stable"] if primary else TIER_COLORS["Watch"]
    return f'<span class="hl-model-pill"><i style="background:{color}"></i>{esc(name)}</span>'


def empty_state(title: str, body: str, icon_name: str = "radar") -> None:
    render_html(
        f'<div class="hl-empty"><div class="ring">{icon(icon_name, 32, 1.6)}</div>'
        f"<h4>{esc(title)}</h4><div>{esc(body)}</div></div>"
    )
