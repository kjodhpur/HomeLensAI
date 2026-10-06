"use client";

import { Fragment, useMemo, useState } from "react";
import { analyzeInBrowser } from "@/lib/api";
import { shortAspect } from "@/lib/format";
import type { AnalyzeResult, Example, SentenceResult } from "@/lib/types";
import { Glass } from "./Glass";

const esc = (s: string) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

/** Wrap dictionary phrases found inside a sentence in <mark> so the reader sees exactly what matched. */
function withPhrases(text: string, s: SentenceResult | { matched_phrases: Record<string, string[]> }) {
  const phrases = [...new Set(Object.values(s.matched_phrases).flat())].sort((a, b) => b.length - a.length);
  if (!phrases.length) return text;
  const re = new RegExp(`(${phrases.map(esc).join("|")})`, "gi");
  return text.split(re).map((part, i) => (i % 2 ? <mark key={i} className="phrase">{part}</mark> : <Fragment key={i}>{part}</Fragment>));
}

interface Props {
  examples: Example[];
  initialText: string;
  initialResult: AnalyzeResult | null;
  flagged: boolean;
  onFlag: (result: AnalyzeResult) => void;
}

export function EvidenceFeed({ examples, initialText, initialResult, flagged, onFlag }: Props) {
  const [text, setText] = useState(initialText);
  const [analyzed, setAnalyzed] = useState(initialText);
  const [result, setResult] = useState<AnalyzeResult | null>(initialResult);
  const [editing, setEditing] = useState(!initialResult);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [evIdx, setEvIdx] = useState<number | null>(null);
  const [weights, setWeights] = useState(false);
  const [drop, setDrop] = useState(0);

  const run = async (t: string) => {
    if (t.trim().length < 3) return;
    setBusy(true);
    setError(null);
    try {
      const r = await analyzeInBrowser(t);
      setResult(r);
      setAnalyzed(t);
      setEvIdx(null);
      setEditing(false);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  };

  const pick = (ex: Example) => {
    setText(ex.text);
    void run(ex.text);
  };

  const evidence = useMemo(() => {
    if (!result) return null;
    const s = evIdx != null ? result.sentences.find((x) => x.index === evIdx) : null;
    if (s) return { sentence: s.text, aspect: s.aspects[0] ?? "No dictionary match", phrases: s.matched_phrases, p: s.risk_probability, match: s.aspects.length > 0, index: s.index };
    const e = result.evidence;
    return e ? { sentence: e.sentence, aspect: e.aspect, phrases: e.matched_phrases, p: e.risk_probability, match: e.has_dictionary_match, index: e.index } : null;
  }, [result, evIdx]);

  const annotated = useMemo(() => {
    if (!result) return null;
    const out: React.ReactNode[] = [];
    let cursor = 0;
    for (const s of [...result.sentences].sort((a, b) => a.start - b.start)) {
      if (s.start > cursor) out.push(<Fragment key={`g${s.index}`}>{analyzed.slice(cursor, s.start)}</Fragment>);
      const body = withPhrases(analyzed.slice(s.start, s.end), s);
      out.push(
        s.flagged ? (
          <button key={s.index} type="button" className={`jelly${evidence?.index === s.index ? " on" : ""}`} onClick={() => setEvIdx(s.index)} title={`Model risk for this sentence: ${s.risk_probability?.toFixed(2)} — click to inspect`}>
            {body}
            <span className="jelly-tag">p {s.risk_probability?.toFixed(2)}</span>
          </button>
        ) : (
          <span key={s.index} className="calm" title={s.risk_probability != null ? `Model risk for this sentence: ${s.risk_probability.toFixed(2)}` : undefined}>
            {body}
          </span>
        ),
      );
      cursor = s.end;
    }
    if (cursor < analyzed.length) out.push(<Fragment key="tail">{analyzed.slice(cursor)}</Fragment>);
    return out;
  }, [result, analyzed, evidence?.index]);

  const maxW = result?.weights ? Math.max(...result.weights.terms.map((t) => Math.abs(t.weight)), 0.01) : 1;
  const att = result?.management_attention;

  return (
    <Glass as="section" id="evidence" className="panel deck" aria-label="Explainable NLP evidence feed">
      <header className="card-head">
        <div>
          <div className="kicker">Explainable NLP ground truth</div>
          <h2>Evidence Feed</h2>
          <p className="sub">Paste a review: see which sentences the model flags and the exact phrases behind each complaint signal</p>
        </div>
        {result && (
          <div className="model-chip glass-sm" title={result.model.note}>
            <span className="live" /> {result.model.name}
            {result.operating_threshold != null && <small> · threshold {result.operating_threshold.toFixed(3)}</small>}
          </div>
        )}
      </header>

      <div className="deck-split">
        {/* ------------------------------------------------------------ input */}
        <div className="deck-pane">
          <div className="pane-title">
            <span className="kicker">Input</span>
            <b>Raw customer review</b>
          </div>
          <div className="dm-examples" role="group" aria-label="Example reviews">
            {examples.map((ex) => (
              <button key={ex.id} className="pill" onClick={() => pick(ex)} data-kind={ex.kind} title={ex.kind === "complaint" ? "Complaint example (synthetic)" : "Positive example (synthetic)"}>
                <span className="dot" style={{ ["--c" as string]: ex.kind === "complaint" ? "var(--t-high)" : "var(--t-stable)" }} />
                {ex.label}
              </button>
            ))}
          </div>

          {editing || !annotated ? (
            <textarea className="dm-input" value={text} onChange={(e) => setText(e.target.value)} placeholder="e.g. The crew showed up two days late and left the job unfinished…" maxLength={5000} aria-label="Customer review text" />
          ) : (
            <div className="dm-view" aria-live="polite">
              {annotated}
            </div>
          )}

          <div className="pane-actions">
            <button className="btn" onClick={() => run(text)} disabled={busy || text.trim().length < 3}>
              {busy ? "Analyzing…" : editing || !result ? "Analyze review" : "Re-analyze"}
            </button>
            {result && !editing && (
              <button className="btn ghost" onClick={() => setEditing(true)}>
                Edit text
              </button>
            )}
            <span className="legend">
              <i className="jelly-swatch" /> sentence scored ≥ threshold
              <i className="phrase-swatch" /> dictionary phrase
            </span>
          </div>
          {error && <p className="dm-err">{error}</p>}
          {result?.masking_applied && <p className="tiny">Phone numbers, emails, links, dollar amounts and star phrases are masked before scoring.</p>}
        </div>

        {/* --------------------------------------------------------- evidence */}
        <div className="deck-pane terminal" aria-live="polite">
          <div className="term-bar">
            <i />
            <i />
            <i />
            <span>evidence · phrase-dictionary match (mirrors the notebook&apos;s spaCy PhraseMatcher)</span>
          </div>
          {!result ? (
            <p className="term-empty">Analyze a review to see its evidence sentence.</p>
          ) : (
            <div className="term-body" key={`${analyzed}-${evidence?.index}`}>
              <pre className="term-lines">
                <span style={{ ["--d" as string]: "0ms" }}>
                  <b className="prompt">$</b> homelens explain --review
                </span>
                <span style={{ ["--d" as string]: "90ms" }}>
                  <u>model</u> {result.model.name}
                </span>
                <span style={{ ["--d" as string]: "180ms" }}>
                  <u>p(risk)</u> {result.risk_probability != null ? `${result.risk_probability.toFixed(4)}  ${att ? "≥" : "<"}  ${result.operating_threshold?.toFixed(3)}` : "n/a (model unavailable)"}
                </span>
                <span style={{ ["--d" as string]: "270ms" }}>
                  <u>decision</u> <em className={att ? "hot" : "calm-text"}>{att == null ? "DICTIONARY SIGNALS ONLY" : att ? "MANAGEMENT ATTENTION" : "ROUTINE MONITORING"}</em>
                </span>
                <span style={{ ["--d" as string]: "360ms" }}>
                  <u>primary</u> {result.detected_aspects.length ? shortAspect(result.primary_aspect) : "No dictionary match"}
                </span>
                <span style={{ ["--d" as string]: "450ms" }}>
                  <u>signals</u> {result.detected_aspects.map(shortAspect).join(" · ") || "—"}
                </span>
                <span style={{ ["--d" as string]: "540ms" }}>
                  <b className="prompt">▸</b> evidence sentence{evidence ? ` #${evidence.index + 1}` : ""}
                </span>
              </pre>

              {evidence ? (
                <div className="viscous">
                  <div className="viscous-fill" aria-hidden="true" />
                  <blockquote className="dm-evidence">
                    <span className="evidence-text">{withPhrases(evidence.sentence, { matched_phrases: evidence.phrases })}</span>
                    <footer>
                      {evidence.match ? <b>{shortAspect(evidence.aspect)}</b> : att ? <b>no dictionary match — manual review</b> : <b>no complaint signal — highest-scoring sentence shown</b>}
                      {evidence.p != null && <span> · sentence risk {evidence.p.toFixed(2)}</span>}
                    </footer>
                  </blockquote>
                </div>
              ) : (
                <p className="term-empty">No sentence to show.</p>
              )}

              <div className="term-actions">
                <button
                  className="btn ghost"
                  disabled={!result.weights}
                  onClick={() => {
                    setWeights((w) => !w);
                    setDrop((d) => d + 1);
                  }}
                  aria-expanded={weights}
                >
                  {weights ? "Hide Model Weights" : "View Model Weights"}
                </button>
                <button className="btn" onClick={() => onFlag(result)} aria-pressed={flagged} disabled={att === false || (att == null && !result.detected_aspects.length)} title={att === false ? "Below the management-attention threshold — routine monitoring" : undefined}>
                  {att === false ? "No risk flag to triage" : flagged ? "Flag selected · see triage ↘" : "Select risk flag → triage"}
                </button>
              </div>
              <p className="dm-rec">
                <b>Recommended action.</b> {result.recommended_action}
              </p>
            </div>
          )}
        </div>
      </div>

      {/* --------------------------------------------------- weights waterfall */}
      <div className="weights" data-open={weights && !!result?.weights} aria-hidden={!weights}>
        <div className="weights-in">
          {result?.weights && weights && (
            <div className="pool" key={drop}>
              <div className="pool-head">
                <span className="kicker">What moved the score</span>
                <span className="tiny">
                  Top terms by logit contribution in the served {result.model.name} model (TF-IDF value × coefficient; the total uses every term). Red pills raise risk; blue pills lower it.
                  DistilBERT is not deployed in this API.
                </span>
              </div>
              <div className="pills-fall">
                {result.weights.terms.map((t, i) => (
                  <span key={t.term} className={`wpill ${t.weight > 0 ? "up" : "down"}`} style={{ ["--i" as string]: i, ["--w" as string]: 0.34 + 0.66 * (Math.abs(t.weight) / maxW) }}>
                    <b>{t.label}</b>
                    <em>
                      {t.weight > 0 ? "+" : "−"}
                      {Math.abs(t.weight).toFixed(2)}
                    </em>
                  </span>
                ))}
                <span className="wpill base" style={{ ["--i" as string]: result.weights.terms.length, ["--w" as string]: 0.5 }}>
                  <b>bias</b>
                  <em>{result.weights.bias.toFixed(2)}</em>
                </span>
                <span className="wpill total" style={{ ["--i" as string]: result.weights.terms.length + 1, ["--w" as string]: 0.75 }}>
                  <b>Σ logit → p</b>
                  <em>
                    {result.weights.logit.toFixed(2)} → {result.risk_probability?.toFixed(3)}
                  </em>
                </span>
              </div>
            </div>
          )}
        </div>
      </div>
    </Glass>
  );
}
