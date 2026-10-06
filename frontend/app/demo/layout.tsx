import type { Metadata } from "next";
import "./demo.css";

export const metadata: Metadata = {
  title: "Live demo",
  description: "The HomeLens AI command center: KPIs, provider risk leaderboard, complaint-aspect radar, explainable evidence feed and action triage, on anonymized historical data.",
};

export default function DemoLayout({ children }: { children: React.ReactNode }) {
  return <div className="demo">{children}</div>;
}
