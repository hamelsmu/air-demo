# Air Demo

Minimal [Air](https://feldroy.github.io/air/) examples that highlight building blocks for AI-ready applications.

## Demos

- `background-tasks/` – contrasts HTMX polling and SSE updates for background job progress.
- `database/` – async database operations using SQLModel with PostgreSQL.

## Run

```bash
pip install -r requirements.txt
fastapi dev background-tasks/polling.py  # or background-tasks/sse.py
```
