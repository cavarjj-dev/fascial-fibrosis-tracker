#!/usr/bin/env python3
"""
Push fascial fibrosis tracker data into Supabase (fascial_fibrosis_entries table).
Used by both the monthly digest cron and the real-time trial-alert cron so the
dashboard (index.html, GitHub Pages) and the markdown tracker never drift apart.

Uses urllib (curl is broken on this MSYS setup — see BD dashboard precedent).

Usage:
  python sync_to_supabase.py --type trial --nct-id NCT07640425 \
    --title "Safety and Efficacy Study of CNT201" --sponsor CONNEXT \
    --status RECRUITING --phase "PHASE1|PHASE2" --location "Queensland, Australia" \
    --condition Dupuytren --startup-drug --url https://clinicaltrials.gov/study/NCT07640425 \
    --headline "New Phase 1/2 trial for CNT201 collagenase, actively recruiting"

  python sync_to_supabase.py --type company --company-name "Ventoux Biosciences" \
    --company-status Preclinical --headline "Human ex vivo tissue studies underway" \
    --company-summary "VEN-201 immuno-fibrotic modulator..." \
    --url https://www.ventouxbio.com/

Requires env vars: SUPABASE_URL, SUPABASE_SERVICE_KEY
(service role key — write access, RLS-gated; never the anon key for writes)
"""
import argparse
import json
import os
import sys
import urllib.request
import urllib.error


def post_entry(payload):
    supabase_url = os.environ.get("SUPABASE_URL", "https://mwdjhinpicvxjetrcvkc.supabase.co")
    service_key = os.environ.get("SUPABASE_SERVICE_KEY")
    if not service_key:
        print("ERROR: SUPABASE_SERVICE_KEY env var not set.", file=sys.stderr)
        sys.exit(1)

    url = f"{supabase_url}/rest/v1/fascial_fibrosis_entries"
    # Upsert on nct_id when present (unique index), otherwise plain insert.
    headers = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates,return=representation",
    }
    if payload.get("nct_id"):
        url += "?on_conflict=nct_id"

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            print(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read().decode()}", file=sys.stderr)
        sys.exit(1)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--type", required=True, choices=["company", "trial", "alert", "digest_note"])
    p.add_argument("--headline", required=True)
    p.add_argument("--detail")
    p.add_argument("--source-run", default="manual")
    # trial fields
    p.add_argument("--nct-id")
    p.add_argument("--title")
    p.add_argument("--status")
    p.add_argument("--phase")
    p.add_argument("--sponsor")
    p.add_argument("--location")
    p.add_argument("--condition")
    p.add_argument("--startup-drug", action="store_true")
    p.add_argument("--url")
    # company fields
    p.add_argument("--company-name")
    p.add_argument("--company-status")
    p.add_argument("--company-summary")
    args = p.parse_args()

    payload = {
        "entry_type": args.type,
        "headline": args.headline,
        "detail": args.detail,
        "source_run": args.source_run,
        "is_new": True,
    }
    if args.type == "trial":
        payload.update({
            "nct_id": args.nct_id,
            "trial_title": args.title,
            "trial_status": args.status,
            "trial_phase": args.phase,
            "trial_sponsor": args.sponsor,
            "trial_location": args.location,
            "trial_condition": args.condition,
            "trial_is_startup_drug": bool(args.startup_drug),
            "trial_url": args.url,
        })
    elif args.type == "company":
        payload.update({
            "company_name": args.company_name,
            "company_status": args.company_status,
            "company_summary": args.company_summary,
            "company_source_url": args.url,
        })

    post_entry({k: v for k, v in payload.items() if v is not None})


if __name__ == "__main__":
    main()
