"""macOS Keychain storage for Garmin OAuth tokens using garth.dumps()/loads().

The `security` binary only exists on macOS. On any other platform (e.g. a
GitHub Actions Ubuntu runner) these functions are no-ops — auth.py falls
back to an env-var token instead. See _env_token_var() in pacerai/auth.py.
"""

import subprocess

SERVICE = "pacerai"


def _account(user: str) -> str:
    return f"garmin:{user}"


def _run(args: list, **kwargs) -> subprocess.CompletedProcess | None:
    try:
        return subprocess.run(args, **kwargs)
    except FileNotFoundError:
        return None


def save(user: str, token_blob: str):
    """Store a garth.dumps() blob in the keychain (creates or updates)."""
    _run(
        [
            "security", "add-generic-password",
            "-U",                   # update if already exists
            "-a", _account(user),
            "-s", SERVICE,
            "-w", token_blob,
        ],
        check=True,
        capture_output=True,
    )


def load(user: str) -> str | None:
    """Return the garth.dumps() blob from keychain, or None if not found."""
    result = _run(
        [
            "security", "find-generic-password",
            "-a", _account(user),
            "-s", SERVICE,
            "-w",
        ],
        capture_output=True,
        text=True,
    )
    if result is None or result.returncode != 0:
        return None
    blob = result.stdout.strip()
    return blob or None


def delete(user: str):
    """Remove tokens from keychain (silent if not present)."""
    _run(
        [
            "security", "delete-generic-password",
            "-a", _account(user),
            "-s", SERVICE,
        ],
        capture_output=True,
    )


def exists(user: str) -> bool:
    result = _run(
        [
            "security", "find-generic-password",
            "-a", _account(user),
            "-s", SERVICE,
        ],
        capture_output=True,
    )
    return result is not None and result.returncode == 0
