"use client";

import { useState } from "react";
import { analyzeText } from "@/lib/api";
import type { AnalyzeResult } from "@/lib/types";

const EXAMPLE = "They never showed up and then overcharged me, $600 more than quoted. Nobody ever called back.";

export default function AnalyzePage() {
  const [text, setText] = useState(EXAMPLE);
  const [result, setResult] = useState<AnalyzeResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function run() {
    setBusy(true);
    setError(null);
    try {
      setResult(await analyzeText(text));
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <h1>Analyze a review</h1>
      <p className="muted">Paste a review to see which complaint aspects it triggers and the evidence sentence for each (lite version of the notebook&apos;s Layer 2).</p>
      <textarea rows={6} value={text} onChange={(e) => setText(e.target.value)} />
      <p>
        <button onClick={run} disabled={busy || text.trim().length < 3}>
          {busy ? "Analyzing…" : "Analyze"}
        </button>
      </p>
      {error && <div className="card error">{error}</div>}
      {result && (
        <div className="card">
          <p>
            Sentiment compound: <strong>{result.text_compound}</strong> ({result.negative_sentiment ? "negative" : "not negative"})
          </p>
          {result.signals.length === 0 && <p>No complaint signals detected.</p>}
          {result.signals.map((s, i) => (
            <blockquote key={i}>
              <strong>{s.label}</strong> — “{s.sentence}”<footer>matched “{s.cue}” ({s.tier})</footer>
            </blockquote>
          ))}
          <p className="muted small">{result.note}</p>
        </div>
      )}
    </>
  );
}
