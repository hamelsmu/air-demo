# Clerk Authentication

Minimal Air application demonstrating authentication using Clerk SDK.

**Clerk Documentation**: https://clerk.com/docs

## Setup

Requires a `.env` file with your Clerk API keys (not checked into git):

```bash
# Create .env file with your Clerk keys
cat > .env <<EOF
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
EOF
```

## Run

```bash
fastapi dev main.py
```

Visit http://localhost:8000
