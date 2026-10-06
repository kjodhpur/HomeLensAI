// TypeScript mirror of the FastAPI responses (see docs/DATA_CONTRACT.md). Keep in sync with backend/app/artifacts.py and scoring.py.

export type Tier = "Stable" | "Watch" | "Elevated" | "High concern";
export type Trend = "Rising" | "Steady" | "Improving" | "Insufficient data";

export interface HistoryPoint {
  year: number;
  reviews: number;
  risk: number;
}

export interface Provider {
  code: string; // anonymized: Provider_XXXX
  service_group: string;
  reviews: number;
  observed_negative_rate: number;
  mean_risk: number;
  recent_risk: number | null;
  trend_delta: number | null;
  trend: Trend;
  high_severity_rate: number;
  top_aspect: string;
  risk_score: number;
  risk_tier: Tier;
  recommended_action: string;
  recent_reviews: number;
  previous_reviews: number;
  latest_review: string | null;
  history: HistoryPoint[];
}

export interface SeriesPoint {
  x: number;
  y: number;
}

export interface ServiceSummary {
  service_group: string;
  monitored_providers: number;
  median_risk_score: number;
  high_concern_providers: number;
  median_recent_risk: number;
}

export interface Overview {
  meta: {
    market: string;
    date_start: string;
    date_end: string;
    core_reviews: number;
    providers: number;
    monitored_providers: number;
    min_reviews: number;
    provider_scores_model: string | null;
  };
  kpis: {
    reviews_analyzed: { value: number; series: SeriesPoint[]; providers: number; unique_reviewers: number };
    sentiment_shift: {
      shift: { from_year: number; to_year: number; from_rate: number; to_rate: number; delta_pts: number } | null;
      series: SeriesPoint[];
    };
    escalations: { value: number; elevated: number; monitored: number; series: SeriesPoint[]; codes: string[] };
  };
  tiers: Record<Tier, number>;
  tier_rules: Record<Tier, string>;
  services: ServiceSummary[];
  models: { model: string; operating_threshold: number; macro_f1: number; negative_recall: number; negative_precision: number }[];
}

export interface Aspect {
  aspect: string;
  reviews_with_signal: number;
  share_of_corpus: number;
  negative_reviews_with_signal: number;
  negative_rate_when_mentioned: number;
  lift: number;
  high_severity: boolean;
  keywords: string[];
  recommended_action: string;
  providers_led: number;
}

export interface Example {
  id: string;
  label: string;
  kind: "complaint" | "positive";
  text: string;
}

export interface SentenceResult {
  index: number;
  start: number;
  end: number;
  text: string;
  risk_probability: number | null;
  flagged: boolean;
  aspects: string[];
  matched_phrases: Record<string, string[]>;
}

export interface AnalyzeResult {
  model: { name: string; threshold: number | null; available: boolean; is_primary: boolean; note: string };
  risk_probability: number | null;
  operating_threshold: number | null;
  management_attention: boolean | null;
  primary_aspect: string;
  detected_aspects: string[];
  matched_phrases: Record<string, string[]>;
  recommended_action: string;
  sentences: SentenceResult[];
  evidence: {
    index: number;
    sentence: string;
    aspect: string;
    matched_phrases: Record<string, string[]>;
    risk_probability: number | null;
    has_dictionary_match: boolean;
  } | null;
  weights: {
    bias: number;
    logit: number;
    terms: { term: string; label: string; weight: number }[];
    explained_positive: number;
    explained_negative: number;
  } | null;
  masking_applied: boolean;
  disclaimer: string;
}

/** What the action-triage dock is currently about. */
export type TriageContext =
  | { kind: "provider"; provider: Provider }
  | { kind: "aspect"; aspect: Aspect }
  | { kind: "review"; result: AnalyzeResult };
