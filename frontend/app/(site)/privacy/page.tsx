import type { Metadata } from "next";
import Link from "next/link";
import { PageHero, Prose, Section } from "@/components/site/ui";
import { SITE } from "@/lib/site";

export const metadata: Metadata = { title: "Privacy", description: "What HomeLens AI collects, what it does not, and how review text is handled." };

export default function PrivacyPage() {
  return (
    <>
      <PageHero eyebrow="Legal" title="Privacy" />
      <Section tight>
        <Prose>
          <p className="meta">Last updated {SITE.updated}. HomeLens AI is a university course project, and this page is a plain-language description of its behavior, not legal advice.</p>
          <h2>What the site collects</h2>
          <p>We do not ask for accounts, names or emails. The site sets no cookies and loads no analytics, advertising or tracking scripts.</p>
          <h2>Review text you paste</h2>
          <p>Text you enter in the analyzer is sent to this site’s <code>/api/analyze</code> endpoint, scored in memory and returned to your browser. We do not write it to a database or file. Please do not paste personal data you would not want processed.</p>
          <h2>Hosting logs</h2>
          <p>The site is hosted on Vercel, which keeps standard operational logs such as request path, time and approximate network information. Request bodies, including pasted reviews, are not part of our application logging.</p>
          <h2>The demo dataset</h2>
          <p>The demo uses reviews from the Yelp Open Dataset for academic purposes. Providers are shown only as anonymized codes such as <code>Provider_0235</code>. Names, business IDs and reviewer identities are not shipped. The raw dataset is not published or redistributed.</p>
          <h2>Contact emails</h2>
          <p>If you email the team, we use your message only to reply.</p>
          <h2>Changes</h2>
          <p>We will update this page and its date if behavior changes. Questions? See <Link href="/contact">Contact</Link>.</p>
        </Prose>
      </Section>
    </>
  );
}
