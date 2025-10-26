# Background Tasks

Two approaches to displaying background job progress in Air:

- `polling.py` – HTMX polling to fetch task updates
- `sse.py` – Server-sent events (SSE) to push task updates

## Run

```bash
pip install -r ../requirements.txt
fastapi dev polling.py  # or sse.py
```
