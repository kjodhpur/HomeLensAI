import type { Overview } from "@/lib/types";
import { NavPill } from "./NavPill";

export function Header({ overview, modelLabel }: { overview: Overview; modelLabel: string | null }) {
  const { meta } = overview;
  const fmt = (iso: string) => new Date(iso).toLocaleDateString("en-US", { month: "short", year: "numeric", timeZone: "UTC" });
  return (
    <>
      <NavPill />
      <header className="topbar">
      <div className="brand">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img src="/logo-mark.svg" alt="" width={40} height={40} />
        <div>
          <h1>HomeLens AI</h1>
          <span>Business Risk Command Center</span>
        </div>
      </div>
      <div className="topbar-pills">
        <span className="pill static">{meta.market} home services</span>
        <span className="pill static">
          {fmt(meta.date_start)} – {fmt(meta.date_end)}
        </span>
        <span className="pill static">Anonymized providers</span>
        {modelLabel && (
          <span className="pill static">
            <span className="dot" style={{ ["--c" as string]: "var(--t-stable)" }} />
            {modelLabel}
          </span>
        )}
      </div>
      </header>
      <section className="hero" aria-label="Product summary">
        <span className="kicker">Review-based risk signals · human investigation</span>
        <h2>
          See which providers need <em>management attention</em> before the next complaint lands.
        </h2>
        <p>
          HomeLens AI reads Yelp reviews of {meta.market} home-service providers and turns them into review-level alerts, complaint aspects with the evidence behind them, and recommended next steps. Every signal is a customer allegation, not a verified finding.
        </p>
      </section>
    </>
  );
}
