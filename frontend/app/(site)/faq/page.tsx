import type { Metadata } from "next";
import Link from "next/link";
import { CtaBand, Faq, PageHero, Section } from "@/components/site/ui";

export const metadata: Metadata = {
  title: "FAQ",
  description: "Answers about what HomeLens AI does, how accurate it is, what data it uses and what it never claims.",
};

export default function FaqPage() {
  return (
    <>
      <PageHero eyebrow="FAQ" title="Questions, answered plainly." />
      <Section tight>
        <Faq
          items={[
            { q: "What is HomeLens AI?", a: <p>A risk command center that turns customer reviews of home-service providers into review-level risk signals, explainable complaint aspects, provider monitoring and recommended actions for a person to review.</p> },
            { q: "Does it detect fraud or predict that a business will fail?", a: <p>No. It reports review-based risk signals and relative concern tiers. It does not verify any allegation, establish misconduct or liability, or predict bankruptcy. See <Link href="/security">Responsible AI</Link>.</p> },
            { q: "How accurate is it?", a: <p>On held-out businesses, the fine-tuned DistilBERT reaches 0.973 macro-F1 and the TF–IDF logistic regression 0.951. Scores are for classifying low-star versus high-star reviews, not for judging a business. Details on <Link href="/how-it-works">How it works</Link>.</p> },
            { q: "Which model powers the website demo?", a: <p>The TF–IDF logistic regression, ported to TypeScript so it runs inside this site. DistilBERT is the primary model in the notebook and Streamlit app; it is not bundled here because of its size.</p> },
            { q: "What data does it use?", a: <p>Yelp Open Dataset reviews of home-service providers in Tucson, AZ, from November 2006 to January 2022. Providers are anonymized as Provider_XXXX and need at least 20 reviews to be monitored.</p> },
            { q: "Can I use it on my own reviews?", a: <p>You can paste any review into the analyzer. Uploading a full export is on the roadmap. Note the models were trained on Yelp reviews from one market.</p> },
            { q: "Is my pasted text stored?", a: <p>No. It is processed for the request and returned. See the <Link href="/privacy">privacy policy</Link>.</p> },
            { q: "Why is a review flagged but no aspect is shown?", a: <p>The model found the review high-risk but no dictionary phrase matched. HomeLens routes these to manual review instead of guessing an aspect.</p> },
            { q: "What do the tiers mean?", a: <p>Stable below 50, Watch 50–75, Elevated 75–90, High concern 90 and above. They rank providers against each other in this corpus and are not probabilities.</p> },
            { q: "Is it free?", a: <p>The demo is free with no account. There are no paid plans today. See <Link href="/pricing">Pricing</Link>.</p> },
          ]}
        />
      </Section>
      <CtaBand title="Still curious?" primary={{ href: "/contact", label: "Contact the team" }} secondary={{ href: "/docs", label: "Documentation" }} />
    </>
  );
}
