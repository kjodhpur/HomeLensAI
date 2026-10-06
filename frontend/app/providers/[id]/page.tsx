import Link from "next/link";
import { notFound } from "next/navigation";
import { ApiErrorPanel } from "@/components/ApiError";
import { TierBadge } from "@/components/TierBadge";
import { ApiError, api } from "@/lib/api";
import type { Provider } from "@/lib/types";

export const dynamic = "force-dynamic";

const pct = (v: number | null | undefined) => (v == null ? "—" : `${Math.round(v * 100)}%`);

export default async function ProviderPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  let p: Provider;
  try {
    p = await api.provider(decodeURIComponent(id));
  } catch (e) {
    if (e instanceof ApiError && e.status === 404) notFound();
    return <ApiErrorPanel message={(e as Error).message} />;
  }

  return (
    <>
      <p>
        <Link href="/">← Dashboard</Link>
      </p>
      <h1>
        {p.name} <TierBadge tier={p.risk_tier} />
      </h1>
      <p className="muted">
        {p.trade} · {p.city}, {p.state} · {p.n_reviews} reviews · avg {p.avg_stars.toFixed(1)}★ · negative-signal rate {pct(p.neg_rate)}
        {p.risk_score != null && ` · risk score ${p.risk_score.toFixed(0)} (rank ${p.rank})`}
      </p>
      {p.safety_escalation && <div className="card warn">⚠ Repeated safety signals in reviews — escalate for human review.</div>}

      <section className="grid2">
        <div className="card">
          <h3>Trend</h3>
          <p>
            <strong>{p.trend.direction}</strong>
            {p.trend.delta != null && (
              <>
                {" "}
                ({pct(p.prior.neg_rate)} → {pct(p.recent.neg_rate)}, p = {p.trend.p_value?.toFixed(3)})
              </>
            )}
          </p>
          {/* TODO(frontend team): line chart of p.history (yearly negative rate). */}
          <ul className="small muted">
            {p.history.map((h) => (
              <li key={h.year}>
                {h.year}: {h.n} reviews, {pct(h.neg_rate)} flagged, {h.avg_stars.toFixed(1)}★
              </li>
            ))}
          </ul>
        </div>
        <div className="card">
          <h3>Recommended action</h3>
          <p>
            <strong>Manager:</strong> {p.action_manager}
          </p>
          <p>
            <strong>Homeowner:</strong> {p.action_homeowner}
          </p>
        </div>
      </section>

      <h2>Issues with evidence</h2>
      {p.issues.length === 0 && <p className="muted">No complaint signals detected.</p>}
      {p.issues.map((i) => (
        <div className="card" key={i.aspect}>
          <h3>
            {i.label}{" "}
            <span className={`pill ${i.recurring ? "pill-rec" : ""}`}>{i.recurring ? "recurring" : "isolated"}</span>
          </h3>
          <p className="muted small">{i.n_reviews} flagged reviews ({pct(i.share_of_flagged)} of flagged)</p>
          {i.evidence.map((e) => (
            <blockquote key={e.review_id}>
              “{e.sentence}”
              <footer>
                {e.date} · {e.stars}★ · matched “{e.cue}”
              </footer>
            </blockquote>
          ))}
        </div>
      ))}
    </>
  );
}
