// Draft generators for the action-triage dock. Nothing is sent anywhere — these are starting points for a human.
// Wording follows the project terminology rules: review-based risk signal, management attention, human investigation.
import { shortAspect } from "./format";
import type { TriageContext } from "./types";

const AUDIT_STEPS: Record<string, string[]> = {
  Workmanship: [
    "Pull the last 90 days of completed jobs and flag repeat visits / callbacks for the same address.",
    "Inspect a sample of recent jobs against the completion checklist; photograph and log defects.",
    "Review technician training records for the trades involved.",
    "Confirm every job closes with a quality check-in call.",
  ],
  "Reliability / No-show": [
    "Export scheduled-vs-arrived timestamps for the last 90 days; list missed and cancelled appointments.",
    "Check that appointment confirmations (and reminders) are actually sent.",
    "Review dispatch capacity on the days with the most misses.",
    "Agree a backup-crew rule for same-day cancellations.",
  ],
  Timeliness: [
    "Measure cycle time from booking to completion; locate the longest queues.",
    "Check whether customers are notified when a job slips.",
    "Review supplier lead times for recurring delayed parts.",
    "Set arrival-window targets and track them weekly.",
  ],
  "Pricing / Billing": [
    "Compare quote vs final invoice for the last 90 days; list variances over a set tolerance.",
    "Verify change orders were approved in writing before extra charges.",
    "Check fee disclosure on quotes and invoices.",
    "Review how disputed charges are escalated and resolved.",
  ],
  Communication: [
    "Audit unanswered calls / messages and time-to-first-response.",
    "Assign a named owner to every open customer request.",
    "Introduce a same-business-day callback standard and an escalation path.",
    "Send proactive status updates on open jobs.",
  ],
  "Professionalism / Trust": [
    "Read the complaint-flagged reviews and note which interactions are described.",
    "Hold a conduct and customer-service refresher with the crews involved.",
    "Review site clean-up and respect-for-property standards.",
    "Follow up personally with affected customers.",
  ],
  "Safety / Property Damage": [
    "Escalate immediately for human review — do not wait for the next reporting cycle.",
    "Identify the jobs behind the signal and verify permit, licence and inspection records.",
    "Contact the affected customers and document what happened from their side and the crew's.",
    "Pause similar work until the investigation concludes; record corrective actions.",
  ],
  "Warranty / Follow-up": [
    "List warranty claims from the last 90 days with open / closed dates.",
    "Check the warranty policy is being applied consistently.",
    "Audit repeat repairs on the same job and time-to-closure.",
    "Confirm every warranty claim has a named owner and a customer follow-up.",
  ],
};
const COMMON_STEPS = [
  "Record findings and owners; this review-based signal is a prompt for investigation, not a conclusion.",
  "Re-check the review signal 30 days after changes are made.",
];

interface Facts {
  subject: string;
  aspect: string;
  action: string;
  lines: string[];
  tag: string;
}

function facts(ctx: TriageContext): Facts {
  switch (ctx.kind) {
    case "provider": {
      const p = ctx.provider;
      const trend =
        p.trend_delta == null ? "trend not yet measurable" : `mean model risk ${p.trend_delta >= 0 ? "up" : "down"} ${Math.abs(p.trend_delta).toFixed(2)} versus 2020`;
      return {
        subject: p.code,
        aspect: p.top_aspect,
        action: p.recommended_action,
        tag: `${p.risk_tier} · score ${p.risk_score.toFixed(0)}`,
        lines: [
          `Relative concern tier: ${p.risk_tier} (risk score ${p.risk_score.toFixed(1)} / 100)`,
          `Service group: ${p.service_group}; ${p.reviews} reviews analysed`,
          `Leading complaint signal: ${p.top_aspect}`,
          `Trend: ${trend}`,
        ],
      };
    }
    case "aspect": {
      const a = ctx.aspect;
      return {
        subject: `${shortAspect(a.aspect)} complaint signal`,
        aspect: a.aspect,
        action: a.recommended_action,
        tag: `${a.lift.toFixed(1)}× lift`,
        lines: [
          `${a.reviews_with_signal.toLocaleString()} reviews mention this aspect; ${(a.negative_rate_when_mentioned * 100).toFixed(0)}% of them are negative`,
          `Negative-review rate is ${a.lift.toFixed(1)}× the corpus baseline when mentioned`,
          `${a.providers_led} monitored providers have this as their leading signal`,
        ],
      };
    }
    case "review": {
      const r = ctx.result;
      const p = r.risk_probability;
      return {
        subject: "Analysed customer review",
        aspect: r.primary_aspect,
        action: r.recommended_action,
        tag: p == null ? "dictionary signal" : `p = ${p.toFixed(2)}`,
        lines: [
          p == null
            ? "Scoring model unavailable; dictionary complaint signals only"
            : `Risk probability ${p.toFixed(4)} against an operating threshold of ${r.operating_threshold?.toFixed(3)} (${r.model.name})`,
          `Detected complaint signals: ${r.detected_aspects.join(", ") || "none"}`,
          ...(r.evidence ? [`Evidence sentence: “${r.evidence.sentence}”`] : []),
        ],
      };
    }
  }
}

export function triageEmail(ctx: TriageContext): { subject: string; body: string } {
  const f = facts(ctx);
  const parts = f.subject.toLowerCase().includes(shortAspect(f.aspect).toLowerCase()) ? [f.subject] : [f.subject, shortAspect(f.aspect)];
  const subject = `[HomeLens AI] Review-based risk signal — ${parts.join(" — ")}`;
  const body = [
    "Hi team,",
    "",
    `HomeLens AI has surfaced a review-based risk signal that warrants management attention: ${f.subject}.`,
    "",
    ...f.lines.map((l) => `  • ${l}`),
    "",
    "Recommended next step:",
    `  ${f.action}`,
    "",
    "Please assign an owner and confirm by end of week. This signal is drawn from customer reviews, which are unverified allegations; it is a prompt for human investigation, not a finding about the business.",
    "",
    "Thanks,",
    "Operations",
  ].join("\n");
  return { subject, body };
}

export function qualityAudit(ctx: TriageContext): { title: string; steps: string[] } {
  const f = facts(ctx);
  const steps = AUDIT_STEPS[f.aspect] ?? [
    "Review the flagged reviews manually and expand the complaint dictionary if the issue is not yet covered.",
    "Identify the jobs behind the signal and interview the people involved.",
  ];
  return { title: `Quality audit — ${f.subject} (${shortAspect(f.aspect)})`, steps: [...steps, ...COMMON_STEPS] };
}

export const triageMeta = (ctx: TriageContext) => {
  const f = facts(ctx);
  return { subject: f.subject, aspect: f.aspect, action: f.action, tag: f.tag };
};
