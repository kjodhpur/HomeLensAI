import { Fragment } from "react";
import { shortAspect } from "@/lib/format";
import type { AnalyzeResult } from "@/lib/types";
import { Highlighted } from "./Highlighted";

/** Static product preview for the hero, rendered at build time from a real analysis of an example review. */
export function HeroPreview({ text, result }: { text: string; result: AnalyzeResult }) {
  const flagged = result.sentences.filter((s) => s.flagged);
  const ev = result.evidence;
  return (
    <div className="hero-preview glass" role="img" aria-label="Preview: a review with its flagged sentences, complaint aspects and recommended action">
      <div className="hp-grid">
        <div className="hp-pane">
          <h3>Customer review</h3>
          <p className="hp-review">
            {result.sentences.map((s) => (
              <Fragment key={s.index}>
                {s.flagged ? (
                  <mark className="flag">
                    <Highlighted text={s.text} phrases={s.matched_phrases} />
                  </mark>
                ) : (
                  s.text
                )}{" "}
              </Fragment>
            ))}
          </p>
          {ev && (
            <p className="hp-evidence">
              <span>Evidence sentence</span>
              {ev.has_dictionary_match ? shortAspect(ev.aspect) : "No dictionary match"} · sentence risk {ev.risk_probability?.toFixed(2)}
            </p>
          )}
        </div>
        <div className="hp-pane hp-meta">
          <h3>What HomeLens found</h3>
          <div className="hp-row">
            <span>Decision</span>
            <b>
              <span className="tier" data-tier={result.management_attention ? "High concern" : "Stable"}>
                {result.management_attention ? "Management attention" : "Routine monitoring"}
              </span>
            </b>
          </div>
          <div className="hp-row">
            <span>Review risk</span>
            <b>
              {result.risk_probability?.toFixed(2)} <small style={{ color: "var(--ink-3)", fontWeight: 500 }}>vs {result.operating_threshold?.toFixed(3)}</small>
            </b>
          </div>
          <div className="hp-row">
            <span>Complaint aspects</span>
            <div className="chips">
              {result.detected_aspects.map((a) => (
                <span key={a} className="chip">
                  {shortAspect(a)}
                </span>
              ))}
            </div>
          </div>
          <div className="hp-row">
            <span>Flagged sentences</span>
            <b>
              {flagged.length} of {result.sentences.length}
            </b>
          </div>
          <div className="hp-row">
            <span>Next step</span>
            <b style={{ maxWidth: "20ch", fontWeight: 500, fontSize: 13.5 }}>{result.recommended_action}</b>
          </div>
        </div>
      </div>
    </div>
  );
}
