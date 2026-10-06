import type { Metadata } from "next";
import { CtaBand, PageHero, Section } from "@/components/site/ui";

export const metadata: Metadata = {
  title: "Changelog",
  description: "What shipped in HomeLens AI, from the first pipeline to the public website.",
};

const RELEASES = [
  {
    date: "2026-10-06",
    title: "Public website and live demo",
    items: ["Product site with pricing, methodology, Responsible AI, docs, FAQ and legal pages", "Working review analyzer on the home page", "Command center moved to /demo", "Documented /api/analyze endpoint"],
  },
  {
    date: "2026-10-06",
    title: "Web app on the shared data layer",
    items: ["Next.js dashboard reading the teammate-built artifacts", "Review analysis ported to TypeScript with parity tests against the Python model", "Single Vercel project, no separate backend"],
  },
  {
    date: "2026-10-06",
    title: "Course notebook",
    items: ["Three-layer NLP pipeline: sentiment models, aspect extraction, provider risk", "Reads Yelp archives directly; runs on a synthetic sample when no data is present"],
  },
  {
    date: "2026-10-05",
    title: "Risk logic and Streamlit command center",
    items: ["Masking rules, phrase dictionary and recommended actions", "TF–IDF fallback model and DistilBERT loader", "Five-page Streamlit app with Responsible AI page and tests"],
  },
] as const;

export default function ChangelogPage() {
  return (
    <>
      <PageHero eyebrow="Changelog" title="What shipped." lead="Milestones from the first commit to the public site." />
      <Section tight>
        <div className="timeline">
          {RELEASES.map((r) => (
            <article key={r.title} className="release">
              <time dateTime={r.date}>{new Date(r.date).toLocaleDateString("en-US", { day: "numeric", month: "long", year: "numeric", timeZone: "UTC" })}</time>
              <h2>{r.title}</h2>
              <ul>
                {r.items.map((i) => (
                  <li key={i}>{i}</li>
                ))}
              </ul>
            </article>
          ))}
        </div>
      </Section>
      <CtaBand title="See the latest build." />
    </>
  );
}
