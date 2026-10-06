// TypeScript port of Rithik's scikit-learn TF-IDF + logistic-regression model (artifacts/homelens_tfidf_*.joblib).
// Vectorizer settings (asserted by scripts/export_frontend_data.py): lowercase, strip_accents="unicode", english stop words,
// word 1–2-grams, token_pattern \b\w\w+\b, sublinear_tf, idf, l2 norm. `npm test` checks parity with Python on sample reviews.
import model from "@/data/tfidf_model.json";

const STOP = new Set<string>(model.stop_words);
let vocab: Map<string, number> | null = null;
const index = () => (vocab ??= new Map(model.terms.map((t, i) => [t, i])));

/** sklearn's analyzer: lower → strip accents → tokenize → drop stop words → unigrams + bigrams. */
export function analyzeDoc(text: string): string[] {
  const lowered = text.toLowerCase().normalize("NFKD").replace(/\p{M}/gu, "");
  const tokens = (lowered.match(/[\p{L}\p{N}_]{2,}/gu) ?? []).filter((t) => !STOP.has(t));
  const grams = [...tokens];
  for (let i = 0; i < tokens.length - 1; i++) grams.push(`${tokens[i]} ${tokens[i + 1]}`);
  return grams;
}

export interface Contribution {
  term: string;
  weight: number; // tf-idf value × coefficient (exact logit contribution)
}

/** Per-term logit contributions of an (already masked) text. */
export function contributions(masked: string): Contribution[] {
  const counts = new Map<number, number>();
  const idx = index();
  for (const g of analyzeDoc(masked)) {
    const j = idx.get(g);
    if (j !== undefined) counts.set(j, (counts.get(j) ?? 0) + 1);
  }
  let norm = 0;
  const raw: [number, number][] = [];
  for (const [j, tf] of counts) {
    const x = (1 + Math.log(tf)) * model.idf[j];
    raw.push([j, x]);
    norm += x * x;
  }
  norm = Math.sqrt(norm) || 1;
  return raw.map(([j, x]) => ({ term: model.terms[j], weight: (x / norm) * model.coef[j] }));
}

export const BIAS = model.intercept;

/** Probability that a (masked) review is a risk signal. */
export function probability(masked: string): number {
  const logit = BIAS + contributions(masked).reduce((s, c) => s + c.weight, 0);
  return 1 / (1 + Math.exp(-logit));
}
