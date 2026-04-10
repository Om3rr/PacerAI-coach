import base64
import json
import os
from pathlib import Path

from garminconnect import Garmin
from pacerai import keychain

# Match login_server / Garmin web expectations so restored sessions behave like a browser.
GARMIN_BROWSER_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/131.0.0.0 Safari/537.36"
)


def _apply_garmin_browser_headers(garmin: Garmin) -> None:
    garmin.garth.sess.headers.update({"User-Agent": GARMIN_BROWSER_USER_AGENT})


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
        garth_blob, display_name = _decode_blob(blob)
        g = Garmin()
        try:
            g.garth.loads(garth_blob)
        except Exception:
            # Session blob is unusable — only case where we drop Keychain entry.
            keychain.delete(user)
        else:
            _apply_garmin_browser_headers(garmin=g)
            if display_name:
                g.display_name = display_name
            else:
                # Old blob or empty display_name from login — try once; never wipe tokens on failure.
                try:
                    prof = g.garth.connectapi("/userprofile-service/userprofile/profile")
                    g.display_name = (prof or {}).get("displayName") or ""
                    keychain.save(
                        user, _encode_blob(g.garth.dumps(), g.display_name or "")
                    )
                except Exception:
                    pass
            print(f"[{user}] Logged in via Keychain")
            return g

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
