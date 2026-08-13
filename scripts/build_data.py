#!/usr/bin/env python3
"""
Builds data/schools.json from a raw CSV export of the "S&ME School" tab
in the "STEP Odisha_Program Management Sheet: 2026-27" Google Sheet.

Refresh workflow:
  1. Open the sheet, click into the "S&ME School" tab.
  2. File -> Download -> Comma Separated Values (.csv), while that tab is active.
  3. Save/overwrite it at data/raw/sme_school.csv (or pass a path as argv[1]).
  4. Run: python3 scripts/build_data.py [path/to/export.csv] [snapshot-date YYYY-MM-DD]
  5. Commit the regenerated data/schools.json (and the raw CSV, for reproducibility).

Filter rule: a school is included if its class range (Class From..Class To)
overlaps Grade 6-8, i.e. Class From <= 8 and Class To >= 6. Schools offering
only lower-primary grades (Class To < 6) are excluded.
"""
import csv
import json
import re
import sys
from collections import OrderedDict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SRC = REPO_ROOT / "data" / "raw" / "sme_school.csv"
OUT_PATH = REPO_ROOT / "data" / "schools.json"

CODE_SUFFIX_RE = re.compile(r"-\d+$")


def clean_name(value):
    """Strip a trailing '-<numeric code>' suffix and title-case the name."""
    stripped = CODE_SUFFIX_RE.sub("", (value or "").strip())
    return stripped.title() if stripped else stripped


def clean_location(value):
    v = (value or "").strip()
    if v.upper() == "NA" or not v:
        return 2  # unknown
    v = v.split("-")[-1].strip().lower()
    if v.startswith("urban"):
        return 1
    if v.startswith("rural"):
        return 0
    return 2


def to_int(value, default=0):
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return default


def build(src_path, snapshot_date):
    districts = OrderedDict()  # name -> index
    blocks = OrderedDict()  # name -> index
    rows = []
    total = 0
    excluded = 0
    bad_range = 0

    with open(src_path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            total += 1
            class_from = to_int(r.get("Class From"), default=None) if r.get("Class From") not in (None, "") else None
            class_to = to_int(r.get("Class To"), default=None) if r.get("Class To") not in (None, "") else None
            if class_from is None or class_to is None:
                bad_range += 1
                continue
            if not (class_from <= 8 and class_to >= 6):
                excluded += 1
                continue

            d_name = clean_name(r.get("District Name"))
            b_name = clean_name(r.get("Block Name"))
            d_idx = districts.setdefault(d_name, len(districts))
            b_idx = blocks.setdefault(b_name, len(blocks))

            rows.append([
                d_idx,
                b_idx,
                (r.get("School Name") or "").strip(),
                (r.get("Udise Code") or "").strip(),
                class_from,
                class_to,
                to_int(r.get("TOT STUDENT(1 TO 12)")),
                to_int(r.get("TOT TEACHER")),
                to_int(r.get("UPS TOT")),
                clean_location(r.get("School Location")),
            ])

    qualifying = len(rows)
    out = {
        "meta": {
            "source": '"S&ME School" tab — STEP Odisha_Program Management Sheet: 2026-27',
            "snapshotDate": snapshot_date,
            "filterRule": "Class From ≤ 8 and Class To ≥ 6 (school offers Grade 6, 7, and/or 8)",
            "totalRowsInTab": total,
            "qualifying": qualifying,
            "excluded": excluded + bad_range,
            "fields": ["districtIdx", "blockIdx", "school", "udise", "classFrom", "classTo",
                       "totalStudents", "totalTeachers", "upsTotal", "location"],
            "locationCodes": {"0": "Rural", "1": "Urban", "2": "Unknown"},
        },
        "districts": list(districts.keys()),
        "blocks": list(blocks.keys()),
        "rows": rows,
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))

    print(f"Read {total} rows from {src_path}")
    print(f"Qualifying (Grade 6/7/8 available): {qualifying}")
    print(f"Excluded (no Grade 6/7/8): {excluded + bad_range}")
    print(f"Districts: {len(districts)}  Blocks: {len(blocks)}")
    print(f"Wrote {OUT_PATH} ({OUT_PATH.stat().st_size:,} bytes)")


if __name__ == "__main__":
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SRC
    snapshot = sys.argv[2] if len(sys.argv) > 2 else "unknown"
    if not src.exists():
        sys.exit(f"CSV not found: {src}\nExport the 'S&ME School' tab as CSV first (see script docstring).")
    build(src, snapshot)
