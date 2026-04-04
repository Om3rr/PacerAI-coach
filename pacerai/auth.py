import base64
import json
import os
from pathlib import Path

from garminconnect import Garmin
from pacerai import keychain

# Load user profiles from users.json (gitignored — contains personal emails).
# Falls back to empty dict; unknown users can still log in via `pacerai login`.
_USERS_FILE = Path(__file__).parent.parent / "users.json"
USERS: dict = {}
if _USERS_FILE.exists():
    with open(_USERS_FILE) as f:
        _raw = json.load(f)
    # Resolve token_store paths relative to the project root (legacy field, optional)
    for _name, _cfg in _raw.items():
        cfg = dict(_cfg)
        if "token_store" in cfg:
            cfg["token_store"] = os.path.abspath(
                _USERS_FILE.parent / cfg["token_store"]
            )
        USERS[_name] = cfg


def _encode_blob(garth_blob: str, display_name: str) -> str:
    """Pack garth token blob + display_name into a single keychain string."""
    payload = json.dumps({"tokens": garth_blob, "display_name": display_name})
    return base64.b64encode(payload.encode()).decode()


def _decode_blob(blob: str) -> tuple[str, str | None]:
    """Return (garth_blob, display_name). Falls back gracefully for old blobs."""
    try:
        payload = json.loads(base64.b64decode(blob))
        if "tokens" in payload:
            return payload["tokens"], payload.get("display_name")
    except Exception:
        pass
    # Old format: bare garth blob
    return blob, None


def get_garmin_client(user: str = "omer") -> Garmin:
    # 1. Try macOS Keychain — primary auth path
    blob = keychain.load(user)
    if blob:
        try:
            garth_blob, display_name = _decode_blob(blob)
            g = Garmin()
            g.garth.loads(garth_blob)
            if display_name:
                g.display_name = display_name
            else:
                # Missing display_name (old blob) — fetch once and re-save
                prof = g.garth.connectapi("/userprofile-service/userprofile/profile")
                g.display_name = prof.get("displayName")
                keychain.save(user, _encode_blob(garth_blob, g.display_name))
            print(f"[{user}] Logged in via Keychain")
            return g
        except Exception:
            keychain.delete(user)

    # 2. Fall back to file-based tokens (legacy migration path, known users only)
    cfg = USERS.get(user)
    if cfg and "token_store" in cfg:
        token_store = cfg["token_store"]
        try:
            g = Garmin()
            g.login(tokenstore=token_store)  # sets g.display_name
            new_blob = _encode_blob(g.garth.dumps(), g.display_name or "")
            keychain.save(user, new_blob)
            print(f"[{user}] Logged in via saved tokens (migrated to Keychain)")
            return g
        except Exception:
            pass

    raise RuntimeError(
        f"No valid tokens for '{user}'. "
        f"Run: poetry run pacerai --user {user} login"
    )
