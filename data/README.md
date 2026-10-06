# Data

The raw Yelp extract (`HomeLens_Yelp_HomeServices.csv`, ~20 MB, 23,685 reviews) lives in
`data/raw/` locally and is **git-ignored**. It contains business names and review text, so it is
never committed or deployed.

The app reads only the aggregated, anonymized tables in `artifacts/`. To regenerate them:

```bash
python scripts/build_artifacts.py --data data/raw/HomeLens_Yelp_HomeServices.csv
```
