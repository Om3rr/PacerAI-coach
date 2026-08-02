"""Optional Telegram notification when a coaching note is pushed.

Purely mechanical (no AI) — mirrors the facts/interpretation split: writing
the note is the meaningful act, this just announces it. Configured via
TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID; silently disabled if either is unset
so it's never a hard requirement for push-coaching-note to work.
"""
import os

import requests
from dotenv import load_dotenv

load_dotenv()

_MAX_LEN = 4096  # Telegram's message length limit


def send_message(text: str) -> bool:
    """Send a Telegram message. Returns False (no-op) if not configured."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return False
    resp = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={"chat_id": chat_id, "text": text[:_MAX_LEN]},
        timeout=10,
    )
    resp.raise_for_status()
    return True


def format_coaching_note_message(note: dict) -> str:
    title = note.get("title") or "Coaching note"
    date = note.get("note_date") or ""
    body = note.get("body") or ""
    return f"🏃 Pacerai — {title}\n{date}\n\n{body}"
