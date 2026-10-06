// Review analysis: the TypeScript equivalent of app/risk_logic.analyze_review + the per-sentence / evidence / token-weight views.
// Runs inside the Next.js app (server side) — there is no separate backend.
import type { AnalyzeResult, SentenceResult } from "@/lib/types";
import { BIAS, contributions, probability } from "./tfidf";
import { DISCLAIMER, MODEL_NAME, NO_MATCH, THRESHOLD, extractAspects, maskSensitiveAndLeakage, maskingApplied, matchedPhrases, recommendAction, sentenceSpans } from "./text";

const r4 = (x: number) => Math.round(x * 1e4) / 1e4;
const TOKEN_LABELS: Record<string, string> = {
  moneytoken: "[$ amount]", phonetoken: "[phone number]", emailtoken: "[email]", urltoken: "[link]", ratingtoken: "[star phrase]",
};

/** Probability for raw text: masking is applied first, exactly like the notebook / Streamlit scorer. */
export const scoreText = (text: string) => probability(maskSensitiveAndLeakage(text));

export function tokenWeights(text: string, top = 7): NonNullable<AnalyzeResult["weights"]> {
  const terms = contributions(maskSensitiveAndLeakage(text)).map((c) => ({ term: c.term, label: TOKEN_LABELS[c.term] ?? c.term, weight: r4(c.weight) }));
  const pos = terms.filter((t) => t.weight > 0).sort((a, b) => b.weight - a.weight).slice(0, top);
  const neg = terms.filter((t) => t.weight < 0).sort((a, b) => a.weight - b.weight).slice(0, Math.max(3, top - 3));
  const sum = (f: (t: { weight: number }) => boolean) => terms.filter(f).reduce((s, t) => s + t.weight, 0);
  return {
    bias: r4(BIAS),
    logit: r4(BIAS + terms.reduce((s, t) => s + t.weight, 0)),
    terms: [...pos, ...neg],
    explained_positive: r4(sum((t) => t.weight > 0)),
    explained_negative: r4(sum((t) => t.weight < 0)),
  };
}

export function analyzeReview(text: string): AnalyzeResult {
  if (!text.trim()) throw new Error("Review text is empty.");
  const p = scoreText(text);
  const attention = p >= THRESHOLD;
  const aspects = extractAspects(text);
  const [primary, action] = recommendAction(attention, aspects);

  const sentences: SentenceResult[] = sentenceSpans(text).map(([a, b], i) => {
    const raw = text.slice(a, b);
    const phrases = matchedPhrases(raw);
    const sp = scoreText(raw);
    return { index: i, start: a, end: b, text: raw.trim(), risk_probability: r4(sp), flagged: sp >= THRESHOLD, aspects: Object.keys(phrases).sort(), matched_phrases: phrases };
  });

  // Evidence = the sentence carrying a dictionary match (highest risk first); otherwise the riskiest sentence.
  const matched = sentences.filter((s) => s.aspects.length);
  const pool = matched.length ? matched : sentences;
  let best: SentenceResult | null = null;
  for (const s of pool) {
    const key = [s.risk_probability ?? 0, Object.keys(s.matched_phrases).length];
    const bk = best ? [best.risk_probability ?? 0, Object.keys(best.matched_phrases).length] : null;
    if (!bk || key[0] > bk[0] || (key[0] === bk[0] && key[1] > bk[1])) best = s;
  }

  return {
    model: {
      name: MODEL_NAME, threshold: THRESHOLD, available: true, is_primary: false,
      note: "Scored with the TF–IDF Logistic Regression model shipped in artifacts/ (the notebook's DistilBERT is not bundled with the web app).",
    },
    risk_probability: r4(p),
    operating_threshold: r4(THRESHOLD),
    management_attention: attention,
    primary_aspect: primary,
    detected_aspects: aspects,
    matched_phrases: matchedPhrases(text),
    recommended_action: action,
    sentences,
    evidence: best
      ? { index: best.index, sentence: best.text, aspect: best.aspects[0] ?? NO_MATCH, matched_phrases: best.matched_phrases, risk_probability: best.risk_probability, has_dictionary_match: best.aspects.length > 0 }
      : null,
    weights: tokenWeights(text),
    masking_applied: maskingApplied(text),
    disclaimer: DISCLAIMER,
  };
}
