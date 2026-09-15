-- Additive lockdown for projects that already ran an older schema.sql.
-- Paste into the Supabase SQL editor. Does not drop or alter columns.

alter table garmin_facts enable row level security;
alter table coaching_notes enable row level security;

revoke all on table garmin_facts from anon, authenticated, public;
revoke all on table coaching_notes from anon, authenticated, public;
grant all on table garmin_facts to service_role;
grant all on table coaching_notes to service_role;
