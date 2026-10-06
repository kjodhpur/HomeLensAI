import type { Metadata } from "next";
import { Icon } from "@/components/site/Icon";
import { Card, CtaBand, PageHero, Section } from "@/components/site/ui";
import { facts, overview } from "@/lib/data";
import { fmtInt } from "@/lib/format";

export const metadata: Metadata = {
  title: "How it works",
  description: "The three-layer NLP pipeline behind HomeLens AI: sentiment models, aspect extraction and provider risk scoring, with validated results.",
};

const FLOW = [
  { icon: "doc", t: "Collect", d: "Yelp reviews of home-service providers in one market" },
  { icon: "lock", t: "Mask", d: "URLs, emails, phones, dollar amounts and star phrases replaced with tokens" },
  { icon: "radar", t: "Score", d: "Each review scored for risk against an operating threshold" },
  { icon: "target", t: "Explain", d: "Phrase dictionary finds the aspect and the evidence sentence" },
  { icon: "chart", t: "Monitor", d: "Aggregate to providers, trends and relative tiers" },
] as const;

export default function HowItWorksPage() {
  const best = [...overview.models].sort((a, b) => b.macro_f1 - a.macro_f1)[0].model;
  return (
    <>
      <PageHero eyebrow="Methodology" title="A transparent pipeline, from raw text to a decision." lead="HomeLens AI combines supervised sentiment models with a rule-based aspect dictionary and a provider-level scoring layer. Every step can be inspected." />

      <Section tight>
        <div className="flow">
          {FLOW.map((f) => (
            <div key={f.t} className="glass-sm" style={{ borderRadius: 18, padding: 18 }}>
              <span style={{ color: "var(--accent-ink)" }}>
                <Icon name={f.icon} size={20} />
              </span>
              <b>{f.t}</b>
              <span>{f.d}</span>
            </div>
          ))}
        </div>
      </Section>

      <Section eyebrow="Three layers" title="What happens to a review.">
        <div className="grid c3">
          <Card tag="Layer 1" title="Is this review a risk signal?">
            <p>One- and two-star reviews are the risk class, four- and five-star the comparison class; three-star reviews are held out. A fine-tuned DistilBERT model is the primary scorer. A TF–IDF logistic regression is the fallback and powers this website’s demo.</p>
            <p>Thresholds are chosen to keep negative-class recall at or above {Math.round(facts.recall_floor * 100)}%.</p>
          </Card>
          <Card tag="Layer 2" title="What exactly went wrong?">
            <p>A curated phrase dictionary over eight aspects finds the complaint language in each sentence and picks the evidence sentence. High-risk reviews with no match go to manual review.</p>
          </Card>
          <Card tag="Layer 3" title="Does it keep happening?">
            <p>Reviews roll up to providers with at least {overview.meta.min_reviews} reviews. A score blends mean risk, recent risk and high-severity rate as percentiles, then maps to a relative tier.</p>
          </Card>
        </div>
      </Section>

      <Section eyebrow="Results" title="Validated on businesses the model never saw." lead="The split holds out whole businesses, so test scores are not inflated by a provider appearing in both training and test data.">
        <div className="table-wrap glass">
          <table className="t">
            <thead>
              <tr>
                <th>Model</th>
                <th>Threshold</th>
                <th>Accuracy</th>
                <th>Macro-F1</th>
                <th>Neg. precision</th>
                <th>Neg. recall</th>
                <th>ROC-AUC</th>
              </tr>
            </thead>
            <tbody>
              {overview.models.map((m) => {
                const row = m as unknown as Record<string, number | string>;
                return (
                  <tr key={m.model} className={m.model === best ? "best" : undefined}>
                    <td>{m.model}</td>
                    <td>{m.operating_threshold.toFixed(3)}</td>
                    <td>{(row.accuracy as number).toFixed(3)}</td>
                    <td>{m.macro_f1.toFixed(3)}</td>
                    <td>{m.negative_precision.toFixed(3)}</td>
                    <td>{m.negative_recall.toFixed(3)}</td>
                    <td>{(row.roc_auc as number).toFixed(3)}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
        <p className="foot-note" style={{ textAlign: "left" }}>
          Test set: {fmtInt(facts.split[2].reviews)} reviews from {facts.split[2].businesses} held-out businesses ({fmtInt(facts.test_negatives)} negative, {fmtInt(facts.test_positives)} positive). TextBlob is the lexicon baseline. Source: <code>artifacts/model_comparison.csv</code>.
        </p>
      </Section>

      <Section eyebrow="The data" title="What the models learned from.">
        <div className="grid c3">
          <Card icon="doc" title={`${fmtInt(facts.core_reviews)} core reviews`}>
            <p>Filtered from {fmtInt(facts.candidate_reviews)} candidates. {fmtInt(facts.providers)} providers and {fmtInt(facts.unique_reviewers)} reviewers in {facts.market}, {facts.date_start}–{facts.date_end}. Median length {facts.median_words} words.</p>
          </Card>
          <Card icon="layers" title="Business-held-out splits">
            {facts.split.map((s) => (
              <p key={s.split}>
                <b>{s.split}:</b> {fmtInt(s.reviews)} reviews, {s.businesses} businesses
              </p>
            ))}
          </Card>
          <Card icon="lock" title="Masked before modeling">
            <p>Phone numbers, emails, links, dollar amounts and star phrases are replaced with tokens so a model cannot lean on a rating written into the text.</p>
          </Card>
        </div>
      </Section>

      <Section eyebrow="Provider scoring" title="A relative score, not a probability." lead="The risk score is a weighted blend of percentiles, which makes it a ranking inside this corpus.">
        <div className="grid c2">
          <Card title="Score formula">
            <p>
              <code>100 × (0.50 · mean-risk percentile + 0.30 · recent-risk percentile + 0.20 · high-severity percentile)</code>
            </p>
            <p>Recent means 2021 onward. The trend compares recent against the 2020 mean and only appears with at least three reviews in each period.</p>
          </Card>
          <Card title="Tiers">
            {(Object.keys(overview.tier_rules) as (keyof typeof overview.tier_rules)[]).map((t) => (
              <p key={t} style={{ display: "flex", justifyContent: "space-between", gap: 12 }}>
                <span className="tier" data-tier={t}>
                  {t}
                </span>
                <span>
                  {overview.tier_rules[t]} · {overview.tiers[t]} providers
                </span>
              </p>
            ))}
          </Card>
        </div>
      </Section>

      <CtaBand title="Inspect it yourself." lead="Paste a review and read the evidence, the matched phrases and the term weights." secondary={{ href: "/docs", label: "Read the docs" }} />
    </>
  );
}
