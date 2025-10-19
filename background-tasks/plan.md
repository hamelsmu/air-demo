# Minimal Air Demo with Background Task

## What I'll create:

### 1. Project Structure:
- Create a new directory `air-demo/`
- `main.py` - Main Air application
- `requirements.txt` - Dependencies (air, fastapi[standard])

### 2. Main Application Features:
- **Home page** with a button to start the background task
- **SSE endpoint** that streams progress updates in real-time
- **Background task** that sleeps for random 10-100 seconds
- **Session storage** to track task state per user (using in-memory dict with session IDs)

### 3. Technical Implementation:
- Use **Server-Sent Events (SSE)** via Air's built-in `air.SSEResponse`
- Use **HTMX SSE extension** for reactive UI updates
- Use **Air Tags** for HTML generation
- Use **air.layouts.mvpcss** for minimal styling
- Show spinner, status message, and completion message

### 4. User Flow:
- Visit home page → see button "Start Task"
- Click button → spinner appears with "Processing..." message
- Task runs for random 10-100 seconds with periodic updates
- On completion → show success message

## Files to create:
- `air-demo/main.py` (~80 lines)
- `air-demo/requirements.txt` (2 lines)
- `air-demo/README.md` (setup instructions)

## Dependencies:
- `air` - Web framework
- `fastapi[standard]` - For running the server
