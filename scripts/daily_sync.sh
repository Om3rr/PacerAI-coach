#!/usr/bin/env bash
# Runs the daily Garmin -> Supabase facts sync, then (only if something looks
# worth noting) a headless Claude session that writes a coaching note.
#
# Designed to run "once per calendar day, whenever the machine is next
# awake" via launchd — not a fixed clock time. Safe to invoke more than once
# a day (e.g. launchd firing on both a missed schedule and login): the
# Supabase last-synced check makes any extra run a no-op.
#
# launchd runs jobs with a minimal environment, so PATH is set explicitly
# rather than relying on the interactive shell's PATH.
set -euo pipefail

export PATH="/opt/homebrew/bin:$HOME/.local/bin:/usr/local/bin:$PATH"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

USER_NAME="${PACERAI_USER:-omer}"
LOG_PREFIX="[daily_sync $(date -u +%Y-%m-%dT%H:%M:%SZ)]"

echo "$LOG_PREFIX starting for user=$USER_NAME"

json_field() {
    # reads pacerai's {"status":"ok","data":{...}} from stdin, prints data[$1]
    python3 -c "import json,sys; d=json.load(sys.stdin)['data']; print(d.get('$1'))"
}

LAST_SYNCED=$(poetry run pacerai --user "$USER_NAME" last-synced | json_field last_fact_date)
TODAY=$(date +%F)

if [ "$LAST_SYNCED" = "$TODAY" ]; then
    echo "$LOG_PREFIX already synced today ($TODAY). Skipping."
    exit 0
fi

if [ "$LAST_SYNCED" = "None" ]; then
    DAYS=14
else
    GAP=$(python3 -c "
from datetime import date
last = date.fromisoformat('$LAST_SYNCED')
today = date.fromisoformat('$TODAY')
print(max(1, min((today - last).days, 14)))
")
    DAYS=$GAP
fi

echo "$LOG_PREFIX syncing facts, days=$DAYS"
poetry run pacerai --user "$USER_NAME" sync-facts --days "$DAYS"

echo "$LOG_PREFIX invoking headless Claude for coaching notes"
claude -p "$(sed "s/{{USER}}/$USER_NAME/g" "$SCRIPT_DIR/daily_coaching_prompt.md")" \
    --allowedTools "Bash(poetry run pacerai *)" \
    || echo "$LOG_PREFIX headless Claude run failed or produced nothing — facts are still synced."

echo "$LOG_PREFIX done"
