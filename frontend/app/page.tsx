import Link from "next/link";
import { ApiErrorPanel } from "@/components/ApiError";
import { TierBadge } from "@/components/TierBadge";
import { api } from "@/lib/api";

export const dynamic = "force-dynamic"; // always read live data; nothing is prerendered at build time

type SP = Promise<{ q?: string; tier?: string; trade?: string; trend?: string; sort?: string }>;

const pct = (v: number | null) => (v == null ? "—" : `${Math.round(v * 100)}%`);

export default async function Dashboard({ searchParams }: { searchParams: SP }) {
  const sp = await searchParams;
  let data;
  try {
    const [summary, list] = await Promise.all([api.summary(), api.providers({ ...sp, limit: "50" })]);
    data = { summary, list };
  } catch (e) {
    return <ApiErrorPanel message={(e as Error).message} />;
  }
  const { summary, list } = data;

  return (
    <>
      {summary.meta.data_mode === "sample" && <div className="card warn">Showing synthetic SAMPLE data — not real Yelp results.</div>}
      <h1>Provider risk dashboard</h1>
      <section className="kpis">
        <Kpi label="Reviews analysed" value={summary.dataset.n_reviews.toLocaleString()} />
        <Kpi label="Providers rated" value={`${summary.meta.n_providers_eligible} / ${summary.meta.n_providers_total}`} hint={`≥ ${summary.meta.min_reviews} reviews`} />
        <Kpi label="High risk" value={String(summary.tiers.High ?? 0)} tone="high" />
        <Kpi label="Worsening" value={String(summary.trend_counts.worsening ?? 0)} hint={`vs prior ${summary.meta.recent_months} months`} />
      </section>

      {/* TODO(frontend team): charts — tier donut, aspect bar chart, trend scatter (data is in /api/summary). */}

      <form className="filters card" method="get">
        <input name="q" placeholder="Search provider…" defaultValue={sp.q} />
        <select name="tier" defaultValue={sp.tier ?? ""}>
          <option value="">All tiers</option>
          <option>High</option>
          <option>Medium</option>
          <option>Low</option>
        </select>
        <select name="trade" defaultValue={sp.trade ?? ""}>
          <option value="">All trades</option>
          {summary.trades.map((t) => (
            <option key={t.trade}>{t.trade}</option>
          ))}
        </select>
        <select name="trend" defaultValue={sp.trend ?? ""}>
          <option value="">Any trend</option>
          <option>worsening</option>
          <option>improving</option>
          <option>stable</option>
        </select>
        <button type="submit">Filter</button>
      </form>

      <p className="muted small">{list.total} providers match</p>
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>Provider</th>
            <th>Trade</th>
            <th>Tier</th>
            <th>Score</th>
            <th>Reviews</th>
            <th>Avg ★</th>
            <th>Negative</th>
            <th>Trend</th>
            <th>Top issues</th>
          </tr>
        </thead>
        <tbody>
          {list.items.map((p) => (
            <tr key={p.business_id}>
              <td>{p.rank ?? "—"}</td>
              <td>
                <Link href={`/providers/${encodeURIComponent(p.business_id)}`}>{p.name}</Link>
                {p.safety_escalation && <span title="Repeated safety signals"> ⚠</span>}
              </td>
              <td>{p.trade}</td>
              <td>
                <TierBadge tier={p.risk_tier} />
              </td>
              <td>{p.risk_score?.toFixed(0) ?? "—"}</td>
              <td>{p.n_reviews}</td>
              <td>{p.avg_stars.toFixed(1)}</td>
              <td>{pct(p.neg_rate)}</td>
              <td>
                {p.trend}
                {p.trend !== "insufficient data" && (
                  <span className="muted small">
                    {" "}
                    ({pct(p.prior_neg_rate)} → {pct(p.recent_neg_rate)})
                  </span>
                )}
              </td>
              <td>{p.top_issues.map((i) => i.label).join(", ") || "—"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </>
  );
}

function Kpi({ label, value, hint, tone }: { label: string; value: string; hint?: string; tone?: "high" }) {
  return (
    <div className={`kpi card ${tone ?? ""}`}>
      <div className="kpi-value">{value}</div>
      <div>{label}</div>
      {hint && <div className="muted small">{hint}</div>}
    </div>
  );
}
