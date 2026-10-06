"""Generate a small SYNTHETIC review dataset that mimics the schema of the
extracted Yelp home-services file (HomeLens_Yelp_HomeServices.csv).

Why this exists
---------------
The real Yelp Open Dataset cannot be redistributed, so it is not stored in this
repository. This script writes ``data/sample/sample_reviews.csv`` so that
teammates (and CI) can run the notebook, the backend and the frontend without
the real data. Everything in the output is machine-generated: business names
are labelled "(SAMPLE)" and no real review text is used.

Usage
-----
    python scripts/make_sample_data.py            # writes data/sample/sample_reviews.csv
    python scripts/make_sample_data.py --seed 7   # different draw
"""

from __future__ import annotations

import argparse
import random
from pathlib import Path

import numpy as np
import pandas as pd

TRADES = {
    "Plumbing": "Home Services, Plumbing, Water Heater Installation/Repair",
    "Electricians": "Home Services, Electricians, Lighting Fixtures & Equipment",
    "HVAC": "Home Services, Heating & Air Conditioning/HVAC",
    "Roofing": "Home Services, Roofing, Contractors",
    "Movers": "Home Services, Movers, Packing Services",
    "General Contractors": "Home Services, Contractors, Handyman",
    "Home Cleaning": "Home Services, Home Cleaning, Carpet Cleaning",
    "Landscaping": "Home Services, Landscaping, Tree Services",
}

# Sentences that describe a *problem* in each aspect (the signal we want to detect).
NEGATIVE = {
    "workmanship": [
        "The work was sloppy and the pipe is still leaking again after they left.",
        "Shoddy workmanship, I had to hire someone else to redo the whole job.",
        "They botched the install and the finish is crooked and cracked.",
        "The repair did not fix the problem and they left a huge mess behind.",
    ],
    "reliability": [
        "They never showed up and did not even call to cancel.",
        "The crew was a no show on the day of the appointment.",
        "He left the job unfinished and never came back.",
        "After two missed appointments I gave up on them.",
    ],
    "pricing": [
        "They overcharged me and the final bill was $600 more than quoted.",
        "Hidden fees everywhere, it felt like a complete rip off.",
        "The quote doubled once they started, classic bait and switch.",
        "Price gouging after they said it was an emergency.",
    ],
    "communication": [
        "They never called back despite five voicemails.",
        "Zero communication and no response to my emails.",
        "The office ignored my messages and nobody returned my calls.",
        "Completely unresponsive once they had my deposit.",
    ],
    "timeliness": [
        "They showed up three hours late and then left early.",
        "The project took forever and was weeks behind schedule.",
        "I waited all day and the technician arrived after dark.",
        "Constant delays, they rescheduled four times.",
    ],
    "professionalism": [
        "The technician was rude and dismissive when I asked questions.",
        "Very unprofessional, he was yelling at his helper in my driveway.",
        "They left trash all over my yard and were disrespectful.",
        "Terrible attitude and a dirty truck full of garbage.",
    ],
    "warranty": [
        "They refused to honor the warranty when it broke a week later.",
        "No one would stand behind their work and they denied my claim.",
        "I asked for a refund under the guarantee and was told no.",
        "The company will not cover the repair even though it is under warranty.",
    ],
    "safety": [
        "I smelled a gas leak after they left and it was dangerous.",
        "Exposed wires and sparks from the panel, a real fire hazard.",
        "None of it was up to code and they did the work with no permit.",
        "The unlicensed crew left the roof unsafe and water came through.",
    ],
}

# Neutral / positive sentences. POSITIVE_ASPECT mentions use the same vocabulary so a
# naive keyword match would misfire - that is intentional and tests the sentiment gate.
POSITIVE = [
    "Great service from start to finish and I would recommend them to anyone.",
    "The technician was friendly, professional and explained everything clearly.",
    "They arrived on time and finished the job faster than expected.",
    "Fair price and no surprises on the final bill.",
    "Excellent communication, they called back within the hour.",
    "The work looks fantastic and they cleaned up completely.",
    "They honored the warranty without any hassle which I really appreciated.",
    "Very safe and careful, everything was done to code and permitted.",
    "Quick response, quality work and a very reasonable estimate.",
    "I will definitely use them again for the next project.",
]
POSITIVE_ASPECT_MENTION = [
    "They were not late at all, which was a nice change.",
    "No hidden fees, the quote matched the invoice exactly.",
    "They gave a lifetime warranty on the parts.",
    "He stayed on schedule and kept me updated by text.",
]
NEUTRAL = [
    "We called them after seeing the listing online.",
    "It was a two story house in the foothills.",
    "The estimate visit took about thirty minutes.",
    "We have lived here for about six years.",
    "The appointment was scheduled for a Tuesday morning.",
]
MIXED = [
    "The work itself was decent but the communication could have been better.",
    "Good crew overall, although the price was a bit higher than I expected.",
    "They were a little late but the quality of the repair was good.",
]


def _provider_table(rng: random.Random, n_providers: int) -> pd.DataFrame:
    rows = []
    trade_names = list(TRADES)
    for i in range(n_providers):
        trade = trade_names[i % len(trade_names)]
        quality = rng.choice([0.9, 0.8, 0.75, 0.6, 0.45])  # latent P(good review)
        # A third of providers have 1-2 chronic problems; some are getting worse over time.
        problems = rng.sample(list(NEGATIVE), k=rng.choice([0, 1, 2])) if quality < 0.8 else []
        rows.append(
            {
                "business_id": f"sample_biz_{i:03d}",
                "business_name": f"{trade.split()[0]} Pros {i:03d} (SAMPLE)",
                "categories": TRADES[trade],
                "trade_group": trade,
                "city": "Tucson",
                "state": "AZ",
                "base_quality": quality,
                "problems": problems,
                "declining": rng.random() < 0.25,
                "n_reviews": rng.choice([8, 14, 24, 30, 36, 48, 60]),
            }
        )
    return pd.DataFrame(rows)


def _compose_review(rng: random.Random, stars: int, problems: list[str]) -> str:
    sentences: list[str] = []
    if stars <= 2:
        aspects = rng.sample(problems, k=min(len(problems), 2)) if problems else []
        if not aspects or rng.random() < 0.35:
            aspects.append(rng.choice(list(NEGATIVE)))
        aspects = list(dict.fromkeys(aspects))
        sentences += [rng.choice(NEGATIVE[a]) for a in aspects]
        sentences += rng.sample(NEUTRAL, k=rng.randint(1, 2))
        if rng.random() < 0.2:
            sentences.append("Would not recommend.")
    elif stars == 3:
        sentences += rng.sample(MIXED, k=1)
        sentences += rng.sample(NEUTRAL, k=1)
        if rng.random() < 0.5:
            sentences.append(rng.choice(NEGATIVE[rng.choice(list(NEGATIVE))]))
        else:
            sentences.append(rng.choice(POSITIVE))
    else:
        sentences += rng.sample(POSITIVE, k=rng.randint(1, 3))
        sentences += rng.sample(NEUTRAL, k=rng.randint(0, 2))
        if rng.random() < 0.25:
            sentences.append(rng.choice(POSITIVE_ASPECT_MENTION))
    rng.shuffle(sentences)
    return " ".join(sentences)


LABEL_NOISE = 0.08  # share of reviews whose text disagrees with their star rating (sarcasm, mis-clicks, polite complaints)


def generate(seed: int = 42, n_providers: int = 40) -> pd.DataFrame:
    rng = random.Random(seed)
    np_rng = np.random.default_rng(seed)
    providers = _provider_table(rng, n_providers)
    end = pd.Timestamp("2022-01-19")
    start = pd.Timestamp("2015-01-01")
    span_days = (end - start).days

    out = []
    rid = 0
    for p in providers.itertuples():
        # Skew dates toward recent years like real Yelp data.
        offsets = np.sort(np.clip(np_rng.beta(2.2, 1.0, p.n_reviews), 0, 1) * span_days).astype(int)
        for off in offsets:
            date = start + pd.Timedelta(days=int(off))
            recent = (end - date).days <= 730
            quality = p.base_quality - (0.3 if (p.declining and recent) else 0.0)
            quality = max(quality, 0.1)
            if rng.random() < quality:
                stars = rng.choices([5, 4, 3], weights=[0.65, 0.28, 0.07])[0]
            else:
                stars = rng.choices([1, 2, 3], weights=[0.55, 0.3, 0.15])[0]
            text_stars = stars
            if stars != 3 and rng.random() < LABEL_NOISE:
                text_stars = 5 if stars <= 2 else 1
            text = _compose_review(rng, text_stars, p.problems)
            out.append(
                {
                    "review_id": f"sample_rev_{rid:05d}",
                    "business_id": p.business_id,
                    "business_name": p.business_name,
                    "categories": p.categories,
                    "city": p.city,
                    "state": p.state,
                    "review_stars": stars,
                    "date": date.strftime("%Y-%m-%d %H:%M:%S"),
                    "text": text,
                    "useful": int(np_rng.poisson(1.0)),
                    "funny": int(np_rng.poisson(0.2)),
                    "cool": int(np_rng.poisson(0.3)),
                }
            )
            rid += 1
    df = pd.DataFrame(out)
    biz = df.groupby("business_id")["review_stars"].agg(["mean", "size"])
    df["business_stars"] = df["business_id"].map((biz["mean"] * 2).round() / 2)
    df["business_review_count"] = df["business_id"].map(biz["size"])
    return df.sample(frac=1.0, random_state=seed).reset_index(drop=True)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--providers", type=int, default=40)
    ap.add_argument("--out", type=Path, default=Path(__file__).resolve().parents[1] / "data" / "sample" / "sample_reviews.csv")
    args = ap.parse_args()
    df = generate(args.seed, args.providers)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out, index=False)
    print(f"wrote {len(df):,} synthetic reviews for {df.business_id.nunique()} providers -> {args.out}")
    print(df.review_stars.value_counts().sort_index().to_string())


if __name__ == "__main__":
    main()
