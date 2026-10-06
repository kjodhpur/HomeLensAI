// TypeScript mirror of docs/DATA_CONTRACT.md. Keep in sync with the notebook's Section 9 export.

export type Tier = "High" | "Medium" | "Low" | "Insufficient data";
export type TrendDirection = "worsening" | "improving" | "stable" | "insufficient data";

export interface TopIssue {
  aspect: string;
  label: string;
  n_reviews: number;
  recurring: boolean;
}

/** One row of GET /api/providers */
export interface ProviderListItem {
  business_id: string;
  name: string;
  trade: string;
  city: string | null;
  state: string | null;
  eligible: boolean;
  n_reviews: number;
  avg_stars: number;
  neg_rate: number;
  risk_score: number | null;
  risk_tier: Tier;
  rank: number | null;
  safety_escalation: boolean;
  trend: TrendDirection;
  recent_neg_rate: number | null;
  prior_neg_rate: number | null;
  top_issues: TopIssue[];
}

export interface ProviderList {
  total: number;
  limit: number;
  offset: number;
  items: ProviderListItem[];
}

export interface Evidence {
  review_id: string;
  date: string;
  stars: number;
  cue: string;
  sentence: string;
}

export interface Issue {
  aspect: string;
  label: string;
  severity: number;
  n_reviews: number;
  share_of_flagged: number;
  recurring: boolean;
  evidence: Evidence[];
}

/** GET /api/providers/{id} */
export interface Provider {
  business_id: string;
  name: string;
  trade: string;
  city: string | null;
  state: string | null;
  categories: string[];
  eligible: boolean;
  n_reviews: number;
  n_flagged: number;
  avg_stars: number;
  yelp_stars: number | null;
  neg_rate: number;
  recent: { n: number; neg_rate: number | null };
  prior: { n: number; neg_rate: number | null };
  trend: { direction: TrendDirection; delta: number | null; p_value: number | null };
  risk_score: number | null;
  risk_tier: Tier;
  rank: number | null;
  safety_escalation: boolean;
  issues: Issue[];
  action_manager: string;
  action_homeowner: string;
  history: { year: number; n: number; neg_rate: number; avg_stars: number }[];
}

export interface Summary {
  meta: {
    data_mode: "sample" | "yelp";
    generated_at: string;
    reference_date: string;
    recent_months: number;
    min_reviews: number;
    n_reviews: number;
    n_providers_total: number;
    n_providers_eligible: number;
    disclaimer: string;
  };
  dataset: { n_reviews: number; n_providers: number; date_min: string; date_max: string; star_distribution: Record<string, number> };
  tiers: Record<string, number>;
  trend_counts: Record<string, number>;
  models: Record<string, string | number | null>[];
  aspects: { key: string; label: string; severity: number; description: string; share_in_risk_reviews: number; share_in_satisfied_reviews: number; flagged_reviews: number }[];
  trades: { trade: string; providers: number; reviews: number; risk_rate: number }[];
}

export interface AnalyzeSignal {
  aspect: string;
  label: string;
  tier: string;
  cue: string;
  sentence: string;
  sentence_compound: number;
  complaint: boolean;
}

export interface AnalyzeResult {
  text_compound: number;
  negative_sentiment: boolean;
  aspects: string[];
  signals: AnalyzeSignal[];
  mode: string;
  note: string;
  disclaimer: string;
}
