#!/usr/bin/env python3
"""Generate a Google Calendar OAuth refresh token for the portfolio contact form.

Before running:
- Enable Google Calendar API in your Google Cloud project.
- Add this authorized redirect URI to your OAuth client:
  http://localhost:8765/oauth2callback

The script prints the refresh token once. It does not write secrets to disk.
"""

from __future__ import annotations

from getpass import getpass
from http.server import BaseHTTPRequestHandler, HTTPServer
import os
from urllib.parse import parse_qs, urlencode, urlparse
import webbrowser

import requests


HOST = "localhost"
PORT = 8765
REDIRECT_URI = f"http://{HOST}:{PORT}/oauth2callback"
SCOPES = [
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/calendar.freebusy",
]
SCOPE = " ".join(SCOPES)


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    server: "OAuthServer"

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        self.server.auth_code = params.get("code", [None])[0]
        self.server.auth_error = params.get("error", [None])[0]
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        if self.server.auth_code:
            body = "<h1>Autorisation recue</h1><p>Vous pouvez revenir au terminal.</p>"
        else:
            body = "<h1>Autorisation impossible</h1><p>Revenez au terminal pour lire l'erreur.</p>"
        self.wfile.write(body.encode("utf-8"))

    def log_message(self, format: str, *args: object) -> None:
        return


class OAuthServer(HTTPServer):
    auth_code: str | None = None
    auth_error: str | None = None


def _read_secret(name: str, *, secret: bool = False) -> str:
    value = os.getenv(name, "").strip()
    if value:
        return value
    prompt = f"{name}: "
    return (getpass(prompt) if secret else input(prompt)).strip()


def main() -> None:
    client_id = _read_secret("GOOGLE_CALENDAR_CLIENT_ID")
    client_secret = _read_secret("GOOGLE_CALENDAR_CLIENT_SECRET", secret=True)
    if not client_id or not client_secret:
        raise SystemExit("GOOGLE_CALENDAR_CLIENT_ID et GOOGLE_CALENDAR_CLIENT_SECRET sont obligatoires.")

    auth_params = {
        "client_id": client_id,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": SCOPE,
        "access_type": "offline",
        "prompt": "consent",
        "include_granted_scopes": "true",
    }
    auth_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(auth_params)
    print("\nOuverture du navigateur pour autoriser Google Calendar...")
    print(f"Redirect URI a declarer dans Google Cloud: {REDIRECT_URI}\n")
    webbrowser.open(auth_url)

    server = OAuthServer((HOST, PORT), OAuthCallbackHandler)
    server.handle_request()
    if server.auth_error:
        raise SystemExit(f"Google a renvoye une erreur OAuth: {server.auth_error}")
    if not server.auth_code:
        raise SystemExit("Aucun code OAuth recu.")

    token_response = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "code": server.auth_code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": REDIRECT_URI,
            "grant_type": "authorization_code",
        },
        timeout=30,
    )
    try:
        token_response.raise_for_status()
    except requests.HTTPError as exc:
        raise SystemExit(f"Echange du code impossible: {token_response.text}") from exc
    payload = token_response.json()
    refresh_token = payload.get("refresh_token")
    if not refresh_token:
        raise SystemExit(
            "Aucun refresh_token recu. Revoquez l'acces de l'app dans votre compte Google, "
            "puis relancez le script avec prompt=consent."
        )

    print("\nGOOGLE_CALENDAR_REFRESH_TOKEN a copier dans Streamlit secrets:\n")
    print(refresh_token)
    print("\nNe le commitez pas dans GitHub.")


if __name__ == "__main__":
    main()
