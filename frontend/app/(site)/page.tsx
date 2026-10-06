import Link from "next/link";
import { HeroPreview } from "@/components/site/HeroPreview";
import { Icon } from "@/components/site/Icon";
import { LiveAnalyzer } from "@/components/site/LiveAnalyzer";
import { Card, Checklist, CtaBand, Section, Stat } from "@/components/site/ui";
import { aspects, examples, facts, overview } from "@/lib/data";
import { analyzeReview } from "@/lib/engine/analyze";
import { fmtInt, shortAspect } from "@/lib/format";

const WE_SAY = ["Review-based risk signal", "Management attention", "Operational concern and complaint signal", "Relative concern tier", "A prompt for human investigation"];
const NEVER = ["Bankruptcy or financial-failure prediction", "Legal liability", "Verified misconduct or fraud", "Verified safety violation"];

export default function Home() {
  const first = examples[0];
  const initial = analyzeReview(first.text);
  const best = overview.models[0];
  return (
    <>
      <section className="home-hero">
        <div className="container">
          <span className="eyebrow glass-sm">
            <Icon name="radar" size={16} /> Review-based risk intelligence for home services
          </span>
          <h1 className="h1">Know which providers need attention, and why.</h1>
          <p className="lead">HomeLens AI reads customer reviews of plumbers, electricians, HVAC and other home-service providers, flags the complaints that matter, shows the exact words behind each signal, and tells you what to do next.</p>
          <div className="hero-actions">
            <Link href="/demo" className="btn lg">
              Open the live demo <Icon name="arrow" size={18} />
            </Link>
            <Link href="/how-it-works" className="btn ghost lg">
              How it works
            </Link>
          </div>
          <HeroPreview text={first.text} result={initial} />
        </div>
      </section>

      <Section tight>
        <div className="stats glass" role="list">
          <div role="listitem">
            <Stat value={fmtInt(facts.core_reviews)} label="Reviews analyzed" note={`${facts.market}, ${new Date(overview.meta.date_start).getUTCFullYear()}–${new Date(overview.meta.date_end).getUTCFullYear()}`} />
          </div>
          <div role="listitem">
            <Stat value={fmtInt(facts.monitored_providers)} label="Providers monitored" note="Anonymized, 20+ reviews each" />
          </div>
          <div role="listitem">
            <Stat value="8" label="Complaint aspects" note="Pricing, safety, reliability and more" />
          </div>
          <div role="listitem">
            <Stat value={best.macro_f1.toFixed(3)} label="Macro-F1, held-out test" note={`${best.model}, businesses held out`} />
          </div>
        </div>
        <p className="foot-note">Metrics come from the validated course notebook. Reviews are historical customer allegations, not verified findings.</p>
      </Section>

      <Section id="try" eyebrow="Try it" title="Paste a review. See the signal." lead="This is the working analyzer, not a mockup. Pick an example or paste your own text.">
        <LiveAnalyzer examples={examples} initialText={first.text} initialResult={initial} />
      </Section>

      <Section eyebrow="What it does" title="From a wall of reviews to a short list of what to do." lead="Three layers turn free-form text into decisions a manager can act on, and every one of them is explainable.">
        <div className="grid c3">
          <Card icon="radar" title="1 · Flag the review">
            <p>A fine-tuned DistilBERT model (with a TF–IDF fallback) scores every review against a recall-targeted threshold, so serious complaints are not missed.</p>
          </Card>
          <Card icon="target" title="2 · Explain the complaint">
            <p>A phrase dictionary over eight aspects shows what went wrong and highlights the evidence sentence, so no score is a black box.</p>
          </Card>
          <Card icon="chart" title="3 · Watch the provider">
            <p>Provider-level scores, yearly trends and relative concern tiers show who needs management attention over time, with a minimum of 20 reviews.</p>
          </Card>
        </div>
      </Section>

      <Section>
        <div className="split">
          <div>
            <span className="kicker">Provider monitoring</span>
            <h2 className="h2">An interactive risk leaderboard.</h2>
            <p>Rank {fmtInt(facts.monitored_providers)} anonymized providers by risk score, filter by tier, search by code, and open any row to see its yearly trajectory, signals and recommended operational action.</p>
            <Checklist items={["Four relative concern tiers, always labeled", "Recent-vs-prior trend with a minimum review count", "Click a row to open triage actions"]} />
          </div>
          <figure className="shot glass">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src="/img/leaderboard.webp" alt="HomeLens AI risk leaderboard listing anonymized providers with tiers, scores and trends" width={1440} height={900} loading="lazy" decoding="async" />
          </figure>
        </div>
      </Section>

      <Section>
        <div className="split rev">
          <div>
            <span className="kicker">Explainable by design</span>
            <h2 className="h2">See the sentence behind the score.</h2>
            <p>Every flag comes with the sentence that triggered it, the dictionary phrases that matched, and the terms that moved the model. Managers can disagree with a signal because they can read exactly why it fired.</p>
            <Checklist items={["Evidence sentence with highlighted phrases", "Term-level weights from the served model", "No dictionary match? It goes to manual review"]} />
          </div>
          <figure className="shot glass">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src="/img/evidence.webp" alt="HomeLens AI evidence feed showing a flagged sentence, matched phrases and model weights" width={1440} height={900} loading="lazy" decoding="async" />
          </figure>
        </div>
      </Section>

      <Section eyebrow="Complaint aspects" title="Eight things customers complain about." lead="Each aspect has its own phrase dictionary and a measured lift: how much more often a review is negative when the aspect is mentioned.">
        <div className="grid c4">
          {[...aspects]
            .sort((a, b) => b.lift - a.lift)
            .map((a) => (
              <article key={a.aspect} className="aspect-card glass lift">
                <h3>{shortAspect(a.aspect)}</h3>
                <div className="aspect-stats">
                  <span>
                    <b>{a.lift.toFixed(1)}×</b>lift
                  </span>
                  <span>
                    <b>{fmtInt(a.reviews_with_signal)}</b>reviews
                  </span>
                </div>
                <div className="chips" style={{ justifyContent: "flex-start" }}>
                  {a.keywords.slice(0, 3).map((k) => (
                    <span key={k} className="chip">
                      {k}
                    </span>
                  ))}
                </div>
              </article>
            ))}
        </div>
      </Section>

      <Section eyebrow="Responsible AI" title="Signals for people, not verdicts." lead="A review is one customer's account. HomeLens AI surfaces patterns so a person knows where to look first.">
        <div className="grid c2">
          <Card icon="check" title="How we describe outputs">
            <Checklist items={WE_SAY} />
          </Card>
          <Card icon="shield" title="What we never claim">
            <Checklist items={NEVER} positive={false} />
          </Card>
        </div>
        <p className="foot-note">
          <Link href="/security" style={{ color: "var(--accent-ink)" }}>
            Read the full Responsible AI approach
          </Link>
        </p>
      </Section>

      <CtaBand title="See it on real review data." lead="The live demo runs on anonymized, historical reviews from Tucson, AZ. No sign-up." secondary={{ href: "/product", label: "Explore the product" }} />
    </>
  );
}
