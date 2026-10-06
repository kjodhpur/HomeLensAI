"use client";

import { useState } from "react";
import { analyzeInBrowser } from "@/lib/api";
import { shortAspect } from "@/lib/format";
import type { AnalyzeResult, Example } from "@/lib/types";
import { Highlighted } from "./Highlighted";

const toneFor = (r: AnalyzeResult) => (r.management_attention == null ? "var(--accent)" : r.management_attention ? "var(--t-high)" : "var(--t-stable)");
const verdictFor = (r: AnalyzeResult) => (r.management_attention == null ? "Dictionary signals only" : r.management_attention ? "Management attention" : "Routine monitoring");

/** Compact paste-a-review analyzer used on the home page. Posts to /api/analyze (same app). */
export function LiveAnalyzer({ examples, initialText, initialResult }: { examples: Example[]; initialText: string; initialResult: AnalyzeResult }) {
  const [text, setText] = useState(initialText);
  const [result, setResult] = useState<AnalyzeResult>(initialResult);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const run = async (t: string) => {
    if (t.trim().length < 3) return;
    setBusy(true);
    setError(null);
    try {
      setResult(await analyzeInBrowser(t));
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  };

  const ev = result.evidence;
  const tone = toneFor(result);
  return (
    <div className="analyzer glass">
      <div className="an-pane">
        <label htmlFor="live-review">Paste a customer review</label>
        <div className="examples" role="group" aria-label="Example reviews">
          {examples.map((ex) => (
            <button
              key={ex.id}
              className="pill"
              onClick={() => {
                setText(ex.text);
                void run(ex.text);
              }}
            >
              <span className="dot" style={{ ["--c" as string]: ex.kind === "complaint" ? "var(--t-high)" : "var(--t-stable)" }} />
              {ex.label}
            </button>
          ))}
        </div>
        <textarea id="live-review" className="review-input" value={text} maxLength={5000} onChange={(e) => setText(e.target.value)} placeholder="e.g. The crew showed up two days late and left the job unfinished…" />
        <div className="an-actions">
          <button className="btn" onClick={() => run(text)} disabled={busy || text.trim().length < 3}>
            {busy ? "Analyzing…" : "Analyze review"}
          </button>
          <span className="an-hint">Scored in your browser session by the same model the demo uses. Nothing is stored.</span>
        </div>
        {error && <p className="err">{error}</p>}
      </div>

      <div className="an-pane an-result" aria-live="polite" style={{ ["--c" as string]: tone }}>
        <div className="verdict">
          <span className="verdict-badge">{verdictFor(result)}</span>
          <span className="an-hint">{result.model.name}</span>
        </div>
        {result.risk_probability != null && result.operating_threshold != null && (
          <div>
            <div className="meter" role="img" aria-label={`Review risk ${result.risk_probability.toFixed(2)}, threshold ${result.operating_threshold.toFixed(3)}`} style={{ ["--p" as string]: result.risk_probability, ["--t" as string]: result.operating_threshold }}>
              <i />
              <u />
            </div>
            <div className="meter-label">
              <span>Review risk {result.risk_probability.toFixed(2)}</span>
              <span>Threshold {result.operating_threshold.toFixed(3)}</span>
            </div>
          </div>
        )}
        {result.detected_aspects.length > 0 ? (
          <div className="chips" style={{ justifyContent: "flex-start" }}>
            {result.detected_aspects.map((a) => (
              <span key={a} className="chip">
                {shortAspect(a)}
              </span>
            ))}
          </div>
        ) : (
          <p className="an-hint">{result.management_attention ? "No dictionary match: send to manual review." : "No complaint signal found in this review."}</p>
        )}
        {ev && (
          <blockquote className="evidence">
            <Highlighted text={ev.sentence} phrases={ev.matched_phrases} />
            <footer>
              Evidence sentence{ev.has_dictionary_match ? ` · ${shortAspect(ev.aspect)}` : ""}
              {ev.risk_probability != null ? ` · sentence risk ${ev.risk_probability.toFixed(2)}` : ""}
            </footer>
          </blockquote>
        )}
        <p className="rec">
          <b>Recommended action.</b> {result.recommended_action}
        </p>
      </div>
    </div>
  );
}
