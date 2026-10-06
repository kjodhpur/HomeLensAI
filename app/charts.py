"""Plotly figure builders sharing one visual system.

Rules: one hue per single-series chart, status colors only for risk tiers,
recessive grid, thin marks with rounded ends, hover on every mark.
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from app.config import (
    BASELINE,
    GRID,
    INK,
    INK_2,
    MODEL_COLORS,
    MUTED,
    PURPLE,
    TIER_COLORS,
)

FONT = "Inter, 'Segoe UI', system-ui, sans-serif"
PLOTLY_CONFIG = {"displayModeBar": False, "responsive": True}


def _base(fig: go.Figure, height: int, left: int = 8) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=left, r=16, t=8, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT, size=12.5, color=INK_2),
        hoverlabel=dict(bgcolor="#FFFFFF", bordercolor="#E3E6F0", font=dict(family=FONT, size=12.5, color=INK)),
        showlegend=False,
        bargap=0.38,
        transition=dict(duration=600, easing="cubic-in-out"),
    )
    fig.update_xaxes(gridcolor=GRID, zeroline=False, linecolor=BASELINE, tickfont=dict(color=MUTED), title_font=dict(color=MUTED, size=12))
    fig.update_yaxes(gridcolor=GRID, zeroline=False, linecolor=BASELINE, tickfont=dict(color=INK_2), title_font=dict(color=MUTED, size=12))
    return fig


def service_benchmark(summary: pd.DataFrame) -> go.Figure:
    """Median relative provider risk score by service group (horizontal bars)."""
    data = summary.sort_values("median_risk_score")
    fig = go.Figure(
        go.Bar(
            x=data["median_risk_score"],
            y=data["service_group"],
            orientation="h",
            marker=dict(color=PURPLE, cornerradius=4, line=dict(width=0)),
            customdata=data[["eligible_businesses", "high_concern_providers", "median_recent_risk"]],
            text=data["median_risk_score"].map(lambda v: f"{v:.0f}"),
            textposition="outside",
            textfont=dict(color=INK_2, size=12),
            cliponaxis=False,
            hovertemplate=(
                "<b>%{y}</b><br>Median risk score: %{x:.1f}"
                "<br>Monitored providers: %{customdata[0]}"
                "<br>High-concern providers: %{customdata[1]}"
                "<br>Median recent risk: %{customdata[2]:.2f}<extra></extra>"
            ),
        )
    )
    fig.add_vline(x=50, line=dict(color=MUTED, width=1, dash="dot"))
    fig.add_annotation(x=50, y=1.0, yref="paper", yanchor="bottom", text="Watch threshold (50)", showarrow=False,
                       font=dict(size=11, color=MUTED), xanchor="left", xshift=4)
    _base(fig, 380)
    fig.update_layout(margin=dict(l=8, r=16, t=30, b=8))
    fig.update_xaxes(range=[0, 100], title_text="Median relative risk score (0–100)", showgrid=True)
    fig.update_yaxes(showgrid=False, ticksuffix="  ")
    return fig


def aspect_lift(aspects: pd.DataFrame) -> go.Figure:
    """Lift of the negative-review rate when a complaint aspect is mentioned."""
    data = aspects.sort_values("lift_vs_corpus_negative_rate")
    fig = go.Figure(
        go.Bar(
            x=data["lift_vs_corpus_negative_rate"],
            y=data["aspect"],
            orientation="h",
            marker=dict(color=PURPLE, cornerradius=4),
            customdata=data[["reviews_with_signal", "negative_rate_when_mentioned"]],
            text=data["lift_vs_corpus_negative_rate"].map(lambda v: f"{v:.2f}×"),
            textposition="outside",
            textfont=dict(color=INK_2, size=12),
            cliponaxis=False,
            hovertemplate=(
                "<b>%{y}</b><br>Lift: %{x:.2f}× the corpus negative rate"
                "<br>Reviews with signal: %{customdata[0]:,}"
                "<br>Negative when mentioned: %{customdata[1]:.0%}<extra></extra>"
            ),
        )
    )
    fig.add_vline(x=1, line=dict(color=MUTED, width=1, dash="dot"))
    fig.add_annotation(x=1, y=1.0, yref="paper", yanchor="bottom", text="Corpus baseline (1×)", showarrow=False,
                       font=dict(size=11, color=MUTED), xanchor="left", xshift=4)
    _base(fig, 380)
    fig.update_layout(margin=dict(l=8, r=16, t=30, b=8))
    fig.update_xaxes(range=[0, max(3.2, data["lift_vs_corpus_negative_rate"].max() * 1.15)],
                     title_text="Lift over corpus negative-review rate", ticksuffix="×")
    fig.update_yaxes(showgrid=False, ticksuffix="  ")
    return fig


SHORT_MODEL_NAMES = {
    "Fine-tuned DistilBERT": "DistilBERT",
    "TF–IDF Logistic Regression": "TF–IDF",
    "TextBlob": "TextBlob",
}

METRIC_LABELS = {
    "macro_f1": "Macro F1",
    "negative_precision": "Negative precision",
    "negative_recall": "Negative recall",
    "negative_f1": "Negative F1",
    "average_precision": "Average precision",
    "roc_auc": "ROC-AUC",
}


def model_dot_plot(comparison: pd.DataFrame) -> go.Figure:
    """Cleveland dot plot: each metric row shows the three models."""
    metrics = list(METRIC_LABELS)[::-1]
    labels = [METRIC_LABELS[m] for m in metrics]
    fig = go.Figure()
    # Connector per metric (range across models) keeps the eye on the gap.
    for metric, label in zip(metrics, labels, strict=True):
        values = comparison[metric]
        fig.add_trace(go.Scatter(x=[values.min(), values.max()], y=[label, label], mode="lines",
                                 line=dict(color="#E3E6F0", width=6), hoverinfo="skip", showlegend=False))
    for _, row in comparison.iterrows():
        name = row["model"]
        fig.add_trace(
            go.Scatter(
                x=[row[m] for m in metrics],
                y=labels,
                mode="markers",
                name=SHORT_MODEL_NAMES.get(name, name),
                marker=dict(size=15, color=MODEL_COLORS.get(name, MUTED), line=dict(color="#FFFFFF", width=2)),
                hovertemplate=f"<b>{name}</b><br>%{{y}}: %{{x:.3f}}<extra></extra>",
            )
        )
    _base(fig, 380)
    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, font=dict(size=12.5, color=INK_2)),
        margin=dict(l=8, r=16, t=40, b=8),
    )
    fig.update_xaxes(range=[0.58, 1.01], title_text="Held-out test score (higher is better)", dtick=0.05)
    fig.update_yaxes(showgrid=False, ticksuffix="  ")
    return fig


def provider_trend(yearly: pd.DataFrame, threshold_line: float | None = None) -> go.Figure:
    """Yearly mean model risk for one provider (line + markers sized by volume)."""
    fig = go.Figure(
        go.Scatter(
            x=yearly["review_year"],
            y=yearly["mean_risk_probability"],
            mode="lines+markers",
            line=dict(color=PURPLE, width=2.5, shape="spline", smoothing=0.6),
            marker=dict(size=(yearly["reviews"].clip(1, 20) * 0.6 + 7), color=PURPLE, line=dict(color="#fff", width=2)),
            fill="tozeroy",
            fillcolor="rgba(108,71,255,0.08)",
            customdata=yearly[["reviews"]],
            hovertemplate="<b>%{x}</b><br>Mean risk: %{y:.2f}<br>Reviews: %{customdata[0]}<extra></extra>",
        )
    )
    if threshold_line is not None:
        fig.add_hline(y=threshold_line, line=dict(color=MUTED, width=1, dash="dot"))
    _base(fig, 230)
    fig.update_yaxes(range=[0, 1.05], tickformat=".0%", title_text="Mean model risk")
    fig.update_xaxes(dtick=2, showgrid=False)
    return fig


def tier_by_group(providers: pd.DataFrame) -> go.Figure:
    """Stacked horizontal bars: provider tiers within each service group.

    Shown under the tier tiles, which act as the legend (swatch + label).
    """
    table = (
        providers.groupby(["service_group", "risk_tier"], observed=False).size().unstack(fill_value=0)
    )
    table = table.loc[table.sum(axis=1).sort_values().index]
    fig = go.Figure()
    for tier in TIER_COLORS:
        if tier not in table.columns:
            continue
        fig.add_trace(go.Bar(
            y=table.index, x=table[tier], name=tier, orientation="h",
            marker=dict(color=TIER_COLORS[tier], line=dict(color="#FFFFFF", width=2)),
            hovertemplate=f"<b>%{{y}}</b><br>{tier}: %{{x}} providers<extra></extra>",
        ))
    _base(fig, 340)
    # The tier tiles rendered directly above this chart serve as its color legend.
    fig.update_layout(barmode="stack", bargap=0.32)
    fig.update_xaxes(title_text="Monitored providers")
    fig.update_yaxes(showgrid=False, ticksuffix="  ")
    return fig


def corpus_timeline(timeline: pd.DataFrame) -> go.Figure:
    """Reviews per year (single series)."""
    fig = go.Figure(go.Bar(
        x=timeline["review_year"], y=timeline["reviews"],
        marker=dict(color=PURPLE, cornerradius=3),
        customdata=timeline[["negative_rate"]],
        hovertemplate="<b>%{x}</b><br>Reviews: %{y:,}<br>1–2 star share: %{customdata[0]:.0%}<extra></extra>",
    ))
    _base(fig, 250)
    fig.update_layout(bargap=0.25)
    fig.update_yaxes(title_text="Reviews", tickformat=",")
    fig.update_xaxes(dtick=2, showgrid=False)
    return fig
