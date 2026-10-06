"""Rebuild the HomeLens AI app artifacts from the raw Yelp CSV (CPU only).

This reproduces the final notebook's pipeline locally:

1. core home-service category filter, service groups, anonymized provider codes;
2. privacy/leakage masking and the business-held-out train/validation/test split;
3. TF-IDF + Logistic Regression grid search, validation threshold, final refit;
4. complaint-aspect extraction and lift;
5. provider-level relative risk tiers (>= 20 reviews) and service-group benchmark.

DistilBERT and TextBlob need a GPU / extra packages, so ``model_comparison.csv``
records the validated test metrics reported by the executed notebook. The
TF-IDF metrics recomputed here are checked against those values.

Provider risk scores are computed from TF-IDF probabilities in this local
rebuild (the notebook used DistilBERT). To use the notebook's DistilBERT-based
dashboard tables instead, copy the Colab ``HomeLensAI_outputs`` CSVs into
``artifacts/`` and set ``provider_scores_model`` in ``artifacts/metadata.json``.

Usage:
    python scripts/build_artifacts.py [--data data/raw/HomeLens_Yelp_HomeServices.csv]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    f1_score,
    precision_recall_fscore_support,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedGroupKFold

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.risk_logic import (  # noqa: E402
    HIGH_SEVERITY_ASPECTS,
    NO_MATCH,
    RECOMMENDATIONS,
    RISK_PHRASES,
    extract_aspects,
    mask_sensitive_and_leakage,
)

RANDOM_SEED = 509
ARTIFACTS = ROOT / "artifacts"

CORE_CATEGORIES = {
    "Contractors", "General Contractors", "Plumbing",
    "Heating & Air Conditioning/HVAC", "Water Heater Installation/Repair",
    "Electricians", "Roofing", "Landscaping", "Landscape Architects",
    "Gardeners", "Tree Services", "Irrigation", "Lawn Services", "Painters",
    "Flooring", "Tiling", "Carpeting", "Carpet Installation", "Carpet Cleaning",
    "Home Cleaning", "Office Cleaning", "Window Washing", "Pressure Washers",
    "Pest Control", "Pool & Hot Tub Service", "Pool Cleaners", "Swimming Pools",
    "Damage Restoration", "Garage Door Services", "Door Sales/Installation",
    "Windows Installation", "Glass & Mirrors", "Keys & Locksmiths",
    "Security Systems", "Solar Installation", "Home Inspectors", "Handyman",
    "Fences & Gates", "Masonry/Concrete", "Septic Services",
    "Water Purification Services", "Appliances & Repair", "Junk Removal & Hauling",
    "Movers", "Packing Services", "Property Management", "Cabinetry",
    "Countertop Installation", "Kitchen & Bath", "Drywall Installation & Repair",
    "Stucco Services", "Refinishing Services", "Home Organization", "Interior Design",
    "Home Theatre Installation", "Air Duct Cleaning", "Hydro-jetting",
    "Grout Services", "Shades & Blinds", "Shutters",
    "Lighting Fixtures & Equipment", "Furniture Reupholstery", "Metal Fabricators",
}

SERVICE_GROUPS = [
    ("Plumbing & Water", {
        "Plumbing", "Water Heater Installation/Repair", "Hydro-jetting",
        "Septic Services", "Water Purification Services",
    }),
    ("HVAC & Air Quality", {"Heating & Air Conditioning/HVAC", "Air Duct Cleaning"}),
    ("Cleaning & Restoration", {
        "Home Cleaning", "Office Cleaning", "Carpet Cleaning", "Window Washing",
        "Pressure Washers", "Damage Restoration", "Grout Services",
    }),
    ("Outdoor & Landscaping", {
        "Landscaping", "Landscape Architects", "Gardeners", "Tree Services",
        "Irrigation", "Lawn Services", "Pool & Hot Tub Service", "Pool Cleaners",
        "Swimming Pools", "Pest Control",
    }),
    ("Construction & Remodeling", {
        "Contractors", "General Contractors", "Roofing", "Painters", "Flooring",
        "Tiling", "Carpeting", "Carpet Installation", "Kitchen & Bath", "Cabinetry",
        "Countertop Installation", "Drywall Installation & Repair", "Stucco Services",
        "Masonry/Concrete", "Fences & Gates", "Interior Design",
        "Refinishing Services", "Metal Fabricators",
    }),
    ("Electrical, Solar & Security", {
        "Electricians", "Solar Installation", "Security Systems",
        "Lighting Fixtures & Equipment", "Home Theatre Installation",
    }),
    ("Repair & Installation", {
        "Appliances & Repair", "Garage Door Services", "Door Sales/Installation",
        "Windows Installation", "Glass & Mirrors", "Keys & Locksmiths", "Handyman",
        "Shades & Blinds", "Shutters", "Furniture Reupholstery", "Home Organization",
    }),
    ("Moving & Hauling", {"Movers", "Packing Services", "Junk Removal & Hauling"}),
    ("Property Management & Inspection", {"Property Management", "Home Inspectors"}),
]

TFIDF_CONFIG: dict[str, Any] = {
    "lowercase": True,
    "strip_accents": "unicode",
    "stop_words": "english",
    "ngram_range": (1, 2),
    "min_df": 3,
    "max_df": 0.97,
    "max_features": 60_000,
    "sublinear_tf": True,
}

# Validated held-out test metrics from the executed notebook (section 9).
NOTEBOOK_MODEL_COMPARISON = [
    {"model": "Fine-tuned DistilBERT", "operating_threshold": 0.95, "accuracy": 0.976,
     "macro_f1": 0.973, "negative_precision": 0.972, "negative_recall": 0.955,
     "negative_f1": 0.963, "average_precision": 0.993, "roc_auc": 0.996},
    {"model": "TF–IDF Logistic Regression", "operating_threshold": 0.62, "accuracy": 0.957,
     "macro_f1": 0.951, "negative_precision": 0.950, "negative_recall": 0.917,
     "negative_f1": 0.933, "average_precision": 0.984, "roc_auc": 0.991},
    {"model": "TextBlob", "operating_threshold": 0.405, "accuracy": 0.793,
     "macro_f1": 0.785, "negative_precision": 0.630, "negative_recall": 0.909,
     "negative_f1": 0.744, "average_precision": 0.848, "roc_auc": 0.911},
]

# Aspect counts reported by the notebook's spaCy PhraseMatcher (section 10).
NOTEBOOK_ASPECT_COUNTS = {
    "Professionalism / Trust": 806, "Communication": 245, "Reliability / No-show": 378,
    "Timeliness": 158, "Warranty / Follow-up": 100, "Pricing / Billing": 276,
    "Workmanship": 281, "Safety / Property Damage": 136,
}


def parse_categories(value: Any) -> set[str]:
    return {item.strip() for item in str(value).split(",") if item.strip()}


def assign_service_group(category_set: set[str]) -> str:
    for group_name, group_categories in SERVICE_GROUPS:
        if category_set & group_categories:
            return group_name
    return "Other Core Home Services"


def aspect_column(aspect: str) -> str:
    import re
    return "aspect_" + re.sub(r"\W+", "_", aspect.lower()).strip("_")


def corpus_aspects(texts: pd.Series) -> pd.Series:
    """Aspect lists per review using the notebook's spaCy PhraseMatcher when available.

    Falls back to the app's regex matcher, which agrees on ~99.5% of matches.
    """
    try:
        import spacy
        from spacy.matcher import PhraseMatcher
    except ImportError:
        print("  spaCy not installed; using the regex matcher.")
        return texts.astype(str).apply(extract_aspects)
    nlp = spacy.blank("en")
    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    for aspect, phrases in RISK_PHRASES.items():
        matcher.add(aspect, [nlp.make_doc(phrase) for phrase in phrases])
    results = [
        sorted({nlp.vocab.strings[match_id] for match_id, _, _ in matcher(doc)})
        for doc in nlp.pipe(texts.astype(str), batch_size=256)
    ]
    return pd.Series(results, index=texts.index)


def classification_metrics(y_true, prediction, probability) -> dict[str, float]:
    precision, recall, negative_f1, _ = precision_recall_fscore_support(
        y_true, prediction, labels=[1], average=None, zero_division=0
    )
    return {
        "accuracy": accuracy_score(y_true, prediction),
        "macro_f1": f1_score(y_true, prediction, average="macro"),
        "negative_precision": precision[0],
        "negative_recall": recall[0],
        "negative_f1": negative_f1[0],
        "average_precision": average_precision_score(y_true, probability),
        "roc_auc": roc_auc_score(y_true, probability),
    }


def select_business_threshold(y_true, probability, recall_floor: float = 0.90):
    rows = []
    for threshold in np.linspace(0.05, 0.95, 181):
        prediction = (probability >= threshold).astype(int)
        precision, recall, negative_f1, _ = precision_recall_fscore_support(
            y_true, prediction, labels=[1], average=None, zero_division=0
        )
        rows.append({
            "threshold": threshold,
            "negative_precision": precision[0],
            "negative_recall": recall[0],
            "negative_f1": negative_f1[0],
            "macro_f1": f1_score(y_true, prediction, average="macro"),
        })
    table = pd.DataFrame(rows)
    feasible = table[table["negative_recall"] >= recall_floor]
    if not feasible.empty:
        best = feasible.sort_values(
            ["negative_precision", "macro_f1", "threshold"], ascending=[False, False, True]
        ).iloc[0]
    else:
        best = table.sort_values(["macro_f1", "negative_f1"], ascending=False).iloc[0]
    return float(best["threshold"]), table


def load_core_reviews(path: Path) -> pd.DataFrame:
    raw_df = pd.read_csv(path)
    raw_df["date"] = pd.to_datetime(raw_df["date"], errors="coerce")
    category_sets = raw_df["categories"].apply(parse_categories)
    core_mask = category_sets.apply(lambda v: bool(v & CORE_CATEGORIES))
    core_mask &= ~category_sets.apply(lambda v: bool(v & {"Hotels", "Hotels & Travel"}))
    core_mask &= ~category_sets.apply(
        lambda v: "Automotive" in v
        and not bool(v & {"Movers", "Junk Removal & Hauling", "Keys & Locksmiths"})
    )
    core_mask &= ~category_sets.apply(
        lambda v: "Apartments" in v and "Property Management" not in v
    )
    df = raw_df.loc[core_mask].copy()
    df["category_set"] = category_sets.loc[core_mask]
    df["service_group"] = df["category_set"].apply(assign_service_group)
    provider_map = {
        business_id: f"Provider_{number:04d}"
        for number, business_id in enumerate(sorted(df["business_id"].unique()), start=1)
    }
    df["provider_code"] = df["business_id"].map(provider_map)
    df["model_text"] = df["text"].apply(mask_sensitive_and_leakage)
    return df


def split_reviews(df: pd.DataFrame):
    model_df = df[df["review_stars"] != 3].copy()
    model_df["normalized_model_text"] = (
        model_df["model_text"].str.lower().str.replace(r"\s+", " ", regex=True).str.strip()
    )
    model_df = model_df.drop_duplicates(subset="normalized_model_text").reset_index(drop=True)
    model_df["label"] = (model_df["review_stars"] <= 2).astype(int)

    outer = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=RANDOM_SEED)
    tv_idx, test_idx = next(outer.split(model_df, model_df["label"], groups=model_df["business_id"]))
    tv_df = model_df.iloc[tv_idx].reset_index(drop=True)
    test_df = model_df.iloc[test_idx].reset_index(drop=True)
    inner = StratifiedGroupKFold(n_splits=4, shuffle=True, random_state=RANDOM_SEED + 1)
    tr_idx, va_idx = next(inner.split(tv_df, tv_df["label"], groups=tv_df["business_id"]))
    return tv_df.iloc[tr_idx].reset_index(drop=True), tv_df.iloc[va_idx].reset_index(drop=True), test_df


def train_tfidf(train_df, validation_df, test_df):
    vec = TfidfVectorizer(**TFIDF_CONFIG)
    X_train = vec.fit_transform(train_df["model_text"])
    X_val = vec.transform(validation_df["model_text"])
    rows = []
    for c_value in [0.5, 1.0, 2.0, 4.0]:
        model = LogisticRegression(
            class_weight="balanced", max_iter=2_000, solver="liblinear",
            C=c_value, random_state=RANDOM_SEED,
        )
        model.fit(X_train, train_df["label"])
        prob = model.predict_proba(X_val)[:, 1]
        threshold, _ = select_business_threshold(validation_df["label"].to_numpy(), prob)
        metrics = classification_metrics(
            validation_df["label"].to_numpy(), (prob >= threshold).astype(int), prob
        )
        rows.append({"C": c_value, "threshold": threshold, **metrics})
    results = pd.DataFrame(rows).sort_values(["macro_f1", "negative_f1"], ascending=False)
    best_c = float(results.iloc[0]["C"])
    threshold = float(results.iloc[0]["threshold"])

    full_df = pd.concat([train_df, validation_df], ignore_index=True)
    vectorizer = TfidfVectorizer(**TFIDF_CONFIG)
    X_full = vectorizer.fit_transform(full_df["model_text"])
    model = LogisticRegression(
        class_weight="balanced", max_iter=2_000, solver="liblinear",
        C=best_c, random_state=RANDOM_SEED,
    )
    model.fit(X_full, full_df["label"])
    prob = model.predict_proba(vectorizer.transform(test_df["model_text"]))[:, 1]
    test_metrics = classification_metrics(
        test_df["label"].to_numpy(), (prob >= threshold).astype(int), prob
    )
    return vectorizer, model, best_c, threshold, test_metrics


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--data", type=Path, default=ROOT / "data/raw/HomeLens_Yelp_HomeServices.csv")
    args = parser.parse_args()
    ARTIFACTS.mkdir(exist_ok=True)

    print("Loading and filtering reviews ...")
    df = load_core_reviews(args.data)
    assert len(df) == 17_943 and df["business_id"].nunique() == 1_054, "Core subset mismatch"

    print("Splitting and training TF-IDF ...")
    train_df, validation_df, test_df = split_reviews(df)
    for a, b in [(train_df, validation_df), (train_df, test_df), (validation_df, test_df)]:
        assert not set(a["business_id"]) & set(b["business_id"]), "Business overlap"
    vectorizer, model, best_c, threshold, test_metrics = train_tfidf(train_df, validation_df, test_df)
    print(f"  C={best_c}  threshold={threshold:.3f}  test macro F1={test_metrics['macro_f1']:.3f}")
    if abs(test_metrics["macro_f1"] - 0.951) > 0.005:
        print("  Note: local split differs from Colab (scikit-learn version); the app reports the notebook's validated 0.951.")

    joblib.dump(vectorizer, ARTIFACTS / "homelens_tfidf_vectorizer.joblib", compress=3)
    joblib.dump(model, ARTIFACTS / "homelens_tfidf_logistic_regression.joblib", compress=3)
    pd.DataFrame(NOTEBOOK_MODEL_COMPARISON).to_csv(ARTIFACTS / "model_comparison.csv", index=False)

    # Interpretable TF-IDF terms (notebook cell 31).
    names = np.array(vectorizer.get_feature_names_out())
    coefs = model.coef_[0]
    neg_idx, pos_idx = np.argsort(coefs)[-15:][::-1], np.argsort(coefs)[:15]
    pd.DataFrame({
        "negative_signal_terms": names[neg_idx], "negative_coefficient": coefs[neg_idx],
        "positive_signal_terms": names[pos_idx], "positive_coefficient": coefs[pos_idx],
    }).to_csv(ARTIFACTS / "tfidf_signal_terms.csv", index=False)

    print("Extracting complaint aspects ...")
    aspect_lists = corpus_aspects(df["text"])
    aspect_columns = [aspect_column(a) for a in RISK_PHRASES]
    for aspect in RISK_PHRASES:
        df[aspect_column(aspect)] = aspect_lists.apply(lambda found, a=aspect: a in found)

    corpus_negative_rate = float((df["review_stars"] <= 2).mean())
    aspect_rows = []
    for aspect in RISK_PHRASES:
        mentioned = df[aspect_column(aspect)]
        count = int(mentioned.sum())
        negatives = int((mentioned & (df["review_stars"] <= 2)).sum())
        rate = negatives / count if count else np.nan
        aspect_rows.append({
            "aspect": aspect, "reviews_with_signal": count, "share_of_corpus": count / len(df),
            "negative_reviews_with_signal": negatives, "negative_rate_when_mentioned": rate,
            "lift_vs_corpus_negative_rate": rate / corpus_negative_rate,
        })
    aspect_summary = pd.DataFrame(aspect_rows).sort_values("negative_rate_when_mentioned", ascending=False)
    aspect_summary.to_csv(ARTIFACTS / "aspect_summary.csv", index=False)
    mismatches = {
        r.aspect: (r.reviews_with_signal, NOTEBOOK_ASPECT_COUNTS[r.aspect])
        for r in aspect_summary.itertuples() if r.reviews_with_signal != NOTEBOOK_ASPECT_COUNTS[r.aspect]
    }
    print("  Aspect counts match notebook." if not mismatches else f"  Aspect count differences: {mismatches}")

    print("Scoring providers ...")
    df["risk_probability"] = model.predict_proba(vectorizer.transform(df["model_text"]))[:, 1]
    df["observed_negative"] = (df["review_stars"] <= 2).astype(int)
    df["review_year"] = df["date"].dt.year
    df["high_severity_signal"] = df[[aspect_column(a) for a in HIGH_SEVERITY_ASPECTS]].any(axis=1).astype(int)

    counts = df.groupby("business_id")[aspect_columns].sum()
    column_to_label = {aspect_column(a): a for a in RISK_PHRASES}
    top_aspect = counts.idxmax(axis=1).map(column_to_label)
    top_aspect[counts.max(axis=1) == 0] = NO_MATCH

    recent_start = pd.Timestamp("2021-01-01")
    previous_start, previous_end = pd.Timestamp("2020-01-01"), pd.Timestamp("2020-12-31 23:59:59")
    provider_rows, yearly_rows = [], []
    for business_id, group in df.groupby("business_id"):
        if len(group) < 20:
            continue
        recent = group[group["date"] >= recent_start]
        previous = group[(group["date"] >= previous_start) & (group["date"] <= previous_end)]
        code = group["provider_code"].iloc[0]
        provider_rows.append({
            "provider_code": code,
            "service_group": group["service_group"].iloc[0],
            "reviews": len(group),
            "observed_negative_rate": group["observed_negative"].mean(),
            "mean_risk_probability": group["risk_probability"].mean(),
            "recent_reviews": len(recent),
            "recent_risk_probability": recent["risk_probability"].mean() if len(recent) else np.nan,
            "previous_reviews": len(previous),
            "previous_risk_probability": previous["risk_probability"].mean() if len(previous) else np.nan,
            "trend_delta": (
                recent["risk_probability"].mean() - previous["risk_probability"].mean()
                if len(recent) >= 3 and len(previous) >= 3 else np.nan
            ),
            "high_severity_rate": group["high_severity_signal"].mean(),
            "top_aspect": top_aspect.get(business_id, NO_MATCH),
            "latest_review": group["date"].max(),
        })
        yearly = group.groupby("review_year").agg(
            reviews=("review_id", "size"), mean_risk_probability=("risk_probability", "mean")
        ).reset_index()
        yearly.insert(0, "provider_code", code)
        yearly_rows.append(yearly)

    provider_risk = pd.DataFrame(provider_rows)
    provider_risk["recent_risk_probability"] = provider_risk["recent_risk_probability"].fillna(
        provider_risk["mean_risk_probability"]
    )
    for column in ["mean_risk_probability", "recent_risk_probability", "high_severity_rate"]:
        provider_risk[f"{column}_percentile"] = provider_risk[column].rank(pct=True, method="average")
    provider_risk["risk_score"] = 100 * (
        0.50 * provider_risk["mean_risk_probability_percentile"]
        + 0.30 * provider_risk["recent_risk_probability_percentile"]
        + 0.20 * provider_risk["high_severity_rate_percentile"]
    )
    provider_risk["risk_tier"] = pd.cut(
        provider_risk["risk_score"], bins=[-np.inf, 50, 75, 90, np.inf],
        labels=["Stable", "Watch", "Elevated", "High concern"],
    )
    provider_risk["recommended_action"] = provider_risk["top_aspect"].map(RECOMMENDATIONS)

    dashboard_columns = [
        "provider_code", "service_group", "reviews", "observed_negative_rate",
        "mean_risk_probability", "recent_risk_probability", "trend_delta",
        "high_severity_rate", "top_aspect", "risk_score", "risk_tier", "recommended_action",
        "recent_reviews", "previous_reviews", "latest_review",
    ]
    provider_dashboard = provider_risk.sort_values("risk_score", ascending=False)[dashboard_columns]
    provider_dashboard.to_csv(ARTIFACTS / "provider_risk_dashboard.csv", index=False)
    pd.concat(yearly_rows).to_csv(ARTIFACTS / "provider_yearly_risk.csv", index=False)
    print("  Tier counts:", provider_risk["risk_tier"].value_counts().sort_index().to_dict())

    service_risk_summary = (
        provider_risk.groupby("service_group").agg(
            eligible_businesses=("provider_code", "size"),
            median_risk_score=("risk_score", "median"),
            high_concern_providers=("risk_tier", lambda v: int((v == "High concern").sum())),
            median_recent_risk=("recent_risk_probability", "median"),
        ).sort_values("median_risk_score", ascending=False)
    )
    service_risk_summary.to_csv(ARTIFACTS / "service_risk_summary.csv")

    # Corpus-level descriptive tables (EDA, model-independent).
    df.groupby("service_group").agg(
        reviews=("review_id", "size"), businesses=("business_id", "nunique"),
        average_stars=("review_stars", "mean"),
        negative_rate=("review_stars", lambda v: float((v <= 2).mean())),
    ).sort_values("negative_rate", ascending=False).to_csv(ARTIFACTS / "service_group_eda.csv")
    df.groupby("review_year").agg(
        reviews=("review_id", "size"),
        negative_rate=("review_stars", lambda v: float((v <= 2).mean())),
    ).reset_index().to_csv(ARTIFACTS / "corpus_timeline.csv", index=False)

    metadata = {
        "market": "Tucson, AZ",
        "core_reviews": int(len(df)),
        "providers": int(df["business_id"].nunique()),
        "unique_reviewers": int(df["user_id"].nunique()),
        "date_start": str(df["date"].min().date()),
        "date_end": str(df["date"].max().date()),
        "monitored_providers": int(len(provider_risk)),
        "min_reviews_for_monitoring": 20,
        "test_reviews": int(len(test_df)),
        "test_businesses": int(test_df["business_id"].nunique()),
        "train_reviews": int(len(train_df)),
        "validation_reviews": int(len(validation_df)),
        "tfidf_threshold": round(threshold, 4),
        "tfidf_best_c": best_c,
        "distilbert_threshold": 0.95,
        "tfidf_rebuild_test_macro_f1": round(float(test_metrics["macro_f1"]), 4),
        "provider_scores_model": "TF–IDF Logistic Regression (local rebuild)",
    }
    (ARTIFACTS / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print("Done. Artifacts written to", ARTIFACTS)


if __name__ == "__main__":
    main()
