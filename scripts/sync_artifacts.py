"""Copy the JSON artifacts written by the notebook (Section 9) into the backend.

    python scripts/sync_artifacts.py              # real data  : data/processed/*.json  -> backend/app/data/
    python scripts/sync_artifacts.py --sample     # sample data: data/sample/outputs/*.json -> backend/app/data/sample/

The backend prefers backend/app/data/<file> and falls back to backend/app/data/sample/<file>.
Real-data files are git-ignored on purpose (they contain review sentences from the Yelp Open Dataset) — see docs/DEPLOYMENT.md.
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = ("provider_risk.json", "summary.json", "aspect_lexicon.json")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sample", action="store_true", help="sync the synthetic sample outputs instead of the real ones")
    args = ap.parse_args()

    src = ROOT / "data" / ("sample/outputs" if args.sample else "processed")
    dst = ROOT / "backend" / "app" / "data" / ("sample" if args.sample else "")
    dst.mkdir(parents=True, exist_ok=True)
    missing = [f for f in FILES if not (src / f).exists()]
    if missing:
        raise SystemExit(f"Missing {missing} in {src}. Run the notebook (Section 9) first.")
    for f in FILES:
        shutil.copy2(src / f, dst / f)
        print(f"copied {(src / f).relative_to(ROOT)} -> {(dst / f).relative_to(ROOT)}")


if __name__ == "__main__":
    main()
