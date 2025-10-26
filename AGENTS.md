# Air Framework Guide

## Overview

[Air](https://feldroy.github.io/air/) is a FastAPI-powered web framework that generates HTML using Python classes instead of templates. It's designed for HTMX-first development with built-in Pydantic form validation.

## Documentation Resources

**When working with Air, always consult these resources:**

1. **Air llms.txt**: https://feldroy.github.io/air/llms.txt - Structured documentation index for LLMs
2. **Air Documentation**: https://feldroy.github.io/air/
3. **Air Repository**: https://github.com/feldroy/air

Use the llms.txt file to quickly locate relevant documentation pages for specific Air features.

## Core Concepts

### Air Tags (HTML as Python)

Tags are Python classes that render to HTML:

```python
air.Div(
    air.H1("Welcome"),
    air.P("Content", class_="text-muted"),
    id="container"
)
```

**Attribute handling**:
- Reserved words: `class_="highlight"` → `class="highlight"`
- HTMX/Alpine: `hx_post="/api"` → `hx-post="/api"`
- Special chars: Use dict unpacking `**{"@click": "handleClick"}`

**Special tags**:
- `Fragment`/`Children`/`Tags` - No wrapper element
- `Raw` - Unescaped HTML (use cautiously)
- Auto-escapes all content by default

### Application Setup

```python
import air

app = air.Air()  # FastAPI with AirResponse default

@app.get("/users")
def users():
    return air.Div(air.H1("Users"))

@app.page  # Creates route from function name: /about-us
def about_us():
    return air.H1("About")
```

### Layouts

Built-in layouts (`mvpcss`, `picocss`) auto-separate head/body tags and include HTMX:

```python
@app.page
def index(is_htmx=air.is_htmx_request):
    return air.layouts.mvpcss(
        air.Title("Home"),
        air.H1("My Site"),
        air.P("Content"),
        is_htmx=is_htmx  # Omits wrapper when True
    )
```

## HTMX Integration

### Request Detection

```python
from air import is_htmx_request

@app.get("/data")
def data(is_htmx=is_htmx_request):
    if is_htmx:
        return air.Div("Partial")
    return air.layouts.mvpcss(air.Div("Full page"))
```

### Common Patterns

```python
air.Button(
    "Load More",
    hx_get="/api/items",
    hx_target="#items-list",
    hx_swap="beforeend"
)
```

## Form Handling

### AirForm with Pydantic

```python
from pydantic import BaseModel
import air

class UserModel(BaseModel):
    name: str
    email: str

class UserForm(air.AirForm):
    model = UserModel

@app.post("/users")
async def create_user(request: air.Request):
    form = await UserForm.from_request(request)
    if form.is_valid:
        data: UserModel = form.data
        return air.H1(f"Created {data.name}")
    return air.Form(form.render(), air.Button("Submit"))
```

Forms auto-render with errors and preserve values after validation failure.

## Server-Sent Events

```python
@app.get("/events")
async def events():
    async def event_generator():
        while True:
            yield air.Div(f"Update")
            await asyncio.sleep(1)
    
    return air.SSEResponse(event_generator())
```

## Best Practices

1. **Use `@app.page`** for simple GET routes (auto-converts function names to paths)
2. **Return fragments for HTMX** - No wrapper needed, just return the tag
3. **Leverage type safety** - Air Tags support IDE autocomplete and type checking
4. **Reusable components** - Just Python functions that return tags
5. **Mix with Jinja** - Use Air Tags in Jinja context for dynamic content

## Quick Reference

```python
# Tags
air.Div(air.H1("Title"), class_="container")
air.Fragment(air.P("One"), air.P("Two"))  # No wrapper

# HTMX attributes
hx_get="/url", hx_target="#id", hx_swap="innerHTML"

# Layouts
air.layouts.mvpcss(*tags, is_htmx=False)

# Forms
form = await MyForm.from_request(request)
if form.is_valid:
    data = form.data  # Pydantic model instance

# Responses
return air.RedirectResponse("/path")
return air.SSEResponse(generator())
```

**Documentation**: https://feldroy.github.io/air/  
**Repository**: https://github.com/feldroy/air
