#!/usr/bin/env python3
"""
Automated path for the live-sync GitHub Action: fetches the "S&ME School" tab
directly via the Google Sheets API (using a read-only service account) and
regenerates data/schools.json. No manual export step, no local file needed.

Requires:
  - env GOOGLE_SERVICE_ACCOUNT_JSON: the full service-account key JSON (as a
    string), shared as a repo secret. The service account must have been
    granted view access to the spreadsheet itself (Share -> paste its
    ...@...iam.gserviceaccount.com address -> Viewer).
  - env SPREADSHEET_ID (optional): defaults to the STEP Odisha sheet's ID.

Run manually with: GOOGLE_SERVICE_ACCOUNT_JSON="$(cat key.json)" python3 scripts/fetch_and_build.py
See .github/workflows/sync-data.yml for the scheduled, hands-off version.
"""
import json
import os
import sys
from datetime import datetime, timezone

from dashboard_data import build_from_records, rows_to_records

DEFAULT_SPREADSHEET_ID = "1o3BduTM-sLqjqWaA7emzkmhqBq2jFCDWpJo7Khay0vU"
SHEET_NAME = "S&ME School"
RANGE = f"'{SHEET_NAME}'!A1:Y100000"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


def fetch_rows():
    from google.oauth2 import service_account
    from googleapiclient.discovery import build

    key_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    if not key_json:
        sys.exit("GOOGLE_SERVICE_ACCOUNT_JSON is not set — see this script's docstring.")
    spreadsheet_id = os.environ.get("SPREADSHEET_ID", DEFAULT_SPREADSHEET_ID)

    info = json.loads(key_json)
    creds = service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
    service = build("sheets", "v4", credentials=creds, cache_discovery=False)

    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, range=RANGE
    ).execute()
    values = result.get("values", [])
    if not values:
        sys.exit(f"No data returned for range {RANGE!r} — check the tab name and sharing.")
    return values[0], values[1:]


def main():
    header, data_rows = fetch_rows()
    records = rows_to_records(header, data_rows)
    print(f"Fetched {len(records)} rows from the '{SHEET_NAME}' tab via the Sheets API")
    snapshot_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    build_from_records(records, snapshot_date)


if __name__ == "__main__":
    main()
