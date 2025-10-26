# Database Form

Contact form with HTML5 validation and SQLite persistence using SQLModel.

## Features

- HTML5 client-side validation
- Jinja templates for form rendering
- SQLite database with SQLModel ORM

## Run

```bash
uv venv
source .venv/bin/activate
uv pip install air sqlmodel "fastapi[standard]"
fastapi dev main.py
```

Visit http://localhost:8000 to submit contacts. Data is saved to `contacts.db`.
