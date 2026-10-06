import { SITE } from "@/lib/site";

/** The allegation disclaimer, kept visible at the foot of the demo. */
export function DemoFooter() {
  return (
    <footer className="dm-foot" role="contentinfo">
      <p>{SITE.disclaimer}</p>
      <p>Demo data: anonymized, historical Yelp reviews (Tucson, AZ). Reviews are unverified customer allegations.</p>
    </footer>
  );
}
