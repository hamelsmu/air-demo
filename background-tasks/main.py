"""
Minimal Air Framework Demo with Background Tasks and Server-Sent Events (SSE)
"""
import asyncio
import random
from typing import Dict
import air

app = air.Air()
tasks: Dict[int, dict] = {} 
task_counter = 0

def page_layout(*children, tasks_list):
    """Reusable page layout with HTMX scripts and common headers"""
    return air.layouts.mvpcss(
        air.Script(src="https://unpkg.com/htmx.org@1.9.10"),
        air.Title("Air Background Task Demo"),
        air.H1("Air Background Task Demo"),
        air.P("Click the button below to start a background task that will run for a random duration (2-6 seconds)."),
        *children,
        air.H2("Tasks", style="margin-top: 40px;"),
        air.Div(*tasks_list, id="tasks-list"),
        air.Style("@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }")
    )


def task_item(task_id: int, status: str):
    """Render a task item"""
    if status == "running":
        icon = air.Span("⏳", style="font-size: 20px; animation: spin 2s linear infinite;")
        text = f" Task #{task_id} - Processing..."
        color = "blue"
        poll_attrs = {"hx_get": f"/task-status/{task_id}", "hx_trigger": "every 3s", "hx_swap": "outerHTML"}
    else:
        icon = air.Span("✅", style="font-size: 20px;")
        text = f" Task #{task_id} - Completed"
        color = "green"
        poll_attrs = {}
    
    return air.P(
        icon,
        air.Span(text, style=f"margin-left: 10px; color: {color};"),
        id=f"task-{task_id}",
        **poll_attrs
    )


@app.page
def index():
    """Home page with button to start background task"""
    button = air.Button("Start Task", hx_post="/start-task", hx_target="#tasks-list", hx_swap="beforeend",
                       style="padding: 10px 20px; font-size: 16px; cursor: pointer;")

    all_tasks = sorted(tasks.values(), key=lambda t: t['task_id'])
    tasks_list = [task_item(t['task_id'], t['status']) for t in all_tasks]
    return page_layout(button, tasks_list=tasks_list)


async def complete_task_later(task_id: int, duration: int):
    """Background task that completes after duration"""
    await asyncio.sleep(duration)
    tasks[task_id]["status"] = "completed"


@app.post("/start-task")
async def start_task():
    """Endpoint to start a background task"""
    global task_counter
    task_counter += 1
    task_id = task_counter
    tasks[task_id] = {"task_id": task_id, "status": "running"}
    asyncio.create_task(complete_task_later(task_id, duration=random.randint(2, 6)))    
    return task_item(task_id, "running")


@app.get("/task-status/{task_id}")
async def task_status(task_id: int):
    """Poll endpoint for task status"""
    if task_id not in tasks:
        return ""
    return task_item(task_id, tasks[task_id]["status"])

