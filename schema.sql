-- Fascial Fibrosis Tracker — Supabase schema
-- Same project as BD dashboard (mwdjhinpicvxjetrcvkc), new table, RLS enabled.
-- Run this in the Supabase SQL editor.

create table if not exists fascial_fibrosis_entries (
    id bigint generated always as identity primary key,
    entry_type text not null check (entry_type in ('company', 'trial', 'alert', 'digest_note')),
    -- company fields
    company_name text,
    company_status text,           -- e.g. "Preclinical", "Phase 1", "Watch"
    company_summary text,
    company_source_url text,
    -- trial fields
    nct_id text,
    trial_title text,
    trial_status text,             -- RECRUITING / NOT_YET_RECRUITING / etc
    trial_phase text,
    trial_sponsor text,
    trial_location text,
    trial_condition text,          -- Dupuytren / Peyronie / Ledderhose / etc
    trial_is_startup_drug boolean default false,  -- true = high-priority per Julian's ask
    trial_url text,
    -- shared
    headline text not null,        -- one-line summary shown on the dashboard card
    detail text,                   -- longer body / notes
    first_seen_at timestamptz not null default now(),
    last_updated_at timestamptz not null default now(),
    is_new boolean default true,   -- true until acknowledged/viewed, drives the "NEW" badge
    source_run text                -- which cron job / run produced this (monthly-digest / trial-alert / manual)
);

create index if not exists idx_ff_entry_type on fascial_fibrosis_entries (entry_type);
create index if not exists idx_ff_nct_id on fascial_fibrosis_entries (nct_id);
create unique index if not exists idx_ff_nct_id_unique on fascial_fibrosis_entries (nct_id) where nct_id is not null;

alter table fascial_fibrosis_entries enable row level security;

-- Read: anyone with anon key can read (dashboard is a single-user tool, low sensitivity —
-- personal medical research interest, not PHI/PII). Mirrors bd_signals RLS pattern.
create policy "allow_read_ff_entries" on fascial_fibrosis_entries
    for select using (true);

-- Write: service-role key only (used by cron jobs / Tre, never the browser page).
create policy "allow_service_write_ff_entries" on fascial_fibrosis_entries
    for all using (auth.role() = 'service_role');
