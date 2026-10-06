"""Vendor the teammate-built data layer into the API project (backend/).

The API is deployed on Vercel with Root Directory = ``backend/``, so it cannot see files outside that folder. This script copies
the single sources of truth into it:

    app/risk_logic.py      ->  backend/app/risk_logic.py        (aspect dictionary, masking, recommendations)
    artifacts/*            ->  backend/app/data/artifacts/*     (CSV tables, metadata.json, TF-IDF joblib files)

Run it after ``python scripts/build_artifacts.py`` (or after editing ``app/risk_logic.py``) and commit the result.
``backend/tests/test_api.py::test_vendored_files_match_sources`` fails if the copies drift.

    python scripts/sync_artifacts.py
"""

from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "backend" / "app"
ARTIFACT_SUFFIXES = {".csv", ".json", ".joblib"}


def main() -> None:
    shutil.copy2(ROOT / "app" / "risk_logic.py", DEST / "risk_logic.py")
    print("copied app/risk_logic.py -> backend/app/risk_logic.py")
    target = DEST / "data" / "artifacts"
    target.mkdir(parents=True, exist_ok=True)
    for stale in target.iterdir():
        if stale.is_file():
            stale.unlink()
    n = 0
    for src in sorted((ROOT / "artifacts").iterdir()):
        if src.suffix in ARTIFACT_SUFFIXES:
            shutil.copy2(src, target / src.name)
            n += 1
    print(f"copied {n} artifact files -> backend/app/data/artifacts/")


if __name__ == "__main__":
    main()
