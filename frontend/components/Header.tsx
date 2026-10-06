import type { Overview } from "@/lib/types";

export function Header({ overview, modelLabel }: { overview: Overview; modelLabel: string | null }) {
  const { meta } = overview;
  const fmt = (iso: string) => new Date(iso).toLocaleDateString("en-US", { month: "short", year: "numeric", timeZone: "UTC" });
  return (
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
  );
}
