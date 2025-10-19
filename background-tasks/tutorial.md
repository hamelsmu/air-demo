# Complete Tutorial: Understanding main.py

This tutorial explains every concept in `main.py` for readers unfamiliar with HTMX, CSS, JavaScript, Server-Sent Events, and web sessions.

---

## Table of Contents

1. [Imports and Setup](#1-imports-and-setup)
2. [Application Setup](#2-application-setup)
3. [The Home Page](#3-the-home-page)
4. [Air Tags - Generating HTML with Python](#4-air-tags---generating-html-with-python)
5. [HTMX Attributes Explained](#5-htmx-attributes-explained)
6. [CSS Styling Explained](#6-css-styling-explained)
7. [CSS Animations](#7-css-animations)
8. [The Start Task Endpoint](#8-the-start-task-endpoint)
9. [Server-Sent Events (SSE)](#9-server-sent-events-sse)
10. [HTMX Out-of-Band Swaps](#10-htmx-out-of-band-swaps)
11. [Running the Server](#11-running-the-server)
12. [The Complete Flow](#12-the-complete-flow)
13. [Key Concepts Summary](#13-key-concepts-summary)

---

## 1. Imports and Setup

### Line 4: `import asyncio`

**asyncio** is Python's built-in library for asynchronous programming.

**What does "async" mean?**
- The program can do multiple things at once without blocking
- Example: While waiting for a task to sleep for 5 seconds, the server can still handle other requests from other users

### Line 5: `import random`

Standard Python library for generating random numbers. We use this to pick a random duration (2-6 seconds) for our task.

### Line 6: `import uuid`

**uuid** = "Universally Unique Identifier"

Generates unique IDs like: `550e8400-e29b-41d4-a716-446655440000`

We use this to create a unique session ID for each visitor to the website. This ensures User A's task doesn't interfere with User B's task.

### Line 7: `from datetime import datetime`

**datetime** lets us work with dates and times.

We use it to:
- Record when a task starts
- Calculate how much time has elapsed
- Show completion time to the user

### Line 8: `from typing import Dict`

This is for **type hints** in Python (optional but helpful).

`Dict[str, dict]` means "a dictionary where keys are strings and values are dicts"

Example:
```python
{
    "user123": {"status": "running", "duration": 5}
}
```

### Line 10: `import air`

The **Air web framework** - the star of our show!

Air is built on top of FastAPI and provides:
- Easy HTML generation using Python classes (Air Tags)
- Built-in support for Server-Sent Events
- Session management

Think of it as a way to build web pages using Python instead of HTML templates.

### Line 11: `from starlette.middleware.sessions import SessionMiddleware`

**Starlette** is the underlying web framework that FastAPI (and Air) are built on.

**SessionMiddleware** adds "session" support to our app.

#### What is a Session?

A session is a way to remember information about a user across multiple requests.

**Without sessions:**
- User visits page → gets assigned ID "abc123"
- User refreshes page → gets NEW ID "xyz789" (forgets who they are!)

**With sessions (using cookies):**
- User visits page → gets ID "abc123" stored in a cookie
- User refreshes page → cookie sent back → still ID "abc123" (remembered!)

**Cookies** are small pieces of data stored in the user's browser that get sent with every request to the server.

---

## 2. Application Setup

### Line 13: `app = air.Air()`

Creates our web application instance.

This `app` object will handle all web requests (visiting pages, clicking buttons, etc.)

### Line 16: `app.add_middleware(SessionMiddleware, secret_key="...")`

**Middleware** is code that runs **BEFORE** your main request handler.

Think of it like a security checkpoint at an airport - everyone goes through it.

**SessionMiddleware specifically:**

1. Checks incoming requests for a session cookie
2. If cookie exists, loads the session data (like user's session_id)
3. If no cookie, creates a new empty session
4. After your code runs, saves session data back to a cookie

The `secret_key` is used to encrypt the cookie so users can't tamper with it.

⚠️ **In production, use a long random string, not this example key!**

### Line 19: `tasks: Dict[str, dict] = {}`

This is our "database" - just a Python dictionary stored in memory.

**Structure:**
```python
{
    "user-session-id-1": {
        "status": "running",
        "duration": 4,
        "start_time": datetime(2025, 1, 1, 12, 30, 0)
    },
    "user-session-id-2": {
        "status": "completed",
        "duration": 3,
        "start_time": datetime(2025, 1, 1, 12, 31, 0)
    }
}
```

**⚠️ KEY LIMITATION:** This is IN-MEMORY storage.

If you restart the server, all tasks are forgotten! For a real app, you'd use a database like PostgreSQL or Redis.

---

## 3. The Home Page

### Lines 22-23: `@app.page` decorator

```python
@app.page
def index(request: air.Request):
```

`@app.page` is a **DECORATOR** - it modifies the function below it.

It tells Air: "When someone visits '/', call this `index()` function"

The function takes a `request` parameter which contains:
- The URL the user visited
- Cookies (including session data)
- HTTP headers
- Form data (if submitted)

### Lines 26-27: Session ID creation

```python
if "session_id" not in request.session:
    request.session["session_id"] = str(uuid.uuid4())
```

This checks: "Does this user already have a session_id?"
- **NO** → Create a new unique ID using `uuid4()` and store it in their session
- **YES** → Do nothing, they already have one

The session data is automatically saved to a cookie by SessionMiddleware when the response is sent back to the browser.

### Line 29: Get session ID

```python
session_id = request.session["session_id"]
```

Retrieve the session_id from the session (now we know it exists). We'll use this to look up the user's task in our tasks dictionary.

### Lines 32-59: Reconnection logic

```python
if session_id in tasks and tasks[session_id]["status"] == "running":
```

This checks: "Does this user have a task currently running?"

- **YES** → Show them the "reconnected" page with the spinner already active
- **NO** → Show them the normal page with just the "Start Task" button

**This is what makes the app survive page refreshes!**

---

## 4. Air Tags - Generating HTML with Python

### Line 34: `air.layouts.mvpcss(...)`

This is a pre-built layout from Air that applies **MVP.css** styling.

MVP.css is a minimalist stylesheet that makes plain HTML look nice without writing any CSS yourself.

`air.layouts.mvpcss()` generates something like:

```html
<html>
  <head>
    <link rel="stylesheet" href="mvp.css">
  </head>
  <body>
    ... your content ...
  </body>
</html>
```

### Lines 35-36: Loading JavaScript libraries

```python
air.Script(src="https://unpkg.com/htmx.org@1.9.10")
```

This generates:
```html
<script src="https://unpkg.com/htmx.org@1.9.10"></script>
```

It loads HTMX from a CDN (Content Delivery Network).

#### What is HTMX?

**HTMX** is a JavaScript library that lets you add interactivity to HTML **without writing JavaScript code**. Instead, you add special attributes to HTML elements.

**Traditional approach (requires JavaScript):**
```html
<button onclick="fetch('/api/data').then(...)">Click me</button>
```

**HTMX approach (no JavaScript needed):**
```html
<button hx-get="/api/data" hx-target="#result">Click me</button>
```

When the button is clicked, HTMX automatically:
1. Makes a GET request to `/api/data`
2. Takes the response (HTML)
3. Puts it inside the element with `id="result"`

The second Script tag loads the **HTMX SSE extension** for Server-Sent Events.

### Lines 37-39: Basic HTML elements

```python
air.Title("...")  # → <title>...</title> (shows in browser tab)
air.H1("...")     # → <h1>...</h1> (big heading)
air.P("...")      # → <p>...</p> (paragraph)
```

These are **AIR TAGS** - Python classes that generate HTML.

### Lines 40-58: The main interface structure

Let's break down the nested structure:

```python
air.Div(                                    # Outer container
    air.Button(...),                        # The "Start Task" button
    air.Div(                                # Task status container
        air.Div(                            # Status header (spinner area)
            air.Div("⏳", ...),              # Spinning hourglass emoji
            air.Span("Processing...", ...),  # Status text
            id="status-header"
        ),
        air.Div(                            # Progress messages container
            air.P("Reconnected!"),
            id="progress"
        ),
        air.Style("..."),                   # CSS animation
        id="task-status"
    )
)
```

---

## 5. HTMX Attributes Explained

### `hx_post="/start-task"` (Line 41)

When button is clicked, make a POST request to `/start-task`

(POST is used for actions that change data, unlike GET which just retrieves)

### `hx_target="#task-status"` (Line 41)

Put the response HTML inside the element with `id="task-status"`

The `#` means "find by ID" (this is CSS selector syntax)

### `hx_swap="innerHTML"` (Line 41)

Replace the **INNER content** of the target element, not the element itself.

Example:
```html
Before: <div id="task-status"><p>Old</p></div>
After:  <div id="task-status"><p>New</p></div>
                              ^^^^^^^^^^^
                              (only this changed)
```

### `hx_ext="sse"` (Line 51)

Enable the Server-Sent Events extension for this element.

This tells HTMX to use SSE instead of regular HTTP requests.

### `sse_connect="/task-progress/{session_id}"` (Line 51)

Connect to the SSE endpoint at this URL.

SSE creates a **persistent connection** that stays open, allowing the server to push updates to the browser in real-time.

### `sse_swap="message"` (Line 51)

When an SSE "message" event is received, add it to this element.

The server can send multiple messages over time, and each one gets appended.

---

## 6. CSS Styling Explained

**CSS** (Cascading Style Sheets) controls how HTML looks.

In Air, you add CSS using the `style="..."` parameter.

### Line 42: Button styling

```python
style="padding: 10px 20px; font-size: 16px; cursor: pointer;"
```

**`padding: 10px 20px;`**
- Adds space INSIDE the button
- 10px on top/bottom, 20px on left/right
- Makes the button bigger and easier to click

**`font-size: 16px;`**
- Makes text 16 pixels tall
- `px` = pixels

**`cursor: pointer;`**
- Changes mouse cursor to a pointing hand when hovering over button
- Indicates it's clickable

### Line 45: Spinner styling

```python
style="display: inline-block; font-size: 24px; animation: spin 2s linear infinite;"
```

**`display: inline-block;`**
- Makes the element flow with text but still allows width/height
- Needed for the rotation animation to work properly

**`font-size: 24px;`**
- Makes the emoji bigger (24 pixels)

**`animation: spin 2s linear infinite;`**
- Runs the "spin" animation (defined in line 54)
- `2s` = takes 2 seconds to complete one rotation
- `linear` = constant speed (not speeding up or slowing down)
- `infinite` = keep spinning forever (until page changes)

### Line 46: Text spacing

```python
style="margin-left: 10px; font-weight: bold;"
```

**`margin-left: 10px;`**
- Adds 10px of space to the LEFT of this element
- Creates gap between spinner and text

**`font-weight: bold;`**
- Makes text bold (thicker)

### Line 52: Progress box styling

```python
style="border: 1px solid #ccc; padding: 10px; background-color: #f9f9f9; min-height: 100px; overflow-y: auto;"
```

**`border: 1px solid #ccc;`**
- Draws a border around the element
- `1px` = 1 pixel thick
- `solid` = solid line (not dashed or dotted)
- `#ccc` = light gray color (hexadecimal color code)

**`padding: 10px;`**
- 10px space inside the box on all sides

**`background-color: #f9f9f9;`**
- Very light gray background
- `#f9f9f9` = almost white (RGB: 249, 249, 249 out of 255)

**`min-height: 100px;`**
- Element must be at least 100px tall
- Prevents it from being too small when empty

**`overflow-y: auto;`**
- If content is taller than the element, show a scrollbar
- Prevents content from spilling out

### Line 47: Vertical spacing

```python
style="margin-top: 20px;"
```

**`margin-top: 20px;`**
- Adds 20px of space ABOVE this element
- Creates vertical spacing between sections

---

## 7. CSS Animations

### Line 54: Defining the spin animation

```python
air.Style("@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }")
```

This defines a CSS **ANIMATION** called "spin"

#### What are Keyframes?

Keyframes define the steps of an animation.

```css
@keyframes spin {
    0% { transform: rotate(0deg); }    /* At start: 0 degrees rotation */
    100% { transform: rotate(360deg); } /* At end: 360 degrees (full circle) */
}
```

`transform: rotate()` is a CSS function that rotates an element:
- `rotate(0deg)` = no rotation
- `rotate(90deg)` = turned 90 degrees (quarter turn)
- `rotate(180deg)` = upside down
- `rotate(360deg)` = full circle (back to start)

Combined with `animation: spin 2s linear infinite` from line 45:
- The hourglass smoothly rotates from 0° to 360° over 2 seconds
- Then repeats infinitely
- This creates the spinning effect!

---

## 8. The Start Task Endpoint

### Lines 77-78: Route definition

```python
@app.post("/start-task")
async def start_task(request: air.Request):
```

This decorator tells Air: "When someone POSTs to `/start-task`, call this function"

POST requests are typically used for actions that create or modify data.

**`async def`** means this function can use `await` for asynchronous operations.

### Lines 80-82: Validate session

```python
session_id = request.session.get("session_id")
if not session_id:
    return air.P("❌ No session found", style="color: red;")
```

**`request.session.get("session_id")`**
- Try to get the session_id from the session
- `.get()` returns `None` if it doesn't exist (won't crash)

**`if not session_id:`**
- If no session, show an error message in red text
- `color: red;` makes the text red

### Lines 85-90: Create the task

```python
duration = random.randint(2, 6)
tasks[session_id] = {
    "status": "running",
    "duration": duration,
    "start_time": datetime.now(),
}
```

**`duration = random.randint(2, 6)`**
- Pick a random number between 2 and 6 (inclusive)
- This is how long the task will run

**`tasks[session_id] = { ... }`**
- Create a new entry in our tasks dictionary
- Key: the user's session_id
- Value: a dictionary with task details

**`"status": "running"`**
- Track if task is running, completed, or failed

**`"duration": duration`**
- Store how long the task should take
- We need this later to show the user and for reconnections

**`"start_time": datetime.now()`**
- Record the exact time the task started
- Used to calculate elapsed time if user refreshes

### Lines 93-104: Return the UI

Instead of redirecting to a new page, we return HTML that HTMX will inject into the page.

**This is what makes the interface update without a full page reload!**

The returned HTML contains:
1. A status header (`id="status-header"`) with spinner and text
2. A progress container (`id="progress"`) that will receive SSE messages
3. The CSS animation definition

---

## 9. Server-Sent Events (SSE)

### What are Server-Sent Events?

SSE is a web technology that allows the server to **PUSH** updates to the browser.

#### Traditional HTTP:
```
Browser: "Hey server, give me data" (request)
Server: "Here you go" (response)
[connection closes]
Browser: "Hey server, give me data again" (new request)
Server: "Here you go" (response)
[connection closes]
```

#### Server-Sent Events (SSE):
```
Browser: "Hey server, I want updates" (request)
Server: "OK, I'll keep this connection open"
[connection stays open]
Server: "Here's an update" (sends data)
Server: "Here's another update" (sends more data)
Server: "Here's the final update" (sends data)
[connection closes]
```

**Benefits:**
- No need to repeatedly ask the server for updates (no polling)
- Updates arrive immediately when available
- More efficient than WebSockets for one-way communication (server → client)

### Line 107: SSE endpoint

```python
@app.get("/task-progress/{session_id}")
```

This is an SSE endpoint that streams updates about a task.

`{session_id}` is a URL parameter - it gets passed to the function.

Example: `/task-progress/abc-123` → `session_id = "abc-123"`

### Line 111: Generator function

```python
async def progress_generator():
```

This is a **GENERATOR FUNCTION** - it uses `yield` instead of `return`

Generators can produce multiple values over time instead of just one.

**Regular function:**
```python
def get_number():
    return 5  # Returns once, function ends
```

**Generator function:**
```python
def get_numbers():
    yield 1  # Produces 1, pauses
    yield 2  # Produces 2, pauses
    yield 3  # Produces 3, ends
```

Each `yield` sends one SSE message to the browser.

### Lines 112-121: Error handling

```python
if session_id not in tasks:
    yield air.Tags(...)
    return
```

Check if this session has a task. Could be missing if server restarted or task expired.

**`yield air.Tags(...)`**
- Send TWO things in one SSE message:
  1. An out-of-band swap (`hx_swap_oob="true"`) to replace the status header
  2. An error message for the progress area

`air.Tags()` is a wrapper that doesn't create HTML itself, it just groups multiple Air Tags together.

### Lines 123-126: Get task details

```python
task = tasks[session_id]
duration = task["duration"]
start_time = task["start_time"]
elapsed = (datetime.now() - start_time).total_seconds()
```

**`elapsed = (datetime.now() - start_time).total_seconds()`**
- Calculate how many seconds have passed since the task started
- Subtracting datetime objects gives a timedelta
- `.total_seconds()` converts to a float (e.g., 2.5 seconds)

### Line 128: First message

```python
yield air.P(f"🚀 Task started at {start_time.strftime('%H:%M:%S')}", style="color: blue;")
```

Send the first SSE message: "Task started at [time]"

**`f"..."`** is an f-string (formatted string) that lets you embed variables:

**`start_time.strftime('%H:%M:%S')`** formats the datetime:
- `%H` = hour (24-hour format, e.g., 14)
- `%M` = minute (e.g., 30)
- `%S` = second (e.g., 05)
- Result: "Task started at 14:30:05"

### Lines 131-142: Already completed check

```python
if elapsed >= duration:
```

If more time has passed than the task duration, it must be done. This happens when user refreshes AFTER task completed.

We immediately send completion messages without waiting.

### Lines 145-146: Wait for remaining time

```python
remaining = duration - elapsed
await asyncio.sleep(remaining)
```

**`remaining = duration - elapsed`**
- Calculate how much time is left
- Example: 5 second task, 2 seconds elapsed → 3 seconds remaining

**`await asyncio.sleep(remaining)`**
- Pause this function for `remaining` seconds
- `await` means "do other work while waiting" (non-blocking)
- During this time, the server can handle other users' requests
- After sleep finishes, continue to next line

### Lines 149-160: Completion

```python
task["status"] = "completed"
actual_duration = (datetime.now() - start_time).total_seconds()

yield air.Tags(...)
```

**`task["status"] = "completed"`**