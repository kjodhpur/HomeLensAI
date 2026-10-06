import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "HomeLens AI — risk intelligence for home-service providers",
  description: "NLP-based risk signals from customer reviews: recurring issues, trends and recommended actions.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <header className="site-header">
          <div className="container row">
            <Link href="/" className="brand">
              HomeLens <span>AI</span>
            </Link>
            <nav>
              <Link href="/">Dashboard</Link>
              <Link href="/analyze">Analyze a review</Link>
            </nav>
          </div>
        </header>
        <main className="container">{children}</main>
        <footer className="container muted small">
          Complaint signals detected in customer reviews. Reviews are unverified customer allegations, not findings of wrongdoing. CIS 509 course project.
        </footer>
      </body>
    </html>
  );
}
