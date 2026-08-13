"""
Shared transform: raw "S&ME School" tab records -> data/schools.json.

Used by both:
  - build_data.py        (manual path: reads a local CSV export)
  - fetch_and_build.py    (automated path: reads rows via the Sheets API)

Filter rule: a school is included if its class range (Class From..Class To)
overlaps Grade 6-8, i.e. Class From <= 8 and Class To >= 6. Schools offering
only lower-primary grades (Class To < 6) are excluded.
"""
import json
import re
from collections import OrderedDict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
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


def rows_to_records(header, data_rows):
    """Convert a header row + 2D list of row values (as returned by the Sheets
    API) into a list of dicts keyed by header name, matching csv.DictReader's
    shape. Short/ragged rows (Sheets API omits trailing empty cells) are
    padded with ''."""
    records = []
    for row in data_rows:
        padded = row + [""] * (len(header) - len(row))
        records.append(dict(zip(header, padded)))
    return records


def build_from_records(records, snapshot_date):
    """records: iterable of dicts with the "S&ME School" tab's column names.
    Returns the dict that gets written to data/schools.json (also writes it)."""
    districts = OrderedDict()  # name -> index
    blocks = OrderedDict()  # name -> index
    rows = []
    total = 0
    excluded = 0
    bad_range = 0

    for r in records:
        total += 1
        cf_raw = r.get("Class From")
        ct_raw = r.get("Class To")
        class_from = to_int(cf_raw, default=None) if cf_raw not in (None, "") else None
        class_to = to_int(ct_raw, default=None) if ct_raw not in (None, "") else None
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

    print(f"Read {total} rows")
    print(f"Qualifying (Grade 6/7/8 available): {qualifying}")
    print(f"Excluded (no Grade 6/7/8): {excluded + bad_range}")
    print(f"Districts: {len(districts)}  Blocks: {len(blocks)}")
    print(f"Wrote {OUT_PATH} ({OUT_PATH.stat().st_size:,} bytes)")
    return out
