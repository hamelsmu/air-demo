"""Minimal Air + Clerk demo.

Run with:
    fastapi dev clerk_auth/main.py
Requires NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY and CLERK_SECRET_KEY env vars.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import air
import httpx
from clerk_backend_api import Clerk
from clerk_backend_api.security.types import AuthenticateRequestOptions
from fastapi import Request
from dotenv import load_dotenv

load_dotenv(Path(__file__).with_name(".env"))
PUBLISHABLE_KEY = os.getenv("NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY")
SECRET_KEY = os.getenv("CLERK_SECRET_KEY")

if not PUBLISHABLE_KEY: raise RuntimeError("NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY is not set")
if not SECRET_KEY: raise RuntimeError("CLERK_SECRET_KEY is not set")
CLERK_JS_SRC = "https://cdn.jsdelivr.net/npm/@clerk/clerk-js@5/dist/clerk.browser.js"

app = air.Air()


SIGN_IN_SCRIPT = """
document.addEventListener('DOMContentLoaded', async () => {
  if (!window.Clerk) return;

  await window.Clerk.load();

  if (window.Clerk.user) {
    window.location.assign('/');
    return;
  }

  window.Clerk.mountSignIn(
    document.getElementById('sign-in'),
    { redirectUrl: '/' }
  );
});
"""


AUTH_SCRIPT = """
document.addEventListener('DOMContentLoaded', async () => {
  if (!window.Clerk) return;

  await window.Clerk.load();

  const button = document.getElementById('sign-out');
  if (!button) return;

  button.addEventListener('click', async () => {
    await window.Clerk.signOut({ redirectUrl: '/' });
  });
});
"""


async def _to_httpx_request(request: Request) -> httpx.Request:
    body = await request.body()
    return httpx.Request(
        method=request.method,
        url=str(request.url),
        headers=dict(request.headers),
        content=body,
    )

def _extract_primary_email(user: Any) -> str:
    email_addresses = list(getattr(user, "email_addresses", []) or [])
    primary_id = getattr(user, "primary_email_address_id", None)

    for address in email_addresses:
        if getattr(address, "id", None) == primary_id:
            return getattr(address, "email_address", "")

    if email_addresses:
        return getattr(email_addresses[0], "email_address", "")

    return ""


def _clerk_script() -> air.Script:
    return air.Script(
        src=CLERK_JS_SRC,
        async_=True,
        crossorigin="anonymous",  # allow fetching Clerk script without cookies/sensitive credentials
        **{"data-clerk-publishable-key": PUBLISHABLE_KEY},
    )

def _signed_out_page() -> air.Html:
    return air.layouts.mvpcss(
        air.Title("Air + Clerk demo"),
        air.Main(
            air.H1("Sign in"),
            air.P("Use Clerk to continue."),
            air.Div(id="sign-in", style="margin-top: 24px;"),
        ),
        _clerk_script(),
        air.Script(SIGN_IN_SCRIPT),
    )


def _signed_in_page(email: str) -> air.Html:
    clean_email = email or "Unknown user"
    return air.layouts.mvpcss(
        air.Title("Air + Clerk demo"),
        air.Main(
            air.H1("Welcome"),
            air.P(f"You are signed in as {clean_email}."),
            air.Button("Sign out", id="sign-out", type="button"),
        ),
        _clerk_script(),
        air.Script(AUTH_SCRIPT),
    )


@app.get("/")
async def home(request: Request) -> air.Html:
    httpx_request = await _to_httpx_request(request)
    origin = f"{request.url.scheme}://{request.url.netloc}"

    with Clerk(bearer_auth=SECRET_KEY) as sdk:
        state = sdk.authenticate_request(
            httpx_request,
            AuthenticateRequestOptions(authorized_parties=[origin]),
        )

        if not state.is_signed_in:
            return _signed_out_page()

        user_id = getattr(state, "user_id", None) or state.payload.get("sub")
        user = sdk.users.get(user_id=user_id)
        email = _extract_primary_email(user)
        return _signed_in_page(email)
