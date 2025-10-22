# Background tasks

Two tiny Air apps that show background progress while work completes.

- `polling.py` – asyncio task updates fetched with HTMX polling.
- `sse.py` – the same task stream pushed via `air.SSEResponse` and the HTMX SSE extension. (I prefer this one.)

```bash
pip install -r requirements.txt
fastapi dev polling.py  # or sse.py
```
