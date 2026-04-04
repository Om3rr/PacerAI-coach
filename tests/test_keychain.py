"""Tests for keychain module — subprocess calls are mocked."""
from unittest.mock import patch, MagicMock
import subprocess
import pytest
from pacerai import keychain


class TestKeychainAccount:
    def test_account_format(self):
        assert keychain._account("omer") == "garmin:omer"
        assert keychain._account("yuval") == "garmin:yuval"
        assert keychain._account("rami") == "garmin:rami"


class TestKeychainSave:
    def test_calls_security_with_correct_args(self):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            keychain.save("omer", "myblob")
            args = mock_run.call_args[0][0]
            assert "security" in args
            assert "add-generic-password" in args
            assert "-U" in args
            assert "garmin:omer" in args
            assert "pacerai" in args
            assert "myblob" in args

    def test_passes_check_true(self):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            keychain.save("omer", "blob")
            kwargs = mock_run.call_args[1]
            assert kwargs.get("check") is True


class TestKeychainLoad:
    def test_returns_blob_on_success(self):
        mock_result = MagicMock(returncode=0, stdout="myblob\n")
        with patch("subprocess.run", return_value=mock_result):
            result = keychain.load("omer")
        assert result == "myblob"

    def test_returns_none_on_failure(self):
        mock_result = MagicMock(returncode=44, stdout="")
        with patch("subprocess.run", return_value=mock_result):
            result = keychain.load("omer")
        assert result is None

    def test_returns_none_on_empty_stdout(self):
        mock_result = MagicMock(returncode=0, stdout="   ")
        with patch("subprocess.run", return_value=mock_result):
            result = keychain.load("omer")
        assert result is None

    def test_calls_find_generic_password(self):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stdout="")
            keychain.load("yuval")
            args = mock_run.call_args[0][0]
            assert "find-generic-password" in args
            assert "garmin:yuval" in args


class TestKeychainDelete:
    def test_calls_delete_generic_password(self):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            keychain.delete("omer")
            args = mock_run.call_args[0][0]
            assert "delete-generic-password" in args
            assert "garmin:omer" in args

    def test_silent_on_failure(self):
        # Should not raise even if key not found
        with patch("subprocess.run", return_value=MagicMock(returncode=44)):
            keychain.delete("nonexistent")


class TestKeychainExists:
    def test_returns_true_when_found(self):
        with patch("subprocess.run", return_value=MagicMock(returncode=0)):
            assert keychain.exists("omer") is True

    def test_returns_false_when_not_found(self):
        with patch("subprocess.run", return_value=MagicMock(returncode=44)):
            assert keychain.exists("unknown") is False

    def test_calls_find_generic_password(self):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            keychain.exists("rami")
            args = mock_run.call_args[0][0]
            assert "find-generic-password" in args
            assert "garmin:rami" in args
