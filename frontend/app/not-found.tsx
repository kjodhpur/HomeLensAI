import Link from "next/link";
import { SiteFooter } from "@/components/site/SiteFooter";
import { SiteHeader } from "@/components/site/SiteHeader";

export default function NotFound() {
  return (
    <>
      <SiteHeader />
      <main id="main" className="notfound">
        <b>404</b>
        <h1 className="h2">This page isn’t here</h1>
        <p className="lead">The link may be old, or the page may have moved.</p>
        <div className="hero-actions">
          <Link href="/" className="btn">
            Back to home
          </Link>
          <Link href="/demo" className="btn ghost">
            Open the demo
          </Link>
        </div>
      </main>
      <SiteFooter />
    </>
  );
}
