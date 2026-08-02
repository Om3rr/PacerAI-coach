"""Tests for optional Telegram notifications — network calls are mocked."""
from unittest.mock import patch, MagicMock
import pytest
from pacerai.telegram import send_message, format_coaching_note_message


class TestSendMessage:
    def test_returns_false_when_unconfigured(self):
        with patch.dict("os.environ", {}, clear=True):
            with patch("requests.post") as mock_post:
                assert send_message("hello") is False
        mock_post.assert_not_called()

    def test_returns_false_when_only_token_set(self):
        with patch.dict("os.environ", {"TELEGRAM_BOT_TOKEN": "t"}, clear=True):
            with patch("requests.post") as mock_post:
                assert send_message("hello") is False
        mock_post.assert_not_called()

    @patch.dict("os.environ", {"TELEGRAM_BOT_TOKEN": "t", "TELEGRAM_CHAT_ID": "123"})
    def test_posts_to_correct_url_and_payload(self):
        mock_resp = MagicMock()
        mock_resp.raise_for_status = lambda: None
        with patch("requests.post", return_value=mock_resp) as mock_post:
            result = send_message("hello world")
        assert result is True
        url = mock_post.call_args[0][0]
        assert url == "https://api.telegram.org/bott/sendMessage"
        payload = mock_post.call_args.kwargs["json"]
        assert payload == {"chat_id": "123", "text": "hello world"}

    @patch.dict("os.environ", {"TELEGRAM_BOT_TOKEN": "t", "TELEGRAM_CHAT_ID": "123"})
    def test_truncates_long_text(self):
        mock_resp = MagicMock()
        mock_resp.raise_for_status = lambda: None
        long_text = "x" * 5000
        with patch("requests.post", return_value=mock_resp) as mock_post:
            send_message(long_text)
        payload = mock_post.call_args.kwargs["json"]
        assert len(payload["text"]) == 4096

    @patch.dict("os.environ", {"TELEGRAM_BOT_TOKEN": "t", "TELEGRAM_CHAT_ID": "123"})
    def test_raises_on_http_error(self):
        mock_resp = MagicMock()
        mock_resp.raise_for_status.side_effect = Exception("boom")
        with patch("requests.post", return_value=mock_resp):
            with pytest.raises(Exception, match="boom"):
                send_message("hello")


class TestFormatCoachingNoteMessage:
    def test_includes_title_date_body(self):
        note = {"title": "Week check-in", "note_date": "2026-08-02", "body": "Solid week."}
        msg = format_coaching_note_message(note)
        assert "Week check-in" in msg
        assert "2026-08-02" in msg
        assert "Solid week." in msg

    def test_defaults_title_when_missing(self):
        note = {"note_date": "2026-08-02", "body": "Body text"}
        msg = format_coaching_note_message(note)
        assert "Coaching note" in msg

    def test_handles_missing_fields(self):
        msg = format_coaching_note_message({})
        assert "Coaching note" in msg
