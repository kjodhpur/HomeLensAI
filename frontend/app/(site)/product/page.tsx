import type { Metadata } from "next";
import Link from "next/link";
import { Card, Checklist, CtaBand, PageHero, Section } from "@/components/site/ui";
import { Icon } from "@/components/site/Icon";
import { facts } from "@/lib/data";
import { fmtInt } from "@/lib/format";

export const metadata: Metadata = {
  title: "Product",
  description: "Review analyzer, provider risk leaderboard, complaint-aspect radar, explainable evidence and action playbooks for home-service providers.",
};

export default function ProductPage() {
  return (
    <>
      <PageHero eyebrow="Product" title="Everything between a review and a decision." lead="HomeLens AI is a risk command center for home-service providers. It reads reviews, explains complaints, monitors providers over time and drafts the next step for a person to review.">
        <Link href="/demo" className="btn lg">
          Open the live demo <Icon name="arrow" size={18} />
        </Link>
        <Link href="/pricing" className="btn ghost lg">
          See pricing
        </Link>
      </PageHero>

      <Section>
        <div className="grid c3">
          <Card icon="radar" title="Review analyzer">
            <p>Paste any review and get a risk score against a recall-targeted threshold, the complaint aspects it contains and a recommended action, in under a second.</p>
          </Card>
          <Card icon="chart" title="Provider risk leaderboard">
            <p>Rank {fmtInt(facts.monitored_providers)} anonymized providers by a percentile-based risk score. Filter by tier, search by code and open any row for its yearly trajectory.</p>
          </Card>
          <Card icon="target" title="Complaint-aspect radar">
            <p>Eight aspects (workmanship, reliability, pricing, communication, timeliness, professionalism, warranty, safety) sized by lift. Select one to filter the leaderboard.</p>
          </Card>
          <Card icon="eye" title="Explainable evidence">
            <p>Every flag shows the sentence behind it, the phrases that matched and the term weights from the served model. If nothing matches, it routes to manual review.</p>
          </Card>
          <Card icon="bolt" title="Action playbooks">
            <p>Draft a triage response email or a quality-audit checklist for a provider, an aspect or a single review. Drafts are for human review; nothing is sent.</p>
          </Card>
          <Card icon="users" title="Human in the loop">
            <p>Signals are review-based and relative. Every Elevated or High-concern tier is an invitation for a person to investigate, never a verdict.</p>
          </Card>
        </div>
      </Section>

      <Section>
        <div className="split">
          <div>
            <span className="kicker">Command center</span>
            <h2 className="h2">One screen for the whole risk picture.</h2>
            <p>Three headline numbers, a live leaderboard, the aspect radar and the evidence feed share a single view, so a manager can go from “what changed?” to “what do I do?” without switching tools.</p>
          </div>
          <figure className="shot glass">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src="/img/overview.webp" alt="HomeLens AI command center overview with KPI cards for reviews analyzed, sentiment shift and critical risk escalations" width={1440} height={900} loading="lazy" decoding="async" />
          </figure>
        </div>
      </Section>

      <Section>
        <div className="split rev">
          <div>
            <span className="kicker">Aspect radar</span>
            <h2 className="h2">See what customers keep complaining about.</h2>
            <p>The radar sizes each aspect by lift, frequency or negative rate. Hover for its keyword cluster; select it to filter providers whose top signal matches.</p>
          </div>
          <figure className="shot glass">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src="/img/aspects.webp" alt="Aspect radar with eight complaint aspects and a keyword cluster tooltip" width={1440} height={900} loading="lazy" decoding="async" />
          </figure>
        </div>
      </Section>

      <Section>
        <div className="split">
          <div>
            <span className="kicker">Triage</span>
            <h2 className="h2">From signal to next step.</h2>
            <p>Select a provider, an aspect or a flagged review and open the triage dock. HomeLens drafts a response email or an audit checklist that a manager can edit, copy and own.</p>
          </div>
          <figure className="shot glass">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src="/img/triage.webp" alt="Action triage dock offering a triage response email and a quality audit checklist" width={1440} height={900} loading="lazy" decoding="async" />
          </figure>
        </div>
      </Section>

      <Section eyebrow="Intended use" title="Built for the people who own service quality." center>
        <div className="grid c3">
          <Card icon="users" title="Operations and quality teams">
            <p>Spot providers drifting toward repeat complaints before they become a pattern, and decide where to audit first.</p>
          </Card>
          <Card icon="chart" title="Customer-experience leads">
            <p>Understand which complaint aspects are rising across a service category and what to coach on.</p>
          </Card>
          <Card icon="scale" title="Marketplace trust teams">
            <p>Prioritize human review of providers whose reviews carry safety, conduct or billing language.</p>
          </Card>
        </div>
      </Section>

      <Section eyebrow="Status" title="What is in the demo today." center>
        <div className="grid c2" style={{ maxWidth: 880, margin: "0 auto" }}>
          <Card icon="check" title="Available now">
            <Checklist items={["Paste-a-review analyzer (TF–IDF model, DistilBERT in the notebook)", "Provider leaderboard, trends and tiers on anonymized data", "Aspect radar, evidence feed, model weights", "Triage email and audit checklist drafts", "Documented /api/analyze endpoint"]} />
          </Card>
          <Card icon="clock" title="On the roadmap">
            <Checklist items={["Upload your own review export", "Hosted DistilBERT inference", "Saved provider watchlists and alerts", "User accounts and audit logs", "Additional markets beyond Tucson, AZ"]} />
          </Card>
        </div>
      </Section>

      <CtaBand title="Try the working demo." lead="Anonymized, historical data. No sign-up." secondary={{ href: "/how-it-works", label: "How it works" }} />
    </>
  );
}
