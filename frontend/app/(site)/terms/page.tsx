import type { Metadata } from "next";
import Link from "next/link";
import { PageHero, Prose, Section } from "@/components/site/ui";
import { SITE } from "@/lib/site";

export const metadata: Metadata = { title: "Terms", description: "Terms of use for the HomeLens AI demo website." };

export default function TermsPage() {
  return (
    <>
      <PageHero eyebrow="Legal" title="Terms of use" />
      <Section tight>
        <Prose>
          <p className="meta">Last updated {SITE.updated}. HomeLens AI is a university course project. These terms are a plain-language summary, not legal advice.</p>
          <h2>Educational demo</h2>
          <p>The site and its analysis are provided for demonstration and education. Features may change or disappear without notice.</p>
          <h2>No verified findings</h2>
          <p>Outputs are review-based risk signals produced by statistical models from unverified customer reviews. They are not statements of fact and do not establish misconduct, legal liability, safety violations or the financial condition of any business. Use them only as a prompt for human investigation.</p>
          <h2>Acceptable use</h2>
          <ul>
            <li>Do not use the site to harass, defame or make decisions about individuals or businesses based solely on a signal.</li>
            <li>Do not attempt to re-identify the anonymized providers.</li>
            <li>Do not overload the service or probe it for vulnerabilities.</li>
          </ul>
          <h2>Data</h2>
          <p>The demo data derives from the Yelp Open Dataset, used under its academic terms. It is not for redistribution.</p>
          <h2>No warranty</h2>
          <p>The site is provided “as is” without warranties of any kind. To the extent permitted by law, the project team is not liable for losses arising from its use.</p>
          <h2>Contact</h2>
          <p>
            Questions about these terms? See <Link href="/contact">Contact</Link>.
          </p>
        </Prose>
      </Section>
    </>
  );
}
