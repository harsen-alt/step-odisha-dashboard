# STEP Odisha — Program Management Dashboard

A static analytics dashboard summarizing the **STEP Odisha_Program Management Sheet: 2026-27** Google Sheet — a 38-tab program tracker for Mantra4Change's Project-Based Learning (PBL) program with the Odisha School & Mass Education Department, OSEPA, and SCERT.

**This repo is public** — GitHub Pages on a private repo requires a paid GitHub plan, so the repo was made public to publish it. It surfaces internal staff task-ownership and real budget figures; be aware of that before sharing the link further.

## Viewing it

Live at: https://harsen-alt.github.io/step-odisha-dashboard/

Scoped to **Academic Year 2026-27 only** — prior-year comparisons have been dropped per program-team direction, and the school count uses the sheet's **24,000-school** "1. Scope" tab figure rather than the smaller 1,184-school cascade-training count.

**Every figure is sourced only from tabs marked "Active" on the sheet's own Index tab.** Hidden tabs ("District wise no. of schools," "Program Summary-EdI," "Impact Assessment," "Impl. Timeline," "Inst. Mat.," and others) were deliberately excluded, per explicit request. Re-deriving the dashboard this way corrected two things that an earlier draft got wrong from hidden-tab data: there is **no Grade 6 content lag** (all three grades sit at an even 82.1% finalised), and Master Trainer training is scheduled for **September 2026**, not mid-August as first reported.

## What's covered

- AY2026-27 program scale (30 districts, 11 zones, 24,000 schools, 230 master trainers)
- Task status: the "Program Index" activity tracker vs. the lesson-plan content pipeline ("Project Tracker" + "Revised Project Tracker" tabs)
- Content-creation progress by grade (6-8) — verified even across all three grades, no lag
- Rollout timeline: recent deadlines, what's due, September MT/cascade training dates, and a MoM logging gap since mid-June
- **District-level school coverage** and a searchable **school explorer**, covering all 30 districts and ~17,600 individual schools state-wide that offer Grade 6, 7, and/or 8 — from the "S&ME School" tab (see below)
- AY2026-27 budget: PBL Kit total, MT training budget, and the still-unbudgeted Teacher Training (Cascading) line
- Task ownership by staff member (from Active tabs' own "Owner" columns), and a bus-factor flag
- Open risks and gaps, each tied to a specific Active tab

## A note on the school-count figure

The source sheet uses several different school-count scopes across its tabs, describing different things rather than disagreeing:

- **24,000 schools** — the "1. Scope" and "PBL Kit" tabs' state-wide target/budget figure (used for the top-line KPIs and Budget section).
- **1,184 schools** — the "Cascading (Teachers & MTs)" tab's figure for this year's actual Master Trainer and HM/teacher cascade-training deployment (used in the Budget section's basis note).
- **17,633 schools** — the district-level school coverage and school explorer sections' figure: every school in the "S&ME School" tab (17,657 schools state-wide) that offers Grade 6, 7, and/or 8 (`Class From <= 8 and Class To >= 6`). This is the full state-wide eligible-school universe, not a rollout or budget scope — by far the largest of the three figures, and not directly comparable to the other two.

## Data pipeline for the district coverage / school explorer sections

Those two sections read `data/schools.json`, a compact, dictionary-encoded extract built from a CSV export of the "S&ME School" tab. There's no live/scheduled sync (deliberately — that would require a Google service-account credential stored in this repo); refreshing it is a manual-export-plus-script step:

1. In the Google Sheet, open the **"S&ME School"** tab.
2. **File → Download → Comma Separated Values (.csv)**.
3. Save/overwrite it at `data/raw/sme_school.csv`.
4. Run `python3 scripts/build_data.py data/raw/sme_school.csv <snapshot-date>` from the repo root.
5. Commit the regenerated `data/schools.json` (and the updated raw CSV, for reproducibility).

The rest of the dashboard (task status, budget, timeline, risks, etc.) is still hand-maintained HTML, unchanged by this pipeline.

## Source

Google Sheet: "STEP Odisha_Program Management Sheet: 2026-27" (owner: subhankar.nayak@mantra4change.com). Snapshot date: 2026-08-13. Figures are roll-ups and approximations — cross-check against the live sheet before using externally.
