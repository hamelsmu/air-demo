# Air Demo

Minimal [Air](https://feldroy.github.io/air/) examples that highlight building blocks for AI-ready applications.

## Demos

- `background-tasks/` – contrasts HTMX polling and SSE updates for background job progress.
- `database-form/` – form validation with SQLModel and SQLite persistence.

## Run

```bash
pip install -r requirements.txt
fastapi dev background-tasks/polling.py  # or background-tasks/sse.py

# Database example (has its own venv)
cd database-form && source .venv/bin/activate && fastapi dev main.py
```
