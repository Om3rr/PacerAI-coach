# Garmin CLI (`pacerai`)

**Canonical reference (single source of truth):** `docs/garmin-cli.md`  
That file lists every command, authentication, workout JSON schema, pace decimals, scheduling, and workflows.

---

## Claude Code and Cursor

| Where | What |
|-------|------|
| **This repo** | Full CLI documentation lives in **`docs/garmin-cli.md`** only. |
| **Cursor** | Agent skill: `.cursor/skills/garmin-cli/SKILL.md` — points agents at `docs/garmin-cli.md`. |
| **Claude Code** | This slash command: `.claude/commands/garmin-cli.md` — same pointer; no duplicate long copy here. |

When the CLI changes, update **`docs/garmin-cli.md`** once. Cursor and Claude both stay aligned by reading that file.

---

## Quick reminders

```bash
poetry run pacerai <command> [--user <name>] [options]
```

- Put global **`--user`** **before** the subcommand, e.g. `poetry run pacerai --user omer login` (not `pacerai login --user omer`).
- Default profile is **omer** unless the user asks for another account.
- Tokens are stored in **macOS Keychain**; CLI output is JSON: `{"status":"ok","data":...}` or `{"status":"error","message":"..."}`.

**Next step:** open **`docs/garmin-cli.md`** for the full command list and examples.
