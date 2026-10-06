// Static data exported from Rithik's artifacts by scripts/export_frontend_data.py (see frontend/data/).
import aspectsJson from "@/data/aspects.json";
import examplesJson from "@/data/examples.json";
import factsJson from "@/data/facts.json";
import overviewJson from "@/data/overview.json";
import providersJson from "@/data/providers.json";
import type { Aspect, Example, Overview, Provider } from "./types";

export const providers = providersJson as unknown as Provider[];
export const aspects = aspectsJson as unknown as Aspect[];
export const overview = overviewJson as unknown as Overview;
export const examples = examplesJson as unknown as Example[];

/** Validated notebook facts (app/config.py NOTEBOOK_FACTS): corpus size, splits, thresholds. Never recompute these in the UI. */
export const facts = factsJson as unknown as {
  candidate_reviews: number;
  core_reviews: number;
  providers: number;
  unique_reviewers: number;
  monitored_providers: number;
  date_start: string;
  date_end: string;
  market: string;
  median_words: number;
  split: { split: string; reviews: number; businesses: number; negative_rate: number }[];
  test_negatives: number;
  test_positives: number;
  distilbert_threshold: number;
  tfidf_threshold: number;
  recall_floor: number;
};
