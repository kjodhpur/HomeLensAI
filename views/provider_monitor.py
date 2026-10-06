"""Provider Monitor: filter anonymized providers and inspect one in detail."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from app import charts
from app.config import TIER_COLORS, TIER_ORDER, TREND_ORDER, TREND_THRESHOLD
from app.data_loader import load_optional, load_providers
from app.ui_components import (
    card_header,
    empty_state,
    esc,
    icon,
    note,
    page_header,
    render_html,
    stat_row,
    tier_badge,
)

TREND_STYLE = {
    "Rising": ("trend_up", "#A82424"),
    "Improving": ("trend_down", "#0A6B0A"),
    "Steady": ("minus", "#4A5272"),
    "Insufficient data": ("minus", "#8A90A8"),
}


def _filters(providers: pd.DataFrame) -> pd.DataFrame:
    with st.container(key="card_filters"):
        card_header("Filters", "Narrow the watchlist. All providers are anonymized.", "filter")
        c1, c2, c3 = st.columns([1.2, 2, 0.9], gap="medium")
        groups = c1.multiselect("Service group", sorted(providers["service_group"].unique()),
                                placeholder="All service groups")
        tiers = c2.pills("Risk tier", TIER_ORDER, selection_mode="multi", default=TIER_ORDER, key="tier_pills")
        max_reviews = int(providers["reviews"].max())
        min_reviews = c3.slider("Minimum reviews", 20, min(max_reviews, 200), 20, step=5)
        c4, c5, c6 = st.columns([1.2, 2, 0.9], gap="medium")
        aspects = c4.multiselect("Top complaint aspect", sorted(providers["top_aspect"].unique()),
                                 placeholder="All aspects")
        trends = c5.pills("Trend direction", TREND_ORDER, selection_mode="multi", default=TREND_ORDER, key="trend_pills")
        sort_by = c6.selectbox("Sort by", ["Risk score", "Reviews", "Recent risk", "Trend change"])

    filtered = providers[providers["reviews"] >= min_reviews]
    if groups:
        filtered = filtered[filtered["service_group"].isin(groups)]
    if aspects:
        filtered = filtered[filtered["top_aspect"].isin(aspects)]
    filtered = filtered[filtered["risk_tier"].isin(tiers or [])]
    filtered = filtered[filtered["trend"].isin(trends or [])]
    sort_column = {"Risk score": "risk_score", "Reviews": "reviews",
                   "Recent risk": "recent_risk_probability", "Trend change": "trend_delta"}[sort_by]
    return filtered.sort_values(sort_column, ascending=False, na_position="last").reset_index(drop=True)


def _detail(row: pd.Series, yearly: pd.DataFrame | None) -> None:
    tier = str(row["risk_tier"])
    trend_icon, trend_color = TREND_STYLE[row["trend"]]
    delta = row["trend_delta"]
    delta_text = "n/a" if pd.isna(delta) else f"{delta:+.2f}"
    render_html(
        f"""<div class="hl-page"><div class="hl-prov-head"><div>
          <div class="hl-kicker">Selected provider</div>
          <div class="hl-prov-code">{esc(row['provider_code'])}</div>
          <div class="hl-prov-group">{esc(row['service_group'])} · {int(row['reviews'])} reviews</div></div>
          {tier_badge(tier)}</div>
          <div class="hl-score"><b>{row['risk_score']:.1f}</b><span>/ 100 relative risk score</span></div>
          <div class="hl-bar"><span style="width:{row['risk_score']:.1f}%;background:{TIER_COLORS[tier]}"></span></div>
          <div class="hl-kv">
            <div><div class="k">1–2 star share</div><div class="v">{row['observed_negative_rate']:.0%}</div></div>
            <div><div class="k">Mean model risk</div><div class="v">{row['mean_risk_probability']:.2f}</div></div>
            <div><div class="k">High-severity rate</div><div class="v">{row['high_severity_rate']:.0%}</div></div>
            <div><div class="k">Recent risk (2021+)</div><div class="v">{row['recent_risk_probability']:.2f}</div></div>
            <div><div class="k">Trend vs 2020</div>
              <div class="v"><span class="hl-trend" style="color:{trend_color}">{icon(trend_icon, 16, 2.2)}{esc(row['trend'])} ({delta_text})</span></div></div>
            <div><div class="k">Top aspect</div><div class="v">{esc(row['top_aspect'])}</div></div>
          </div></div>"""
    )
    if yearly is not None:
        history = yearly[yearly["provider_code"] == row["provider_code"]]
        if len(history) >= 2:
            render_html('<div class="hl-kicker" style="margin:4px 0 0">Yearly mean model risk</div>')
            st.plotly_chart(charts.provider_trend(history), config=charts.PLOTLY_CONFIG, width="stretch",
                            key=f"trend_{row['provider_code']}")
    render_html(
        f"""<div class="hl-action"><span class="ic">{icon('action', 20)}</span><div>
          <div class="k">Operational recommendation</div><div class="v">{esc(row['recommended_action'])}</div></div></div>"""
    )


def render() -> None:
    providers = load_providers()
    yearly = load_optional("provider_yearly_risk.csv")

    page_header(
        "Provider Monitor",
        "Anonymized provider watchlist",
        "Relative concern tiers for providers with at least 20 reviews. Filter, select a provider, "
        "and review the leading complaint signal and recommended action.",
        pills=[("providers", f"{len(providers)} monitored providers"), ("lock", "Provider identities masked"),
               ("clock", "Trend: 2021+ vs 2020")],
    )
    st.write("")
    filtered = _filters(providers)

    rising = int((filtered["trend"] == "Rising").sum())
    attention = int(filtered["risk_tier"].isin(["Elevated", "High concern"]).sum())
    stat_row([
        ("Providers in view", f"{len(filtered)}", f"of {len(providers)} monitored"),
        ("Elevated or High concern", f"{attention}",
         f"{attention / len(filtered):.0%} of the current view" if len(filtered) else "—"),
        ("Rising trend", f"{rising}", f"mean risk up more than {TREND_THRESHOLD:.2f} vs 2020"),
    ])
    st.write("")

    if filtered.empty:
        with st.container(key="card_empty"):
            empty_state("No providers match these filters", "Widen the filters to see providers again.", "filter")
        return

    table_col, detail_col = st.columns([1.45, 1], gap="medium")
    with table_col:
        with st.container(key="card_table"):
            card_header("Watchlist", "Select a row to open the provider detail panel.", "layers")
            view = filtered[[
                "provider_code", "risk_tier", "risk_score", "service_group", "reviews",
                "recent_risk_probability", "trend", "top_aspect",
            ]].copy()
            view["risk_tier"] = view["risk_tier"].astype(str)
            event = st.dataframe(
                view,
                hide_index=True,
                width="stretch",
                height=480,
                on_select="rerun",
                selection_mode="single-row",
                key="provider_table",
                column_config={
                    "provider_code": st.column_config.TextColumn("Provider", width=110),
                    "risk_tier": st.column_config.TextColumn("Tier", width=105),
                    "risk_score": st.column_config.ProgressColumn("Risk score", min_value=0, max_value=100, format="%.0f", width=120),
                    "service_group": st.column_config.TextColumn("Service group", width=210),
                    "reviews": st.column_config.NumberColumn("Reviews", format="%d", width=80),
                    "recent_risk_probability": st.column_config.NumberColumn("Recent risk", format="%.2f"),
                    "trend": st.column_config.TextColumn("Trend"),
                    "top_aspect": st.column_config.TextColumn("Top aspect"),
                },
            )
            export = filtered.drop(columns=["latest_review"], errors="ignore").copy()
            export["risk_tier"] = export["risk_tier"].astype(str)
            st.download_button(
                "Export filtered CSV",
                export.to_csv(index=False).encode("utf-8"),
                file_name="homelens_provider_watchlist.csv",
                mime="text/csv",
                icon=":material/download:",
            )

    selected_rows = event.selection.rows if event and event.selection else []
    selected_rows = [r for r in selected_rows if r < len(filtered)]  # stale after a filter change
    selected = filtered.iloc[selected_rows[0]] if selected_rows else filtered.iloc[0]
    with detail_col:
        with st.container(key="card_detail"):
            _detail(selected, yearly)
            if not selected_rows:
                note("Showing the highest-ranked provider in the current view. Select a row to change it.")
    note("Tiers are relative within this historical Tucson corpus and reflect review-based signals only. "
         "They are a prompt for human investigation, not a finding about any business.", "shield")
