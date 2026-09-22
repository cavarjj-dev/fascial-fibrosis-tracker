# Fascial Fibrosis Research Tracker — Dashboard

Living dashboard for tracking startup biomed companies and clinical trial
opportunities across the fascial fibromatosis family (Dupuytren's
contracture, Peyronie's disease, Ledderhose disease / plantar fibromatosis).

## Architecture

- **Source of truth (narrative):** `C:\Users\BizDev\HQ\research\fascial-fibrosis-tracker.md`
  — the full write-up with context, is maintained separately and is NOT
  auto-generated from this dashboard.
- **Source of truth (structured):** Supabase table `fascial_fibrosis_entries`
  in the same project as the BD dashboard (`mwdjhinpicvxjetrcvkc`), a
  dedicated new table — see `schema.sql`.
- **This repo:** static `index.html`, reads directly from Supabase via the
  anon (read-only) key, hosted on GitHub Pages. No build step.
- **Sync:** `sync_to_supabase.py` is called by the two cron jobs
  (monthly digest, real-time trial-alert monitor) after they update the
  markdown tracker, so the dashboard and the narrative file stay in sync.

## Setup (one-time)

1. Run `schema.sql` in the Supabase SQL editor for project `mwdjhinpicvxjetrcvkc`.
2. Get the project's anon (public) key from Supabase settings → API, paste
   it into `index.html` in place of `REPLACE_WITH_ANON_KEY`.
3. Get the service role key, set as env var `SUPABASE_SERVICE_KEY` wherever
   the cron jobs run (never commit this key, never expose it client-side).
4. Push this repo to GitHub, enable GitHub Pages on `main` branch, root.

## Cron integration

Both `Fascial Fibrosis Research Tracker (Monthly)` and
`Fascial Fibrosis Trial Alert (Real-Time)` cron jobs should call
`sync_to_supabase.py` for each new/updated company or trial they find, in
addition to updating the markdown tracker file.
