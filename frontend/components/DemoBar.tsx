import Link from "next/link";
import type { Overview } from "@/lib/types";

const LINKS = [
  ["overview", "Overview"],
  ["providers", "Providers"],
  ["aspects", "Aspects"],
  ["evidence", "Evidence"],
] as const;

/** Slim glass bar for the demo: brand, section anchors, data scope and a way back to the site. */
export function DemoBar({ overview, modelLabel }: { overview: Overview; modelLabel: string | null }) {
  const { meta } = overview;
  const year = (iso: string) => new Date(iso).getUTCFullYear();
  return (
    <header className="dm-top">
      <div className="dm-bar glass">
        <Link href="/" className="logo" aria-label="HomeLens AI home">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src="/logo-mark.svg" alt="" width={28} height={28} />
          <span>HomeLens AI</span>
        </Link>
        <span className="dm-sep" aria-hidden="true" />
        <nav className="dm-nav" aria-label="Demo sections">
          {LINKS.map(([id, label]) => (
            <a key={id} href={`#${id}`}>
              {label}
            </a>
          ))}
        </nav>
        <div className="dm-end">
          <Link href="/product" className="btn ghost sm">
            About the product
          </Link>
        </div>
      </div>
      <div className="dm-meta">
        <h1>Business Risk Command Center</h1>
        <div className="dm-pills">
          <span className="pill static">{meta.market}</span>
          <span className="pill static">
            {year(meta.date_start)}–{year(meta.date_end)} · historical
          </span>
          <span className="pill static">Anonymized providers</span>
          {modelLabel && (
            <span className="pill static">
              <span className="dot" style={{ ["--c" as string]: "var(--t-stable)" }} />
              {modelLabel}
            </span>
          )}
        </div>
      </div>
    </header>
  );
}
