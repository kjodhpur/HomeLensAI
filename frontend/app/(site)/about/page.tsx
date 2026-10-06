import type { Metadata } from "next";
import { Card, CtaBand, PageHero, Section } from "@/components/site/ui";

export const metadata: Metadata = {
  title: "About",
  description: "HomeLens AI is a CIS 509 Analytics for Unstructured Data course project turning customer reviews into explainable risk signals.",
};

const TEAM = ["Rithik Roy Thati", "Kanha Jodhpurkar", "Sankalp Sharma Madgula", "Dev Bhattacharyya"];
const initials = (n: string) => n.split(" ").map((p) => p[0]).slice(0, 2).join("");

export default function AboutPage() {
  return (
    <>
      <PageHero eyebrow="About" title="Built by a student team, held to a product standard." lead="HomeLens AI started as the final project for CIS 509, Analytics for Unstructured Data. We wanted to see how far free-form customer language could go as an early-warning signal for service quality." />

      <Section eyebrow="Mission" title="Make complaints legible." lead="Home-service customers describe problems in their own words. We turn that language into signals a manager can read, challenge and act on, without pretending the signal is a verdict.">
        <div className="grid c3">
          <Card icon="eye" title="Explainable first">
            <p>If we can’t show the sentence and phrases behind a flag, we don’t ship the flag.</p>
          </Card>
          <Card icon="scale" title="Careful with claims">
            <p>Reviews are allegations. Our language stays at “risk signal” and “management attention,” never “fraud” or “liability.”</p>
          </Card>
          <Card icon="lock" title="Privacy by default">
            <p>Providers are anonymized, text is masked before modeling and pasted reviews are not stored.</p>
          </Card>
        </div>
      </Section>

      <Section eyebrow="Team" title="The people behind it.">
        <div className="grid c2">
          {TEAM.map((n) => (
            <div key={n} className="person glass">
              <span className="avatar" aria-hidden="true">
                {initials(n)}
              </span>
              <div>
                <b>{n}</b>
                <span>CIS 509 project team</span>
              </div>
            </div>
          ))}
        </div>
      </Section>

      <Section eyebrow="Under the hood" title="Technology.">
        <div className="grid c3">
          <Card title="Modeling">
            <p>Fine-tuned DistilBERT, TF–IDF logistic regression, a lexicon baseline, and a phrase-dictionary aspect extractor.</p>
          </Card>
          <Card title="Data">
            <p>Yelp Open Dataset reviews of home-service providers in Tucson, AZ, processed in a reproducible notebook pipeline.</p>
          </Card>
          <Card title="Product">
            <p>A Streamlit command center for analysts and this Next.js site, deployed on Vercel, which runs the same analysis in TypeScript.</p>
          </Card>
        </div>
      </Section>

      <CtaBand title="Have feedback?" lead="We’d like to hear how you would use it." primary={{ href: "/contact", label: "Get in touch" }} secondary={{ href: "/how-it-works", label: "Read the methodology" }} />
    </>
  );
}
