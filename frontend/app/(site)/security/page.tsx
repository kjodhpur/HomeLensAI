import type { Metadata } from "next";
import { Card, CtaBand, PageHero, Section, SkyBand } from "@/components/site/ui";
import { Icon } from "@/components/site/Icon";
import { facts } from "@/lib/data";

export const metadata: Metadata = {
  title: "Responsible AI & privacy",
  description: "Scope, limitations, human oversight and privacy: how HomeLens AI keeps review-based risk signals fair, transparent and reviewable.",
};

const SAY = ["Review-based risk signal", "Needs management attention", "Operational concern and complaint signal", "Relative concern tier within this corpus", "Prompt for human investigation"];
const NEVER = ["Bankruptcy or financial-failure prediction", "Legal liability", "Verified misconduct or fraud detection", "Verified safety violation", "A verdict on any individual business"];

export default function SecurityPage() {
  return (
    <>
      <PageHero eyebrow="Responsible AI" title="Signals for people, not verdicts." lead="HomeLens AI surfaces patterns in customer language so managers know where to look. Every alert is a starting point for human judgment." />

      <SkyBand label="Language guardrails" title={<>How we describe <em>outputs</em>.</>} left={{ title: "We say", items: SAY }} right={{ title: "We never claim", items: NEVER }} />

      <Section eyebrow="01 — Known limitations" title={<>What the data can and <em>cannot</em> tell you.</>}>
        <div className="grid c3">
          <Card icon="pin" title="One market" tag="Scope">
            <p>Reviews come from {facts.market} only. Patterns may not transfer to other markets.</p>
          </Card>
          <Card icon="clock" title="Historical data" tag="Scope">
            <p>Data runs from {facts.date_start} to {facts.date_end} and may not reflect how providers operate today.</p>
          </Card>
          <Card icon="users" title="Self-selection bias" tag="Bias">
            <p>Yelp reviewers are not a random sample of customers. Very satisfied and very unhappy customers are over-represented.</p>
          </Card>
          <Card icon="chart" title="Star ratings as labels" tag="Labels">
            <p>Models learn from star ratings, an imperfect proxy for operational risk. Three-star reviews were excluded from training.</p>
          </Card>
          <Card icon="alert" title="Unverified allegations" tag="Claims">
            <p>A review is one customer’s account. Detected safety or conduct language is a claim to investigate, not a confirmed event.</p>
          </Card>
          <Card icon="scale" title="Relative tiers" tag="Benchmark">
            <p>Provider tiers rank providers against each other within this corpus. They are not absolute probabilities of any outcome.</p>
          </Card>
        </div>
      </Section>

      <Section eyebrow="Human oversight" title="Every serious signal goes through a person.">
        <div className="flow">
          {[
            ["radar", "Signal raised", "Model score exceeds the operating threshold"],
            ["eye", "Analyst review", "Read the full review and its context"],
            ["users", "Provider dialogue", "Hear the business’s side before acting"],
            ["bolt", "Proportionate action", "Coaching, process fix, or no action"],
            ["clock", "Monitor and retrain", "Track drift and refresh the model"],
          ].map(([icon, t, d]) => (
            <div key={t}>
              <span style={{ color: "var(--accent-ink)" }}>
                <Icon name={icon as "radar"} size={20} />
              </span>
              <b>{t}</b>
              <span>{d}</span>
            </div>
          ))}
        </div>
      </Section>

      <Section eyebrow="Privacy" title="Data privacy and anonymization.">
        <div className="grid c3">
          <Card icon="lock" title="Providers are masked">
            <p>Businesses appear only as stable codes such as Provider_0235. Names and Yelp business IDs are not shipped with the app.</p>
          </Card>
          <Card icon="shield" title="Text is masked before modeling">
            <p>URLs, emails, phone numbers, dollar amounts and explicit star phrases are replaced with tokens before any model sees the text.</p>
          </Card>
          <Card icon="list" title="Volume threshold">
            <p>A provider needs at least {20} reviews before it is monitored, which avoids noisy, unfair conclusions from a handful of reviews.</p>
          </Card>
          <Card icon="eye" title="No raw data deployed">
            <p>The website ships aggregates and a small model only. The raw Yelp dataset is never published.</p>
          </Card>
          <Card icon="doc" title="Pasted text is not stored">
            <p>Review text you type into the analyzer is processed for the request and not saved. The site sets no cookies and loads no analytics or ad trackers.</p>
          </Card>
          <Card icon="scale" title="Dataset terms">
            <p>The Yelp Open Dataset is used for academic purposes under its terms and is not redistributed.</p>
          </Card>
        </div>
      </Section>

      <CtaBand title="Questions about how a signal is made?" lead="Read the methodology or inspect the analysis endpoint." primary={{ href: "/how-it-works", label: "How it works" }} secondary={{ href: "/docs", label: "Documentation" }} />
    </>
  );
}
