-- Pacerai facts + coaching sync schema.
-- Run this once in the Supabase SQL editor (Project → SQL Editor → New query).
-- PostgREST (the API pacerai talks to) cannot run DDL, so this step is manual.
-- Safe to re-run: table creates are IF NOT EXISTS; RLS statements are idempotent.

create table if not exists garmin_facts (
  id bigint generated always as identity primary key,
  user_name text not null,
  fact_date date not null,
  source text not null,              -- 'activity' | 'sleep' | 'hrv' | 'stats' | 'body_battery' | 'training_status'
  source_id text not null default '', -- e.g. Garmin activityId; '' for daily aggregates (never NULL — needed for upsert dedup)
  metric_key text not null,          -- e.g. 'distance_km', 'avg_hr', 'sleep_score'
  metric_value double precision,
  metric_text text,
  metadata jsonb,
  synced_at timestamptz not null default now(),
  unique (user_name, fact_date, source, source_id, metric_key)
);
create index if not exists idx_garmin_facts_user_date on garmin_facts (user_name, fact_date);

create table if not exists coaching_notes (
  id bigint generated always as identity primary key,
  user_name text not null,
  note_date date not null,           -- date this note is written for/about
  period_start date,
  period_end date,
  title text,
  body text not null,
  tags text[],
  generated_by text not null default 'claude-interactive',  -- 'claude-interactive' | 'claude-api' | 'manual'
  model text,
  status text not null default 'final',                     -- 'draft' | 'final'
  created_at timestamptz not null default now()
);
create index if not exists idx_coaching_notes_user_date on coaching_notes (user_name, note_date);

-- Health data (sleep, HRV, weight, body fat, coaching notes) must never be
-- world-readable via the anon key. RLS with no policies denies anon and
-- authenticated; the CLI uses SUPABASE_SERVICE_KEY (service_role), which
-- bypasses RLS. Re-run this file on existing projects to lock tables down.
alter table garmin_facts enable row level security;
alter table coaching_notes enable row level security;

revoke all on table garmin_facts from anon, authenticated, public;
revoke all on table coaching_notes from anon, authenticated, public;
grant all on table garmin_facts to service_role;
grant all on table coaching_notes to service_role;
