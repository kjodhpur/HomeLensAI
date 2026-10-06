/** Site-wide constants. Optional public env vars add contact/repo links only when the team sets them (no dead links). */
export const SITE = {
  name: "HomeLens AI",
  tagline: "Review-based risk intelligence for home-service providers",
  description:
    "HomeLens AI turns customer reviews of home-service providers into review-level risk signals, explainable complaint aspects, provider monitoring and recommended management actions.",
  url: process.env.NEXT_PUBLIC_SITE_URL ?? (process.env.VERCEL_PROJECT_PRODUCTION_URL ? `https://${process.env.VERCEL_PROJECT_PRODUCTION_URL}` : "https://homelensai.vercel.app"),
  contactEmail: process.env.NEXT_PUBLIC_CONTACT_EMAIL ?? null,
  repoUrl: process.env.NEXT_PUBLIC_REPO_URL ?? null,
  updated: "6 October 2026",
  disclaimer: "System architecture surfaces consumer allegation signals; does not compile verified legal findings.",
} as const;

export const NAV = [
  { href: "/product", label: "Product" },
  { href: "/how-it-works", label: "How it works" },
  { href: "/pricing", label: "Pricing" },
  { href: "/security", label: "Responsible AI" },
  { href: "/docs", label: "Docs" },
] as const;

export const FOOTER = [
  {
    title: "Product",
    links: [
      { href: "/product", label: "Overview" },
      { href: "/demo", label: "Live demo" },
      { href: "/how-it-works", label: "How it works" },
      { href: "/pricing", label: "Pricing" },
      { href: "/changelog", label: "Changelog" },
    ],
  },
  {
    title: "Resources",
    links: [
      { href: "/docs", label: "Documentation" },
      { href: "/security", label: "Responsible AI" },
      { href: "/faq", label: "FAQ" },
    ],
  },
  {
    title: "Company",
    links: [
      { href: "/about", label: "About" },
      { href: "/contact", label: "Contact" },
    ],
  },
  {
    title: "Legal",
    links: [
      { href: "/privacy", label: "Privacy" },
      { href: "/terms", label: "Terms" },
    ],
  },
] as const;
