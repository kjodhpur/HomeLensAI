"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { fmtPct, shortAspect, TIER_VAR, TIERS } from "@/lib/format";
import { spawnRipple } from "@/lib/ripple";
import type { Overview, Provider, Tier } from "@/lib/types";
import { Glass } from "./Glass";
import { TrajectoryChart } from "./TrajectoryChart";

type SortKey = "risk_score" | "recent_risk" | "trend_delta";
const SORTS: { key: SortKey; label: string }[] = [
  { key: "risk_score", label: "Risk score" },
  { key: "recent_risk", label: "Recent risk" },
  { key: "trend_delta", label: "Risk spike" },
];

function RowSpark({ p }: { p: Provider }) {
  const h = p.history;
  if (h.length < 2) return <span className="rowspark-empty">—</span>;
  const x0 = h[0].year;
  const x1 = h[h.length - 1].year;
  const pts = h.map((q) => [2 + ((q.year - x0) / (x1 - x0 || 1)) * 60, 20 - q.risk * 18] as const);
  const last = pts[pts.length - 1];
  return (
    <svg className="rowspark" viewBox="0 0 64 22" width="64" height="22" aria-hidden="true">
      <polyline points={pts.map(([x, y]) => `${x},${y}`).join(" ")} fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" opacity="0.9" />
      <circle cx={last[0]} cy={last[1]} r="2.4" fill="currentColor" />
    </svg>
  );
}

function TrendCell({ p }: { p: Provider }) {
  if (p.trend_delta == null) return <span className="trend na">n/a</span>;
  const arrow = p.trend === "Rising" ? "▲" : p.trend === "Improving" ? "▼" : "●";
  return (
    <span className={`trend ${p.trend.toLowerCase()}`} title={`Mean model risk, 2021+ vs 2020: ${p.trend_delta >= 0 ? "+" : ""}${p.trend_delta.toFixed(2)}`}>
      {arrow} {p.trend_delta >= 0 ? "+" : "−"}
      {Math.abs(p.trend_delta).toFixed(2)}
    </span>
  );
}

interface RowProps {
  p: Provider;
  rank: number;
  open: boolean;
  onToggle: () => void;
  groupMedian: number | null;
  groupScore: number | null;
}

function Row({ p, rank, open, onToggle, groupMedian, groupScore }: RowProps) {
  const host = useRef<HTMLLIElement>(null);
  const fx = useRef<HTMLDivElement>(null);
  const spike = p.trend_delta != null ? Math.min(1, Math.max(0, p.trend_delta / 0.3)) : 0;

  useEffect(() => {
    if (open) host.current?.scrollIntoView({ block: "nearest", behavior: "smooth" });
  }, [open]);

  return (
    <li ref={host} className="lb-row" data-open={open} data-tier={p.risk_tier} data-spike={spike > 0.2 ? "1" : "0"} style={{ ["--score" as string]: p.risk_score, ["--spike" as string]: spike, ["--c" as string]: TIER_VAR[p.risk_tier] }}>
      <div className="row-fx" ref={fx} aria-hidden="true" />
      <div
        className="lb-head"
        role="button"
        tabIndex={0}
        aria-expanded={open}
        onPointerDown={(e) => spawnRipple(fx.current, host.current, e)}
        onClick={onToggle}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            onToggle();
          }
        }}
      >
        <span className="lb-rank">{rank}</span>
        <span className="lb-id">
          <b>{p.code}</b>
          <small>{p.service_group}</small>
        </span>
        <span className="tier" data-tier={p.risk_tier}>
          {p.risk_tier}
        </span>
        <span className="lb-score" title={`Relative risk score ${p.risk_score.toFixed(1)} / 100`}>
          <span className="lb-bar">
            <span className="lb-fill" style={{ width: `${p.risk_score}%` }} />
          </span>
          <em>{p.risk_score.toFixed(0)}</em>
        </span>
        <span className="lb-num">{p.reviews}</span>
        <span className="lb-spark" style={{ color: TIER_VAR[p.risk_tier] }}>
          <RowSpark p={p} />
        </span>
        <TrendCell p={p} />
        <span className="lb-aspect">{shortAspect(p.top_aspect)}</span>
        <span className="lb-chev" aria-hidden="true" />
      </div>

      <div className="lb-body" aria-hidden={!open}>
        <div className="lb-body-in">
          <div className="lb-detail">
            <div className="lb-chart">
              <div className="kicker">Provider trajectory · yearly mean model risk</div>
              <TrajectoryChart history={p.history} color={TIER_VAR[p.risk_tier]} groupMedian={groupMedian} />
            </div>
            <div className="lb-facts">
              <div className="kicker">Signals</div>
              <dl>
                <dt>1–2★ share</dt>
                <dd>{fmtPct(p.observed_negative_rate)}</dd>
                <dt>Mean model risk</dt>
                <dd>{p.mean_risk.toFixed(2)}</dd>
                <dt>High-severity rate</dt>
                <dd>{fmtPct(p.high_severity_rate)}</dd>
                <dt>Recent risk (2021+)</dt>
                <dd>{p.recent_risk == null ? "—" : p.recent_risk.toFixed(2)}</dd>
                <dt>Reviews recent / prior</dt>
                <dd>
                  {p.recent_reviews} / {p.previous_reviews}
                </dd>
                <dt>Latest review</dt>
                <dd>{p.latest_review ?? "—"}</dd>
              </dl>
              {groupScore != null && (
                <p className="tiny">
                  {p.service_group}: median score {groupScore.toFixed(0)} · this provider {p.risk_score.toFixed(0)}
                </p>
              )}
            </div>
            <div className="lb-act">
              <div className="kicker">Operational recommendation</div>
              <p>{p.recommended_action}</p>
              <p className="tiny">Leading complaint signal: {p.top_aspect}. A review-based signal for human investigation — not a finding about the provider.</p>
            </div>
          </div>
        </div>
      </div>
    </li>
  );
}

interface Props {
  providers: Provider[];
  overview: Overview;
  selected: string | null;
  onSelect: (code: string | null) => void;
  aspectFilter: string | null;
  onClearAspect: () => void;
}

export function Leaderboard({ providers, overview, selected, onSelect, aspectFilter, onClearAspect }: Props) {
  const [tiers, setTiers] = useState<Set<Tier>>(new Set(TIERS));
  const [q, setQ] = useState("");
  const [sort, setSort] = useState<SortKey>("risk_score");
  const [limit, setLimit] = useState(40);

  const rankOf = useMemo(() => new Map(providers.map((p, i) => [p.code, i + 1])), [providers]);
  const groupOf = useMemo(() => new Map(overview.services.map((s) => [s.service_group, s])), [overview.services]);

  const rows = useMemo(() => {
    const list = providers.filter((p) => tiers.has(p.risk_tier) && (!aspectFilter || p.top_aspect === aspectFilter) && (!q || p.code.toLowerCase().includes(q.toLowerCase())));
    const val = (p: Provider) => (sort === "recent_risk" ? p.recent_risk : sort === "trend_delta" ? p.trend_delta : p.risk_score);
    return [...list].sort((a, b) => (val(b) ?? -Infinity) - (val(a) ?? -Infinity));
  }, [providers, tiers, q, sort, aspectFilter]);

  // If a provider is selected from elsewhere (KPI chip), make sure it is not hidden by the current filters.
  useEffect(() => {
    if (!selected) return;
    const idx = rows.findIndex((p) => p.code === selected);
    if (idx === -1) {
      setTiers(new Set(TIERS));
      setQ("");
      if (aspectFilter) onClearAspect();
    } else if (idx >= limit) setLimit(idx + 10);
  }, [selected, rows, limit, aspectFilter, onClearAspect]);

  const toggleTier = (t: Tier) =>
    setTiers((prev) => {
      const next = new Set(prev);
      if (next.has(t)) next.delete(t);
      else next.add(t);
      return next.size ? next : new Set(TIERS);
    });

  return (
    <Glass as="section" className="card lb" aria-label="Risk leaderboard">
      <header className="card-head">
        <div>
          <div className="kicker">Provider watchlist</div>
          <h2>Interactive Risk Leaderboard</h2>
          <p className="sub">
            {providers.length} providers with ≥ {overview.meta.min_reviews} reviews · anonymized · select a row to open its trajectory
          </p>
        </div>
        <div className="seg" role="group" aria-label="Sort by">
          {SORTS.map((s) => (
            <button key={s.key} className="pill" aria-pressed={sort === s.key} onClick={() => setSort(s.key)}>
              {s.label}
            </button>
          ))}
        </div>
      </header>

      <div className="lb-controls">
        <div className="tier-filters" role="group" aria-label="Filter by tier">
          {TIERS.map((t) => (
            <button key={t} className="pill" aria-pressed={tiers.has(t)} onClick={() => toggleTier(t)} style={{ ["--c" as string]: TIER_VAR[t] }}>
              <span className="dot" />
              {t}
              <span className="count">{overview.tiers[t] ?? 0}</span>
            </button>
          ))}
        </div>
        <label className="search">
          <span className="sr-only">Search provider code</span>
          <input placeholder="Search Provider_…" value={q} onChange={(e) => setQ(e.target.value)} />
        </label>
        {aspectFilter && (
          <button className="pill on" onClick={onClearAspect} title="Clear aspect filter">
            {shortAspect(aspectFilter)} ✕
          </button>
        )}
      </div>

      <div className="lb-cols" aria-hidden="true">
        <span>#</span>
        <span>Provider</span>
        <span>Tier</span>
        <span>Risk score</span>
        <span>Reviews</span>
        <span>History</span>
        <span>vs 2020</span>
        <span>Top signal</span>
        <span />
      </div>
      <ul className="lb-list">
        {rows.slice(0, limit).map((p) => (
          <Row
            key={p.code}
            p={p}
            rank={rankOf.get(p.code) ?? 0}
            open={selected === p.code}
            onToggle={() => onSelect(selected === p.code ? null : p.code)}
            groupMedian={groupOf.get(p.service_group)?.median_recent_risk ?? null}
            groupScore={groupOf.get(p.service_group)?.median_risk_score ?? null}
          />
        ))}
        {rows.length === 0 && <li className="lb-empty">No providers match these filters.</li>}
        {rows.length > limit && (
          <li className="lb-more">
            <button className="btn ghost" onClick={() => setLimit((l) => l + 40)}>
              Show {Math.min(40, rows.length - limit)} more · {rows.length - limit} remaining
            </button>
          </li>
        )}
      </ul>
    </Glass>
  );
}
