# Air Framework Background Task Demo

A minimal demonstration of the [Air web framework](https://feldroy.github.io/air/) featuring:
- Server-Sent Events (SSE) for real-time updates
- Background task with random duration (2-6 seconds)
- HTMX integration for reactive UI
- Session-based task tracking (survives page refresh!)

## Features

- Click a button to start a background task
- Visual feedback with spinner animation
- Real-time progress updates via Server-Sent Events
- Completion notification
- Clean, minimal UI using MVP.css layout

## Requirements

- Python 3.13 or 3.14 (required by Air framework)
- [uv](https://docs.astral.sh/uv/) package manager

## Installation

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```

## Running the Application

```bash
fastapi dev main.py
```

Or using uvicorn:

```bash
uvicorn main:app --reload
```

## Usage

1. Start the application using one of the methods above
2. Open your browser to http://127.0.0.1:8000
3. Click the "Start Task" button
4. Watch the progress updates appear in real-time
5. Wait for the completion message (2-6 seconds)
6. Try refreshing the page while the task is running - it will reconnect!

## How It Works

### Architecture

- **Air Framework**: Built on FastAPI, provides Air Tags for HTML generation
- **Server-Sent Events (SSE)**: Streams progress updates from server to client
- **HTMX**: Handles SSE connections and DOM updates without writing JavaScript
- **Session Management**: Uses UUID-based session IDs to track individual tasks

### Key Components

1. **Home Page** (`/`): Displays the interface with a "Start Task" button
2. **Start Task Endpoint** (`/start-task/{session_id}`): Initializes a task and returns SSE-connected UI
3. **Progress Stream** (`/task-progress/{session_id}`): SSE endpoint that yields progress updates

### Code Highlights

- **Air Tags**: Python classes that render HTML (e.g., `air.Div()`, `air.P()`)
- **air.SSEResponse**: Built-in Air support for Server-Sent Events
- **HTMX SSE Extension**: Enables reactive UI updates via `hx_ext="sse"` and `sse_connect`
- **Async Generators**: Uses `async def` with `yield` for streaming updates

## File Structure

```
air-demo/
├── main.py              # Main application code
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Technologies Used

- [Air](https://feldroy.github.io/air/) - AI-first Python web framework
- [FastAPI](https://fastapi.tiangolo.com/) - Modern async web framework (Air's foundation)
- [HTMX](https://htmx.org/) - HTML-driven interactivity
- [MVP.css](https://andybrewer.github.io/mvp/) - Minimalist stylesheet
- Server-Sent Events (SSE) - Real-time server-to-client streaming

## Notes

- The task duration is randomly chosen between 2-6 seconds
- Each session gets a unique UUID to track its task
- **Sessions persist across page refreshes** - refresh during a running task and it will reconnect!
- Task state is stored in-memory (resets on server restart)
- Progress updates are sent at regular intervals based on task duration
- Reconnections automatically resume from current progress
- Completed tasks are automatically cleaned up after 2 seconds

## Learning Resources

- [Air Documentation](https://feldroy.github.io/air/)
- [Air GitHub Repository](https://github.com/feldroy/air)
- [HTMX SSE Extension](https://htmx.org/extensions/server-sent-events/)
- [Server-Sent Events Specification](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)

## License

This is a demonstration project. Feel free to use and modify as needed.
