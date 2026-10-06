import type { AnalyzeResult } from "./types";

/** Browser → the Next.js route handler at /api/analyze (same app, same origin; see app/api/analyze/route.ts). */
export async function analyzeInBrowser(text: string): Promise<AnalyzeResult> {
  const res = await fetch("/api/analyze", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ text }) });
  if (!res.ok) throw new Error(res.status === 400 ? "Enter between 3 and 5,000 characters." : `Analysis failed (${res.status})`);
  return (await res.json()) as AnalyzeResult;
}
