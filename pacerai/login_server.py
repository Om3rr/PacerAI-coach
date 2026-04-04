"""
Local web login server for Garmin Connect authentication.

Opens a browser form → handles password + optional OTP → saves tokens to macOS Keychain.

Usage:
    poetry run pacerai login [--user omer|yuval|rami]
"""

import http.server
import json
import os
import socket
import sys
import threading
import urllib.parse
import webbrowser
from html import escape

from pacerai import keychain
from pacerai.auth import USERS, _encode_blob
from garminconnect import Garmin

# ─── State (single-session, so module-level is fine) ──────────────────────────

_state = {
    "status": "pending",   # pending | awaiting_mfa | done | error
    "error": None,
    "garmin": None,
    "client_state": None,
}
_shutdown_event = threading.Event()
_user: str = "omer"


# ─── HTML pages ───────────────────────────────────────────────────────────────

_CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, sans-serif;
  background: #f0f2f5; min-height: 100vh;
  display: flex; align-items: center; justify-content: center;
}
.card {
  background: #fff; border-radius: 14px; padding: 44px 40px;
  width: 100%; max-width: 400px;
  box-shadow: 0 4px 32px rgba(0,0,0,0.09);
}
.logo { text-align: center; margin-bottom: 32px; }
.logo h1 { font-size: 22px; color: #111; font-weight: 700; letter-spacing: -0.5px; }
.logo p  { color: #888; font-size: 13px; margin-top: 5px; }
.badge {
  background: #f6f8fa; border: 1px solid #e4e7eb; border-radius: 8px;
  padding: 11px 15px; margin-bottom: 26px;
  font-size: 13px; color: #555;
}
.badge strong { color: #111; }
.field { margin-bottom: 18px; }
label { display: block; font-size: 13px; font-weight: 500; color: #333; margin-bottom: 6px; }
input[type=password], input[type=text] {
  width: 100%; padding: 11px 14px;
  border: 1.5px solid #dde1e7; border-radius: 9px;
  font-size: 14px; outline: none; transition: border-color .15s;
  background: #fafbfc;
}
input:focus { border-color: #1DB954; background: #fff; }
.hint { font-size: 12px; color: #999; margin-top: 5px; }
button {
  width: 100%; padding: 13px; background: #1DB954; color: #fff;
  border: none; border-radius: 9px; font-size: 15px; font-weight: 600;
  cursor: pointer; margin-top: 8px; transition: background .15s;
}
button:hover  { background: #17a348; }
button:active { background: #148f3e; }
.error {
  background: #fff5f5; border: 1px solid #ffd0d0; color: #c53030;
  padding: 12px 14px; border-radius: 9px; margin-bottom: 20px; font-size: 13px;
}
.success {
  background: #f0fff4; border: 1px solid #9ae6b4; color: #276749;
  padding: 16px; border-radius: 9px; text-align: center; font-size: 14px;
}
.success h2 { font-size: 20px; margin-bottom: 8px; }
"""

def _page(body: str, extra_head: str = "") -> bytes:
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Garmin Login — Pacerai</title>
  <style>{_CSS}</style>
  {extra_head}
</head>
<body><div class="card">{body}</div></body>
</html>"""
    return html.encode()


def _login_page(error: str = None, prefill_email: str = "") -> bytes:
    cfg = USERS.get(_user)
    known_email = cfg["email"] if cfg else ""
    err_html = f'<div class="error">{escape(error)}</div>' if error else ""

    if known_email:
        # Known user — email is fixed, just ask for password
        email_field = f'<div class="badge">Logging in as <strong>{_user}</strong> · {escape(known_email)}</div>'
        email_input = f'<input type="hidden" name="email" value="{escape(known_email)}">'
    else:
        # New user — show email field
        email_field = f'<div class="badge">New profile: <strong>{_user}</strong></div>'
        email_input = f"""
          <div class="field">
            <label>Garmin Connect Email</label>
            <input type="text" name="email" autofocus placeholder="you@example.com"
                   value="{escape(prefill_email)}" required>
          </div>
        """

    autofocus = "" if not known_email else " autofocus"
    return _page(f"""
      <div class="logo">
        <h1>Pacerai</h1>
        <p>Sign in to Garmin Connect</p>
      </div>
      {email_field}
      {err_html}
      <form method="POST" action="/login">
        {email_input}
        <div class="field">
          <label>Password</label>
          <input type="password" name="password"{autofocus} placeholder="Garmin Connect password" required>
        </div>
        <button type="submit">Sign In</button>
      </form>
    """)


def _otp_page(error: str = None) -> bytes:
    err_html = f'<div class="error">{escape(error)}</div>' if error else ""
    return _page(f"""
      <div class="logo">
        <h1>Two-Factor Auth</h1>
        <p>Check your email or authenticator app</p>
      </div>
      {err_html}
      <form method="POST" action="/otp">
        <div class="field">
          <label>One-Time Code</label>
          <input type="text" name="otp" autofocus placeholder="6-digit code"
                 inputmode="numeric" pattern="[0-9]{{4,8}}" maxlength="8" required>
          <div class="hint">Sent to your email or generated by your authenticator app</div>
        </div>
        <button type="submit">Verify</button>
      </form>
    """)


def _success_page() -> bytes:
    return _page(
        """
        <div class="logo"><h1>Pacerai</h1></div>
        <div class="success">
          <h2>Logged in!</h2>
          <p>Tokens saved to macOS Keychain.<br>You can close this tab.</p>
        </div>
        """,
        extra_head='<script>setTimeout(()=>window.close(),2500)</script>',
    )


# ─── Request handler ──────────────────────────────────────────────────────────

class _Handler(http.server.BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        pass  # suppress request logs

    def _send(self, body: bytes, status: int = 200):
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _redirect(self, path: str):
        self.send_response(302)
        self.send_header("Location", path)
        self.end_headers()

    def _parse_post(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length).decode()
        return {k: v[0] for k, v in urllib.parse.parse_qs(raw).items()}

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        if path in ("/", "/login"):
            self._send(_login_page())
        elif path == "/otp":
            if _state["status"] != "awaiting_mfa":
                self._redirect("/login")
            else:
                self._send(_otp_page())
        elif path == "/success":
            self._send(_success_page())
            threading.Thread(target=_shutdown_event.set, daemon=True).start()
        else:
            self._send(b"Not found", 404)

    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path

        if path == "/login":
            data = self._parse_post()
            password = data.get("password", "")
            cfg = USERS.get(_user)
            email = cfg["email"] if cfg else data.get("email", "").strip()
            if not email:
                self._send(_login_page(error="Email is required."))
                return
            try:
                g = Garmin(email, password, return_on_mfa=True)
                g.garth.sess.headers.update({
                    "User-Agent": (
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/131.0.0.0 Safari/537.36"
                    )
                })
                result, client_state = g.login()
                if result == "needs_mfa":
                    _state["status"] = "awaiting_mfa"
                    _state["garmin"] = g
                    _state["client_state"] = client_state
                    self._redirect("/otp")
                else:
                    _finalise(g)
                    self._redirect("/success")
            except Exception as e:
                msg = str(e)
                if "422" in msg:
                    msg = "Garmin returned 422 — try again in a few minutes. If it persists, check that you can log in at connect.garmin.com and accept any pending terms."
                elif "429" in msg:
                    msg = "Garmin is rate-limiting login attempts. Wait 5–10 minutes and try again."
                elif "invalid" in msg.lower() or "incorrect" in msg.lower() or "401" in msg:
                    msg = "Incorrect email or password. Please try again."
                self._send(_login_page(error=msg, prefill_email=email))

        elif path == "/otp":
            if _state["status"] != "awaiting_mfa":
                self._redirect("/login")
                return
            data = self._parse_post()
            otp = data.get("otp", "").strip()
            try:
                g = _state["garmin"]
                g.resume_login(client_state=_state["client_state"], mfa_code=otp)
                _finalise(g)
                self._redirect("/success")
            except Exception as e:
                msg = str(e)
                if "invalid" in msg.lower() or "incorrect" in msg.lower():
                    msg = "Invalid code. Please try again."
                self._send(_otp_page(error=msg))

        else:
            self._send(b"Not found", 404)


def _finalise(g: Garmin):
    """Save tokens + display_name to keychain and mark state as done."""
    # Fetch display_name (needed by garminconnect for most endpoints)
    try:
        prof = g.garth.connectapi("/userprofile-service/userprofile/profile")
        display_name = prof.get("displayName", "")
    except Exception:
        display_name = ""
    blob = _encode_blob(g.garth.dumps(), display_name)
    keychain.save(_user, blob)
    _state["status"] = "done"
    _state["garmin"] = g


# ─── Entry point ──────────────────────────────────────────────────────────────

def run(user: str = "omer", timeout: int = 300):
    """Start the login server, open browser, block until done or timeout."""
    global _user, _shutdown_event
    _user = user
    _shutdown_event = threading.Event()  # reset for re-use

    # Pick a free port
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]

    server = http.server.HTTPServer(("127.0.0.1", port), _Handler)
    server.timeout = 1  # allow periodic checks

    url = f"http://127.0.0.1:{port}/login"
    print(f"Opening browser: {url}")
    webbrowser.open(url)

    deadline = __import__("time").time() + timeout
    while not _shutdown_event.is_set():
        if __import__("time").time() > deadline:
            print("Login timed out.")
            break
        server.handle_request()

    server.server_close()
    return _state["status"] == "done"
