"""macOS Keychain storage for Garmin OAuth tokens using garth.dumps()/loads()."""

import subprocess

SERVICE = "pacerai"


def _account(user: str) -> str:
    return f"garmin:{user}"


def save(user: str, token_blob: str):
    """Store a garth.dumps() blob in the keychain (creates or updates)."""
    subprocess.run(
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
    result = subprocess.run(
        [
            "security", "find-generic-password",
            "-a", _account(user),
            "-s", SERVICE,
            "-w",
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    blob = result.stdout.strip()
    return blob or None


def delete(user: str):
    """Remove tokens from keychain (silent if not present)."""
    subprocess.run(
        [
            "security", "delete-generic-password",
            "-a", _account(user),
            "-s", SERVICE,
        ],
        capture_output=True,
    )


def exists(user: str) -> bool:
    result = subprocess.run(
        [
            "security", "find-generic-password",
            "-a", _account(user),
            "-s", SERVICE,
        ],
        capture_output=True,
    )
    return result.returncode == 0
