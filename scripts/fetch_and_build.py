#!/usr/bin/env python3
"""
Automated path for the live-sync GitHub Action: fetches the "S&ME School" tab
directly (using a read-only service account) and regenerates data/schools.json.
No manual export step, no local file needed.

Fetches by the tab's numeric sheetId (gid) via the CSV export endpoint rather
than by name through the Sheets API's values.get A1-range parser — that parser
rejects ranges whose (quoted) sheet name contains "&", which "S&ME School"
does, always failing with "Unable to parse range" regardless of credentials
or sharing. Looking the gid up by title first sidesteps that entirely.

Requires:
  - env GOOGLE_SERVICE_ACCOUNT_JSON: the full service-account key JSON (as a
    string), shared as a repo secret. The service account must have been
    granted view access to the spreadsheet itself (Share -> paste its
    ...@...iam.gserviceaccount.com address -> Viewer).
  - env SPREADSHEET_ID (optional): defaults to the STEP Odisha sheet's ID.

Run manually with: GOOGLE_SERVICE_ACCOUNT_JSON="$(cat key.json)" python3 scripts/fetch_and_build.py
See .github/workflows/sync-data.yml for the scheduled, hands-off version.
"""
import csv
import io
import json
import os
import sys
from datetime import datetime, timezone

from dashboard_data import build_from_records

DEFAULT_SPREADSHEET_ID = "1o3BduTM-sLqjqWaA7emzkmhqBq2jFCDWpJo7Khay0vU"
SHEET_NAME = "S&ME School"
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]


def fetch_records():
    from google.auth.transport.requests import AuthorizedSession
    from google.oauth2 import service_account
    from googleapiclient.discovery import build

    key_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    if not key_json:
        sys.exit("GOOGLE_SERVICE_ACCOUNT_JSON is not set — see this script's docstring.")
    spreadsheet_id = os.environ.get("SPREADSHEET_ID", DEFAULT_SPREADSHEET_ID)

    info = json.loads(key_json)
    creds = service_account.Credentials.from_service_account_info(info, scopes=SCOPES)

    service = build("sheets", "v4", credentials=creds, cache_discovery=False)
    meta = service.spreadsheets().get(
        spreadsheetId=spreadsheet_id, fields="sheets.properties"
    ).execute()
    sheets = [s["properties"] for s in meta.get("sheets", [])]
    match = next((s for s in sheets if s.get("title") == SHEET_NAME), None)
    if match is None:
        available = ", ".join(repr(s.get("title")) for s in sheets)
        sys.exit(f"No tab named {SHEET_NAME!r} in this spreadsheet. Available tabs: {available}")
    gid = match["sheetId"]

    export_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=csv&gid={gid}"
    session = AuthorizedSession(creds)
    resp = session.get(export_url)
    resp.raise_for_status()
    text = resp.content.decode("utf-8-sig")
    records = list(csv.DictReader(io.StringIO(text)))
    if not records:
        sys.exit(f"No data returned for the {SHEET_NAME!r} tab (gid {gid}) — check the tab name and sharing.")
    return records


def main():
    records = fetch_records()
    print(f"Fetched {len(records)} rows from the '{SHEET_NAME}' tab via CSV export")
    snapshot_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    build_from_records(records, snapshot_date)


if __name__ == "__main__":
    main()
