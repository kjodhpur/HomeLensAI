"use client";

import { useEffect, useState } from "react";

const LINKS = [
  { id: "overview", label: "Overview" },
  { id: "providers", label: "Providers" },
  { id: "aspects", label: "Aspects" },
  { id: "evidence", label: "Evidence" },
] as const;

/** Floating glass navigation (Daylight-style pill): jumps between dashboard sections and highlights the one in view. */
export function NavPill() {
  const [active, setActive] = useState<string>(LINKS[0].id);

  useEffect(() => {
    const seen = new Map<string, number>();
    const io = new IntersectionObserver(
      (entries) => {
        for (const e of entries) seen.set(e.target.id, e.isIntersecting ? e.intersectionRatio : 0);
        let best: string | null = null;
        let top = 0;
        for (const [id, ratio] of seen) if (ratio > top) (top = ratio), (best = id);
        if (best) setActive(best);
      },
      { rootMargin: "-20% 0px -45% 0px", threshold: [0, 0.1, 0.25, 0.5, 0.75, 1] },
    );
    for (const l of LINKS) {
      const el = document.getElementById(l.id);
      if (el) io.observe(el);
    }
    return () => io.disconnect();
  }, []);

  return (
    <nav className="navpill glass-sm" aria-label="Dashboard sections">
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src="/logo-mark.svg" alt="" width={26} height={26} className="navpill-logo" />
      <span className="navpill-name">HomeLens</span>
      <ul>
        {LINKS.map((l) => (
          <li key={l.id}>
            <a href={`#${l.id}`} aria-current={active === l.id ? "location" : undefined}>
              {l.label}
            </a>
          </li>
        ))}
      </ul>
      <a className="navpill-cta" href="#evidence">
        Analyze a review
      </a>
    </nav>
  );
}
