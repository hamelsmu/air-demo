# Database Form

Minimal Air apps with Jinja templates, HTML5 validation, and database persistence.

## SQLite Version (`main.py`)

```bash
uv venv
source .venv/bin/activate
uv pip install air sqlmodel "fastapi[standard]"
fastapi dev main.py
```

## PostgreSQL Version (`main-postgres.py`)

```bash
brew install postgresql@17
brew services start postgresql@17
createdb contacts  # Creates database (ORM creates tables)

uv pip install air sqlmodel "fastapi[standard]" psycopg2-binary

# Unset DATABASE_URL to use default (your macOS username)
unset DATABASE_URL
fastapi dev main-postgres.py
```

Cleanup: `dropdb contacts && brew services stop postgresql@17`

## Features

- HTML5 validation (browser validates minlength, maxlength, required, email)
- Jinja templates with validation attributes
- SQLModel ORM (creates tables automatically)
- No server-side validation (HTML5 only)
