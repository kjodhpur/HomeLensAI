// TypeScript port of app/risk_logic.py (text side): privacy/leakage masking, sentence spans and the complaint-phrase dictionary.
// The patterns themselves are exported from the Python module into data/risk_config.json — they are NOT re-typed here.
import config from "@/data/risk_config.json";

const MASKS = config.masking_rules.map((r) => ({ re: new RegExp(r.source, "gi"), replacement: r.replacement }));
const ASPECT_RES: [string, RegExp][] = Object.entries(config.aspect_patterns).map(([aspect, source]) => [aspect, new RegExp(source, "gi")]);

export const NO_MATCH: string = config.no_match;
export const RECOMMENDATIONS = config.recommendations as Record<string, string>;
export const ROUTINE_MONITORING: string = config.routine_monitoring;
export const THRESHOLD: number = config.threshold;
export const MODEL_NAME: string = config.model_name;
export const DISCLAIMER: string = config.disclaimer;

const collapse = (s: string) => s.replace(/\s+/g, " ").trim();

/** Mask URLs, emails, phones, dollar amounts and explicit star phrases (mask_sensitive_and_leakage). */
export function maskSensitiveAndLeakage(text: string): string {
  let out = String(text);
  for (const { re, replacement } of MASKS) out = out.replace(re, replacement);
  return collapse(out);
}

export const maskingApplied = (text: string) => maskSensitiveAndLeakage(text) !== collapse(text);

/** Exact phrases matched per detected aspect, lower-cased and sorted (matched_phrases). */
export function matchedPhrases(text: string): Record<string, string[]> {
  const found: Record<string, string[]> = {};
  for (const [aspect, re] of ASPECT_RES) {
    const hits = [...new Set([...text.matchAll(re)].map((m) => m[0].toLowerCase()))].sort();
    if (hits.length) found[aspect] = hits;
  }
  return found;
}

export const extractAspects = (text: string): string[] => Object.keys(matchedPhrases(text)).sort();

/** Pick the primary aspect and management action (recommend_action). */
export function recommendAction(attention: boolean, aspects: string[]): [string, string] {
  const primary = aspects[0] ?? NO_MATCH;
  return [primary, attention ? (RECOMMENDATIONS[primary] ?? RECOMMENDATIONS[NO_MATCH]) : ROUTINE_MONITORING];
}

/** Character spans of the sentences in `text` (whitespace-only spans dropped, at most 40). */
export function sentenceSpans(text: string, max = 40): [number, number][] {
  const spans: [number, number][] = [];
  for (const m of text.matchAll(/[^.!?\n]+(?:[.!?]+|\n|$)/g)) {
    if (m[0].trim()) spans.push([m.index!, m.index! + m[0].length]);
  }
  return spans.slice(0, max);
}
