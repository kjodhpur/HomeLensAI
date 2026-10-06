import Image from "next/image";
import Link from "next/link";
import { HeroPreview } from "@/components/site/HeroPreview";
import { Icon } from "@/components/site/Icon";
import { LiveAnalyzer } from "@/components/site/LiveAnalyzer";
import { Checklist, CtaBand, Section, SkyBand, Stat, SunsetCards } from "@/components/site/ui";
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
      <section className="photo-hero on-dark">
        <Image src="/img/dusk.webp" alt="" fill priority sizes="100vw" quality={70} />
        <div className="container">
          <span className="mono-label">Why HomeLens</span>
          <h1 className="h1">
            Know which providers need <em>attention</em>, and why.
          </h1>
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
        <div className="after-photo">
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
        </div>
      </Section>

      <Section id="try" eyebrow="00 — Try it" title={<>Paste a review. See the <em>signal</em>.</>} lead="This is the working analyzer, not a mockup. Pick an example or paste your own text.">
        <LiveAnalyzer examples={examples} initialText={first.text} initialResult={initial} />
      </Section>

      <SunsetCards
        label="What it does"
        title={<>From a wall of reviews to a short list of <em>what to do</em>.</>}
        lead="Three layers turn free-form text into decisions a manager can act on, and every one of them is explainable."
        cards={[
          { label: "01 — Flag", title: "Flag the review", body: ["A fine-tuned DistilBERT model (with a TF–IDF fallback) scores every review against a recall-targeted threshold.", "Serious complaints are not missed."] },
          { label: "02 — Explain", title: "Explain the complaint", body: ["A phrase dictionary over eight aspects shows what went wrong.", "The evidence sentence is highlighted, so no score is a black box."] },
          { label: "03 — Watch", title: "Watch the provider", body: ["Provider scores, yearly trends and relative concern tiers show who needs management attention over time.", "A minimum of 20 reviews each."] },
        ]}
      />

      <Section>
        <div className="split">
          <div>
            <span className="kicker">01 — Provider monitoring</span>
            <h2 className="h2">An interactive risk <em>leaderboard</em>.</h2>
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
            <span className="kicker">02 — Explainable by design</span>
            <h2 className="h2">See the sentence behind the <em>score</em>.</h2>
            <p>Every flag comes with the sentence that triggered it, the dictionary phrases that matched, and the terms that moved the model. Managers can disagree with a signal because they can read exactly why it fired.</p>
            <Checklist items={["Evidence sentence with highlighted phrases", "Term-level weights from the served model", "No dictionary match? It goes to manual review"]} />
          </div>
          <figure className="shot glass">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src="/img/evidence.webp" alt="HomeLens AI evidence feed showing a flagged sentence, matched phrases and model weights" width={1440} height={900} loading="lazy" decoding="async" />
          </figure>
        </div>
      </Section>

      <Section eyebrow="03 — Complaint aspects" title={<>Eight things customers <em>complain</em> about.</>} lead="Each aspect has its own phrase dictionary and a measured lift: how much more often a review is negative when the aspect is mentioned.">
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

      <SkyBand label="Responsible AI" title={<>Signals for people, not <em>verdicts</em>.</>} left={{ title: "How we describe outputs", items: WE_SAY }} right={{ title: "What we never claim", items: NEVER }} />

      <CtaBand title={<>See it on <em>real</em> review data.</>} lead="The live demo runs on anonymized, historical reviews from Tucson, AZ. No sign-up." secondary={{ href: "/product", label: "Explore the product" }} />
    </>
  );
}
