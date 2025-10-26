# Database Form

Minimal Air app with Jinja templates, HTML5 validation, and SQLite persistence.

**Features:**
- HTML5 client-side validation (browser validates before submission)
- Jinja templates for form rendering
- SQLite database with SQLModel ORM
- No server-side Pydantic validation needed

**Why HTML5 validation?**
- Immediate user feedback without round-trip to server
- Browser handles validation UI automatically
- Simpler code (no `form.is_valid` checks)
- Note: Still vulnerable to bypass via curl/fetch - fine for demos

```bash
# Create venv and install dependencies
uv venv
source .venv/bin/activate
uv pip install air sqlmodel "fastapi[standard]"

# Run the app
fastapi dev main.py
```

Visit http://localhost:8000 and submit the form. 

**Try the validation:**
- Leave fields empty → browser blocks submission
- Type 1 char in name → "too short" error
- Type invalid email → browser validates format
- Type less than 10 chars in message → blocked

Contacts are saved to `contacts.db`.
