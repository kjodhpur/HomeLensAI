import Link from "next/link";
import { FOOTER, SITE } from "@/lib/site";

export function SiteFooter() {
  return (
    <footer className="site-footer">
      <div className="container">
        <div className="footer-grid">
          <div className="footer-brand">
            <Link href="/" className="logo" aria-label="HomeLens AI home">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src="/logo-mark.svg" alt="" width={28} height={28} />
              <span>HomeLens AI</span>
            </Link>
            <p>{SITE.tagline}. Built by students as a CIS 509 course project.</p>
          </div>
          {FOOTER.map((col) => (
            <nav key={col.title} aria-label={col.title}>
              <h2>{col.title}</h2>
              <ul>
                {col.links.map((l) => (
                  <li key={l.href}>
                    <Link href={l.href}>{l.label}</Link>
                  </li>
                ))}
              </ul>
            </nav>
          ))}
        </div>
        <div className="footer-base">
          <p>{SITE.disclaimer} Reviews are unverified customer allegations; every signal is for human investigation.</p>
          <p>© 2026 HomeLens AI team · Data: Yelp Open Dataset (academic use), Tucson, AZ</p>
        </div>
      </div>
    </footer>
  );
}
