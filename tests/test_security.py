"""Regression tests for public-repo security controls."""
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import requests

from pacerai.cli import _redact_secrets
from pacerai.supabase_sync import (
    _eq,
    _ident,
    _table,
    _validate_supabase_url,
    last_synced_date,
    read_facts,
)
from pacerai.telegram import TelegramError, send_message

ROOT = Path(__file__).resolve().parent.parent


class TestPostgrestFilterSanitization:
    def test_eq_wraps_safe_ident(self):
        assert _eq("omer", "user") == "eq.omer"

    def test_ident_rejects_filter_injection(self):
        with pytest.raises(ValueError):
            _ident("omer,id=eq.1", "user")
        with pytest.raises(ValueError):
            _ident("omer)or(user_name.eq.x", "user")
        with pytest.raises(ValueError):
            _ident("a/b", "user")
        with pytest.raises(ValueError):
            _ident("", "user")

    def test_table_allowlist(self):
        assert _table("garmin_facts") == "garmin_facts"
        with pytest.raises(ValueError):
            _table("pg_shadow")

    @patch.dict("os.environ", {"SUPABASE_URL": "https://x.supabase.co", "SUPABASE_SERVICE_KEY": "k"})
    def test_last_synced_rejects_injected_user(self):
        with pytest.raises(ValueError, match="Invalid user"):
            last_synced_date("omer&select=*")

    @patch.dict("os.environ", {"SUPABASE_URL": "https://x.supabase.co", "SUPABASE_SERVICE_KEY": "k"})
    def test_read_facts_rejects_injected_source(self):
        with pytest.raises(ValueError, match="Invalid source"):
            read_facts("omer", "2026-01-01", "2026-01-02", source="sleep,user_name=eq.x")


class TestSupabaseUrl:
    def test_accepts_hosted_https(self):
        assert _validate_supabase_url("https://abcd.supabase.co/") == "https://abcd.supabase.co"

    def test_accepts_localhost(self):
        assert _validate_supabase_url("http://127.0.0.1:54321") == "http://127.0.0.1:54321"

    def test_rejects_http_remote_and_ssrf_targets(self):
        with pytest.raises(RuntimeError):
            _validate_supabase_url("http://abcd.supabase.co")
        with pytest.raises(RuntimeError):
            _validate_supabase_url("https://evil.example.com")
        with pytest.raises(RuntimeError):
            _validate_supabase_url("https://169.254.169.254")


class TestSecretRedaction:
    def test_redacts_telegram_bot_url(self):
        leaked = "401 for url: https://api.telegram.org/bot123456:ABC-DEF/sendMessage"
        out = _redact_secrets(leaked)
        assert "123456:ABC-DEF" not in out
        assert "<redacted>" in out

    def test_redacts_jwt(self):
        jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.e30.signature"
        assert "<redacted-jwt>" in _redact_secrets(f"token {jwt}")

    @patch.dict("os.environ", {"TELEGRAM_BOT_TOKEN": "123456:SECRET", "TELEGRAM_CHAT_ID": "1"})
    def test_telegram_http_error_omits_token(self):
        resp = MagicMock()
        resp.status_code = 401
        err = requests.HTTPError("401 Client Error for url: https://api.telegram.org/bot123456:SECRET/sendMessage")
        err.response = resp
        mock_resp = MagicMock()
        mock_resp.raise_for_status.side_effect = err
        with patch("requests.post", return_value=mock_resp):
            with pytest.raises(TelegramError) as ei:
                send_message("hi")
        assert "SECRET" not in str(ei.value)
        assert "123456" not in str(ei.value)


class TestRepoLockdowns:
    def test_schema_enables_rls(self):
        sql = (ROOT / "supabase" / "schema.sql").read_text()
        assert "enable row level security" in sql
        assert "revoke all on table garmin_facts" in sql
        assert "revoke all on table coaching_notes" in sql

    def test_daily_export_does_not_upload_health_json(self):
        yml = (ROOT / ".github" / "workflows" / "daily-export.yml").read_text()
        assert "upload-artifact" not in yml
        assert "export/sleep.json" not in yml
        assert "export/hrv.json" not in yml
        assert "permissions:" in yml
        assert "contents: read" in yml

    def test_ci_restricts_token_permissions(self):
        yml = (ROOT / ".github" / "workflows" / "ci.yml").read_text()
        assert "permissions:" in yml
        assert "contents: read" in yml

    def test_daily_sync_does_not_interpolate_into_python(self):
        script = (ROOT / "scripts" / "daily_sync.sh").read_text()
        assert "date.fromisoformat('$LAST_SYNCED')" not in script
        assert "os.environ[\"LAST_SYNCED\"]" in script
        assert "print(d.get('$1'))" not in script
