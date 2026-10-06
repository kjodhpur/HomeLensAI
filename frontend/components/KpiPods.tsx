"use client";

import type { ReactNode } from "react";
import { fmtInt, fmtPct } from "@/lib/format";
import { useCountUp } from "@/lib/hooks";
import type { Overview } from "@/lib/types";
import { Glass } from "./Glass";
import { MercurySparkline } from "./MercurySparkline";

interface PodProps {
  index: number;
  label: string;
  value: ReactNode;
  caption: string;
  tone?: string;
  series: { x: number; y: number }[];
  format: (y: number) => string;
  sparkTone?: string;
  detail: ReactNode;
  alert?: boolean;
}

function Pod({ index, label, value, caption, series, format, sparkTone, detail, alert }: PodProps) {
  return (
    // The tooltip is a SIBLING of the glass pod (not a child): a nested backdrop-filter could not blur what lies outside its parent.
    <div className="pod-cell" style={{ ["--i" as string]: index }}>
      <Glass className={`pod${alert ? " pod-alert" : ""}`} ripple tabIndex={0} aria-label={`${label}: ${caption}`}>
        <div className="kicker">{label}</div>
        <div className="pod-value">{value}</div>
        <div className="pod-caption">{caption}</div>
        <MercurySparkline points={series} format={format} tone={sparkTone} />
      </Glass>
      <div className="pod-detail glass" role="tooltip">
        {detail}
      </div>
    </div>
  );
}

export function KpiPods({ overview, onSelectProvider }: { overview: Overview; onSelectProvider: (code: string) => void }) {
  const { reviews_analyzed: ra, sentiment_shift: ss, escalations: es } = overview.kpis;
  const reviews = useCountUp(ra.value);
  const shift = useCountUp(ss.shift?.delta_pts ?? 0, 1400, 1);
  const esc = useCountUp(es.value, 1000);

  const peak = ra.series.reduce((a, b) => (b.y > a.y ? b : a), ra.series[0]);

  return (
    <section className="pods" aria-label="Key metrics">
      <Pod
        index={0}
        label="Total Reviews Analyzed"
        value={fmtInt(Math.round(reviews))}
        caption={`${overview.meta.market} home-service reviews`}
        series={ra.series}
        format={(y) => `${fmtInt(y)} reviews`}
        detail={
          <>
            <div className="kicker">Corpus</div>
            <dl>
              <dt>Providers in corpus</dt>
              <dd>{fmtInt(ra.providers)}</dd>
              <dt>Unique reviewers</dt>
              <dd>{fmtInt(ra.unique_reviewers)}</dd>
              <dt>Window</dt>
              <dd>
                {overview.meta.date_start.slice(0, 4)}–{overview.meta.date_end.slice(0, 4)}
              </dd>
              <dt>Busiest year</dt>
              <dd>
                {peak.x} · {fmtInt(peak.y)}
              </dd>
            </dl>
          </>
        }
      />
      <Pod
        index={1}
        label="Net Sentiment Shift"
        alert={(ss.shift?.delta_pts ?? 0) > 0}
        value={
          <>
            {(ss.shift?.delta_pts ?? 0) >= 0 ? "+" : "−"}
            {Math.abs(shift).toFixed(1)}
            <small> pts</small>
          </>
        }
        caption={ss.shift ? `negative-review share · ${ss.shift.to_year} vs ${ss.shift.from_year}` : "not enough history"}
        series={ss.series}
        format={(y) => `${fmtPct(y, 1)} negative`}
        sparkTone="var(--t-high)"
        detail={
          ss.shift ? (
            <>
              <div className="kicker">Year over year</div>
              <dl>
                <dt>{ss.shift.from_year}</dt>
                <dd>{fmtPct(ss.shift.from_rate, 1)} negative</dd>
                <dt>{ss.shift.to_year}</dt>
                <dd>{fmtPct(ss.shift.to_rate, 1)} negative</dd>
                <dt>Definition</dt>
                <dd>1–2★ share of reviews</dd>
              </dl>
            </>
          ) : null
        }
      />
      <Pod
        index={2}
        label="Critical Risk Escalations"
        alert={es.value > 0}
        value={esc >= 0 ? Math.round(esc) : 0}
        caption={`High-concern providers · of ${es.monitored} monitored`}
        series={es.series}
        format={(y) => `mean risk ${y.toFixed(2)}`}
        sparkTone="var(--t-high)"
        detail={
          <>
            <div className="kicker">Needs human investigation</div>
            <dl>
              <dt>High concern</dt>
              <dd>{es.value} providers</dd>
              <dt>Elevated</dt>
              <dd>{es.elevated} providers</dd>
            </dl>
            <div className="code-chips">
              {es.codes.map((c) => (
                <button key={c} className="pill" onClick={() => onSelectProvider(c)}>
                  {c}
                </button>
              ))}
            </div>
            <p className="tiny">Sparkline: review-weighted mean model risk of these providers by year.</p>
          </>
        }
      />
    </section>
  );
}
