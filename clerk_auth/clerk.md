# Clerk authentication notes

## Why Clerk?

Clerk provides a hosted identity service with drop-in UI, session management, and REST/SDK tooling so apps can add sign-in, sign-up, and profile management without building auth flows manually.

- **Frontend SDKs** (for example `@clerk/clerk-js`, `@clerk/nextjs`) mount prebuilt widgets like `<SignIn />` or `<UserButton />` and manage client-side state ([JavaScript quickstart](https://raw.githubusercontent.com/clerk/clerk-docs/main/docs/getting-started/quickstart.js-frontend.mdx)).
- **Backend SDKs** (e.g., `clerk-backend-api` for Python) wrap Clerk’s REST API and expose helpers such as `authenticate_request` to validate incoming tokens ([Python SDK README](https://github.com/clerk/clerk-sdk-python/blob/main/README.md)).
- **Session tokens** are JWTs set in the `__session` cookie (same-origin) or passed via `Authorization` headers; they include user, session, and organization claims and should be verified on every request ([Session tokens guide](https://raw.githubusercontent.com/clerk/clerk-docs/main/docs/guides/sessions/session-tokens.mdx)).

## Account & key setup

1. Create a Clerk application in the dashboard.
2. Copy the environment keys from **API Keys**: `CLERK_PUBLISHABLE_KEY` (frontend) and `CLERK_SECRET_KEY` (backend). They use `pk_` / `sk_` prefixes for test vs. live environments ([Environment variables reference](https://raw.githubusercontent.com/clerk/clerk-docs/main/docs/guides/development/clerk-environment-variables.mdx)).
3. Optional configuration via env vars:
   - `CLERK_FAPI` / `CLERK_JS_URL` to pin frontend API endpoints or scripts.
   - `CLERK_API_URL`, `CLERK_API_VERSION` for backend REST calls.
   - `CLERK_DOMAIN` & `CLERK_IS_SATELLITE` for multi-domain sharing.
   - Telemetry opt-outs (`CLERK_TELEMETRY_DISABLED`, etc.).
4. Never expose the secret key to the browser; restrict publishable keys to client bundles only.

## Minimal frontend integration options

### Using Clerk’s CDN script (framework agnostic)

```html
<!-- index.html -->
<div id="app"></div>
<script
  async
  crossorigin="anonymous"
  data-clerk-publishable-key="${CLERK_PUBLISHABLE_KEY}"
  src="https://${FRONTEND_API}/npm/@clerk/clerk-js@5/dist/clerk.browser.js"
></script>
<script>
  window.addEventListener('load', async () => {
    await Clerk.load();
    const root = document.getElementById('app');
    if (Clerk.isSignedIn) {
      root.innerHTML = '<div id="user-button"></div>';
      Clerk.mountUserButton(root.firstElementChild);
    } else {
      root.innerHTML = '<div id="sign-in"></div>';
      Clerk.mountSignIn(root.firstElementChild);
    }
  });
</script>
```

- `FRONTEND_API` (a.k.a. FAPI) is available from the dashboard or as `CLERK_FAPI`.
- `Clerk.load()` initializes the SDK; `Clerk.isSignedIn`, `mountSignIn`, and `mountUserButton` manage UI state ([JS quickstart](https://raw.githubusercontent.com/clerk/clerk-docs/main/docs/getting-started/quickstart.js-frontend.mdx)).
- This approach works for static assets served alongside Air or from a separate frontend bundle.

The `<script>` example above downloads Clerk’s JavaScript from Clerk’s own servers. When the script starts, it looks at the publishable key you pass in `data-clerk-publishable-key` and figures out which Clerk project to talk to—no extra configuration is needed. Some production apps prefer to host that script from their own Clerk subdomain (for example `https://your-app.clerk.accounts.dev/...`) so that every browser request only hits their allow-listed domains. If you ever need that setup, add `data-clerk-frontend-api="your-app.clerk.accounts.dev"` to the `<script>` tag. For this demo we keep things simple and rely on the default Clerk-hosted script plus the publishable key.

### Using `@clerk/clerk-js` directly

When bundling with Vite/Webpack, install `@clerk/clerk-js`, instantiate `new Clerk(publishableKey)`, call `await clerk.load()`, then mount widgets the same way as above. Environment variables (e.g., `VITE_CLERK_PUBLISHABLE_KEY`) keep keys outside source control.

## Backend integration (Air/FastAPI)

Install the backend SDK in your Air project:

```bash
pip install clerk-backend-api
```

### Authenticating requests

Use `clerk_backend_api.Clerk` with your secret key and the `authenticate_request` helper (from `clerk_backend_api.security`) to validate each incoming HTTP request. The helper extracts session or API tokens from headers/cookies, downloads JWKS as needed, and ensures the token is valid, unexpired, and issued by your frontend origin.

```python
import os
from clerk_backend_api import Clerk
from clerk_backend_api.security import authenticate_request
from clerk_backend_api.security.types import AuthenticateRequestOptions

clerk = Clerk(bearer_auth=os.environ["CLERK_SECRET_KEY"])

def verify_httpx_request(request):
    state = clerk.authenticate_request(
        request,
        AuthenticateRequestOptions(
            authorized_parties=["http://localhost:8000"],
            accepts_token=["session_token", "oauth_token"],
        ),
    )
    return state if state.is_signed_in else None
```

- `authorized_parties` mitigates CSRF by whitelisting Origins.
- Use `state.payload` for user/session claims or `state.reason` to inspect failures (per Python SDK README).
- In Air routes, convert the incoming Starlette/FastAPI `Request` into the format `authenticate_request` expects (e.g., build an `httpx.Request`).

### Accessing Clerk resources

The SDK exposes typed clients (for example `clerk.users.get_user(user_id)`) and supports async usage with `async with Clerk(...)`. For operations not covered by helpers, call Clerk’s REST API at `https://api.clerk.com/v1` with the secret key as a bearer token ([Backend API reference](https://clerk.com/docs/reference/backend-api)).

## Session tokens & claims

- Issued on sign-in, stored in the `__session` cookie or `Authorization: Bearer <token>` header, and scoped by the origin (`azp` claim) ([Session tokens guide](https://raw.githubusercontent.com/clerk/clerk-docs/main/docs/guides/sessions/session-tokens.mdx)).
- Default claims include `sub` (user ID), `sid` (session ID), `iss` (frontend API URL), `exp`/`nbf`, `fva` (MFA timestamps), optional organization data (`o.*`), and `sts` (session status).
- Token size must stay under ~4 KB to fit browser cookie limits; avoid large metadata in JWTs, prefer fetching via the Backend API.

## Manual JWT verification fallback

If you opt out of the SDK helpers:

1. Read the token from the cookie or header.
2. Fetch your JWKS via `https://api.clerk.com/v1/jwks` or `<frontend_api>/.well-known/jwks.json`.
3. Verify signature (RS256), `exp`, `nbf`, and ensure `azp` matches a permitted origin.
4. Optionally reject sessions with `sts = "pending"` when org membership is required ([Manual verification guide](https://raw.githubusercontent.com/clerk/clerk-docs/main/docs/guides/sessions/manual-jwt-verification.mdx)).

Python example (using `pyjwt` & `cookies`):

```python
import jwt

decoded = jwt.decode(
    token,
    public_key_pem,
    algorithms=["RS256"],
    audience=None,
    options={"require": ["exp", "nbf", "sid", "sub"]},
)
if decoded.get("azp") not in {"http://localhost:8000", "https://example.com"}:
    raise RuntimeError("Unauthorized origin")
```

## Implementation checklist for the Air demo

1. Add Clerk publishable/secret keys to `.env` or environment.
2. Serve a small Clerk-powered frontend (bundled or CDN script) that mounts `<SignIn />` and `<UserButton />`.
3. On the backend, wrap Air routes with a dependency that calls `authenticate_request` and attaches the Clerk session/user data to the request context.
4. Handle unauthenticated requests (redirect to sign-in or return 401) and optionally enforce organization/session status.
5. For advanced claims or larger metadata, query Clerk’s Backend API using the Python SDK rather than expanding JWT payload size.

These notes consolidate the material needed to wire Clerk into the Air demo and should be referenced when implementing the minimal auth example.
