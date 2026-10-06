import type { Metadata } from "next";
import Link from "next/link";
import { Checklist, CtaBand, Faq, PageHero, Section } from "@/components/site/ui";
import { Icon } from "@/components/site/Icon";

export const metadata: Metadata = {
  title: "Pricing",
  description: "How HomeLens AI could be packaged: a free public demo today, with pilot and enterprise plans on the roadmap.",
};

export default function PricingPage() {
  return (
    <>
      <PageHero eyebrow="Pricing" title="Free to explore. Built to grow into a pilot." lead="HomeLens AI is a university course project, so nothing is for sale today. These plans describe how it could be packaged once it runs on a customer’s own review data." />

      <Section tight>
        <div className="notice glass" style={{ maxWidth: 880, margin: "0 auto 36px" }}>
          <Icon name="alert" size={20} />
          <p>The public demo is free and needs no account. Pilot and Enterprise are planning notes, not offers: there are no prices, contracts or sign-ups yet.</p>
        </div>
        <div className="grid c3">
          <article className="plan glass">
            <span className="kicker">Available now</span>
            <h3>Explore</h3>
            <p className="price">
              Free <small>no account</small>
            </p>
            <Checklist items={["Live analyzer on any pasted review", "Provider leaderboard on anonymized Tucson, AZ data", "Aspect radar, evidence feed and model weights", "Triage email and audit checklist drafts", "Public /api/analyze endpoint"]} />
            <Link href="/demo" className="btn">
              Open the demo
            </Link>
          </article>
          <article className="plan glass featured">
            <span className="kicker" style={{ color: "var(--accent-ink)" }}>
              Planned
            </span>
            <h3>Pilot</h3>
            <p className="price">
              Let’s talk <small>scoped per team</small>
            </p>
            <Checklist items={["Upload your own review export", "Provider monitoring with your thresholds", "Hosted model inference", "Shared watchlists and playbooks", "Onboarding with the project team"]} />
            <Link href="/contact" className="btn accent">
              Register interest
            </Link>
          </article>
          <article className="plan glass">
            <span className="kicker">Roadmap</span>
            <h3>Enterprise</h3>
            <p className="price">
              Custom <small>not yet offered</small>
            </p>
            <Checklist items={["Single sign-on and roles", "Audit log of every signal and action", "Scheduled review ingestion", "Multi-market models", "Security review and data-processing terms"]} />
            <Link href="/contact" className="btn ghost">
              Ask about the roadmap
            </Link>
          </article>
        </div>
      </Section>

      <Section eyebrow="Questions" title="Pricing questions" center>
        <Faq
          items={[
            { q: "Is HomeLens AI a commercial product?", a: <p>Not yet. It is a CIS 509 course project built by a student team. The demo is real software on real, anonymized data, but there is no paid service.</p> },
            { q: "What would a pilot need from us?", a: <p>A CSV export of your reviews (text, rating, date, provider). We would anonymize providers, validate the model on your data and agree thresholds with your team before showing any score.</p> },
            { q: "Will you store the reviews I paste into the demo?", a: <p>No. Pasted text is processed for the request and returned. See the <Link href="/privacy">privacy policy</Link>.</p> },
            { q: "Why is there no price list?", a: <p>Quoting prices for a service that does not exist would be misleading. When a pilot is real, pricing will be published here.</p> },
          ]}
        />
      </Section>

      <CtaBand title="Start with the demo." lead="It takes a minute and needs no sign-up." secondary={{ href: "/contact", label: "Talk to the team" }} />
    </>
  );
}
