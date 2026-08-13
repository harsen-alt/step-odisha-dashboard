# STEP Odisha — Program Management Dashboard

A static analytics dashboard summarizing the **STEP Odisha_Program Management Sheet: 2026-27** Google Sheet — a 38-tab program tracker for Mantra4Change's Project-Based Learning (PBL) program with the Odisha School & Mass Education Department, OSEPA, and SCERT.

**This repo is public** — GitHub Pages on a private repo requires a paid GitHub plan, so the repo was made public to publish it. It surfaces internal staff task-ownership and real budget figures; be aware of that before sharing the link further.

## Viewing it

Live at: https://harsen-alt.github.io/step-odisha-dashboard/

Scoped to **Academic Year 2026-27 only** — prior-year comparisons have been dropped per program-team direction. The top-line Schools/Head Masters/Teachers KPI tiles and the PBL Kit budget line use the **17,633-school** "S&ME School" tab count (schools offering Grade 6, 7, and/or 8), in place of the sheet's own 24,000-school "1. Scope" tab figure — see the note below.

**Every figure is sourced only from tabs marked "Active" on the sheet's own Index tab.** Hidden tabs ("District wise no. of schools," "Program Summary-EdI," "Impact Assessment," "Impl. Timeline," "Inst. Mat.," and others) were deliberately excluded, per explicit request. Re-deriving the dashboard this way corrected two things that an earlier draft got wrong from hidden-tab data: there is **no Grade 6 content lag** (all three grades sit at an even 82.1% finalised), and Master Trainer training is scheduled for **September 2026**, not mid-August as first reported.

## What's covered

- AY2026-27 program scale (30 districts, 11 zones, 17,633 schools, 230 master trainers)
- Task status: the "Program Index" activity tracker vs. the lesson-plan content pipeline ("Project Tracker" + "Revised Project Tracker" tabs)
- Content-creation progress by grade (6-8) — verified even across all three grades, no lag
- Rollout timeline: recent deadlines, what's due, September MT/cascade training dates, and a MoM logging gap since mid-June
- **District-level school coverage** and a searchable **school explorer**, covering all 30 districts and ~17,600 individual schools state-wide that offer Grade 6, 7, and/or 8 — from the "S&ME School" tab (see below)
- AY2026-27 budget: PBL Kit total (recomputed on the 17,633-school count), MT training budget, and the still-unbudgeted Teacher Training (Cascading) line
- Task ownership by staff member (from Active tabs' own "Owner" columns), and a bus-factor flag
- Open risks and gaps, each tied to a specific Active tab

## A note on the school-count figure

The source sheet uses several different school-count scopes across its tabs, describing different things rather than disagreeing:

- **17,633 schools** — every school in the "S&ME School" tab (17,657 schools state-wide) that offers Grade 6, 7, and/or 8 (`Class From <= 8 and Class To >= 6`). Used for the top-line Schools/Head Masters (1/school)/Teachers (2/school) KPI tiles, the PBL Kit budget line (₹7,660/school → ₹13.51 Cr), and the district-level school coverage / school explorer sections.
- **24,000 schools** — the "1. Scope" and "PBL Kit" tabs' own state-wide target/budget figure. The sheet's own PBL Kit total against this figure is ~₹18.38 Cr; this dashboard no longer uses either number directly, but the Budget section's basis note shows both for comparison.
- **1,184 schools** — the "Cascading (Teachers & MTs)" tab's figure for this year's actual Master Trainer and HM/teacher cascade-training deployment (referenced in the Budget section's basis note).

None of these are errors — they describe different scopes (full state-wide Grade 6-8 eligibility vs. the sheet's own broader target scope vs. this year's actual cascade-training rollout).

## Live data pipeline (district coverage / school explorer / top KPI tiles / PBL Kit budget)

Those sections read `data/schools.json`, a compact, dictionary-encoded extract of the "S&ME School" tab. A scheduled GitHub Action (`.github/workflows/sync-data.yml`) re-fetches that tab roughly every 15 minutes via a read-only Google service account, rebuilds `data/schools.json`, and commits it if anything changed — which auto-redeploys the page (this repo's GitHub Pages is the "legacy" build type: any push to `main` redeploys). An open browser tab also polls `data/schools.json` every 3 minutes so it picks up a change without a manual reload — see the "Live — checked HH:MM:SS" indicator above the District-level school coverage heading.

**No polling for edits faster than that, and no push-on-edit** — this is "checks every ~15 min," not instant. That tradeoff was chosen deliberately to keep the source sheet itself completely private (the service account only has read access to this one sheet; nothing about the sheet's sharing settings changed).

### One-time setup (required before the Action will run)

The Action skips cleanly (not a failure) until this is done:

1. **Google Cloud**: create a project (or reuse one) at [console.cloud.google.com](https://console.cloud.google.com), enable the **Google Sheets API** for it (APIs & Services → Library → search "Google Sheets API" → Enable).
2. **Service account**: APIs & Services → Credentials → Create Credentials → Service Account. No IAM roles needed — access is granted via sharing the sheet directly (next step). Note its email, e.g. `something@project-id.iam.gserviceaccount.com`.
3. **Key**: open the service account → Keys → Add Key → Create new key → JSON. This downloads a `.json` file — treat it like a password.
4. **Share the sheet**: in "STEP Odisha_Program Management Sheet: 2026-27," Share → paste the service account's email → Viewer. The sheet itself stays otherwise private/unpublished.
5. **GitHub secret**: in this repo, Settings → Secrets and variables → Actions → New repository secret → name it `GOOGLE_SERVICE_ACCOUNT_JSON` → paste the entire contents of the downloaded JSON key file as the value.
6. Trigger a run once by hand (Actions tab → "Sync dashboard data from Google Sheet" → Run workflow) to confirm it succeeds, then it runs on its own from then on.

### Manual/offline fallback

`scripts/build_data.py` still works standalone if you ever need a one-off refresh without the Action (e.g. the service account is mid-setup, or you want to double-check a specific export):

1. In the Google Sheet, open the **"S&ME School"** tab.
2. **File → Download → Comma Separated Values (.csv)**.
3. Save/overwrite it at `data/raw/sme_school.csv`.
4. Run `python3 scripts/build_data.py data/raw/sme_school.csv <snapshot-date>` from the repo root.
5. Commit the regenerated `data/schools.json` (and the updated raw CSV, for reproducibility).

Both paths (the Action's `fetch_and_build.py` and the manual `build_data.py`) share the same filtering/aggregation logic in `scripts/dashboard_data.py`, so they produce identical output for the same underlying rows.

The rest of the dashboard (task status, budget line items other than PBL Kit, timeline, risks, etc.) is still hand-maintained HTML, unchanged by this pipeline.

## Source

Google Sheet: "STEP Odisha_Program Management Sheet: 2026-27" (owner: subhankar.nayak@mantra4change.com). Snapshot date: 2026-08-13. Figures are roll-ups and approximations — cross-check against the live sheet before using externally.
