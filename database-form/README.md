# Database Form

Minimal Air app showing form validation and SQLite persistence with SQLModel.

- Form validation with Pydantic/AirForm
- SQLite database with SQLModel ORM
- Display saved entries on homepage

```bash
# Create venv and install dependencies
uv venv
source .venv/bin/activate
uv pip install air sqlmodel "fastapi[standard]"

# Run the app
fastapi dev main.py
```

Visit http://localhost:8000 and submit the form. Contacts are saved to `contacts.db`.
