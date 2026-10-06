import type { Tier } from "./types";

export const TIERS: Tier[] = ["High concern", "Elevated", "Watch", "Stable"];
export const TIER_VAR: Record<Tier, string> = {
  "High concern": "var(--t-high)",
  Elevated: "var(--t-elev)",
  Watch: "var(--t-watch)",
  Stable: "var(--t-stable)",
};

/** The 8 aspects in the order the radar lays them out, with the short label shown on the blob. */
export const ASPECT_ORDER: { aspect: string; short: string }[] = [
  { aspect: "Workmanship", short: "Workmanship" },
  { aspect: "Reliability / No-show", short: "Reliability" },
  { aspect: "Pricing / Billing", short: "Pricing" },
  { aspect: "Communication", short: "Communication" },
  { aspect: "Timeliness", short: "Timeliness" },
  { aspect: "Professionalism / Trust", short: "Professionalism" },
  { aspect: "Warranty / Follow-up", short: "Warranty" },
  { aspect: "Safety / Property Damage", short: "Safety" },
];

export const shortAspect = (aspect: string) => ASPECT_ORDER.find((a) => a.aspect === aspect)?.short ?? aspect;

export const fmtInt = (n: number) => n.toLocaleString("en-US");
export const fmtPct = (v: number | null | undefined, digits = 0) => (v == null ? "—" : `${(v * 100).toFixed(digits)}%`);
export const fmtSigned = (v: number, digits = 1) => `${v >= 0 ? "+" : "−"}${Math.abs(v).toFixed(digits)}`;

export const clamp = (v: number, lo: number, hi: number) => Math.min(hi, Math.max(lo, v));
export const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
