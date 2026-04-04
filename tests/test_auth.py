"""Tests for auth blob encoding/decoding."""
import base64
import json
import pytest
from pacerai.auth import _encode_blob, _decode_blob


class TestEncodeBlob:
    def test_roundtrip(self):
        garth = '{"some": "token_data"}'
        display = "Omer S"
        blob = _encode_blob(garth, display)
        decoded_garth, decoded_display = _decode_blob(blob)
        assert decoded_garth == garth
        assert decoded_display == display

    def test_output_is_base64(self):
        blob = _encode_blob("tokens", "name")
        # Should not raise
        base64.b64decode(blob)

    def test_none_display_name(self):
        blob = _encode_blob("tokens", None)
        _, display = _decode_blob(blob)
        assert display is None

    def test_empty_display_name(self):
        blob = _encode_blob("tokens", "")
        garth, display = _decode_blob(blob)
        assert garth == "tokens"
        assert display == ""

    def test_encoded_contains_tokens_key(self):
        blob = _encode_blob("my_token", "Alice")
        payload = json.loads(base64.b64decode(blob))
        assert "tokens" in payload
        assert payload["tokens"] == "my_token"

    def test_encoded_contains_display_name_key(self):
        blob = _encode_blob("t", "Bob")
        payload = json.loads(base64.b64decode(blob))
        assert payload["display_name"] == "Bob"


class TestDecodeBlob:
    def test_new_format(self):
        payload = json.dumps({"tokens": "abc123", "display_name": "Yuval"})
        blob = base64.b64encode(payload.encode()).decode()
        garth, display = _decode_blob(blob)
        assert garth == "abc123"
        assert display == "Yuval"

    def test_old_format_fallback(self):
        # Old format: blob is just a raw garth token string (not JSON-wrapped)
        old_blob = "raw_garth_token_data_not_json"
        garth, display = _decode_blob(old_blob)
        assert garth == old_blob
        assert display is None

    def test_missing_display_name_key(self):
        # JSON blob but no display_name field
        payload = json.dumps({"tokens": "tok"})
        blob = base64.b64encode(payload.encode()).decode()
        garth, display = _decode_blob(blob)
        assert garth == "tok"
        assert display is None

    def test_no_tokens_key_falls_back(self):
        # Valid base64 JSON but no "tokens" key → treat as old format
        payload = json.dumps({"something_else": "value"})
        blob = base64.b64encode(payload.encode()).decode()
        garth, display = _decode_blob(blob)
        # Falls back to returning the blob as-is
        assert display is None
