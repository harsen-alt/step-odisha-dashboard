#!/usr/bin/env python3
"""
Builds data/schools.json from a raw CSV export of the "S&ME School" tab
in the "STEP Odisha_Program Management Sheet: 2026-27" Google Sheet.

Manual refresh workflow (use this if you don't have the automated sync set
up, or want to force a one-off refresh from a fresh export):
  1. Open the sheet, click into the "S&ME School" tab.
  2. File -> Download -> Comma Separated Values (.csv), while that tab is active.
  3. Save/overwrite it at data/raw/sme_school.csv (or pass a path as argv[1]).
  4. Run: python3 scripts/build_data.py [path/to/export.csv] [snapshot-date YYYY-MM-DD]
  5. Commit the regenerated data/schools.json (and the raw CSV, for reproducibility).

For the automated, no-manual-steps path, see fetch_and_build.py and
.github/workflows/sync-data.yml instead — this script is the fallback.
"""
import csv
import sys
from pathlib import Path

from dashboard_data import build_from_records

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SRC = REPO_ROOT / "data" / "raw" / "sme_school.csv"


if __name__ == "__main__":
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SRC
    snapshot = sys.argv[2] if len(sys.argv) > 2 else "unknown"
    if not src.exists():
        sys.exit(f"CSV not found: {src}\nExport the 'S&ME School' tab as CSV first (see script docstring).")
    with open(src, encoding="utf-8-sig", newline="") as f:
        records = list(csv.DictReader(f))
    print(f"Read {len(records)} rows from {src}")
    build_from_records(records, snapshot)
