"""
TipTap Rich Text Editor with Air Framework
Minimal example using Jinja templates and HTMX
"""
import air
from sqlmodel import SQLModel, Field, select, Session, create_engine
from air.requests import Request
from datetime import datetime

# Database setup
engine = create_engine("sqlite:///./documents.db")

class Document(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    content: str  # Store as HTML from TipTap
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())

# Create tables
SQLModel.metadata.create_all(engine)

app = air.Air()
jinja = air.JinjaRenderer(directory="templates")

# Serve static files
app.mount("/static", air.StaticFiles(directory="static"), name="static")

@app.get("/")
def index(request: Request):
    """Main page"""
    return jinja(request, name="index.html")

@app.get("/load/{doc_id}")
def load_document(doc_id: int, request: Request):
    """Load document into editor (returns form fragment)"""
    with Session(engine) as dbsession:
        doc = dbsession.get(Document, doc_id)
        if not doc:
            return '<div id="editor-form"><p class="error">Document not found</p></div>'
    
    return f'''<div id="editor-form">
    <form hx-post="/save" hx-target="#status">
        <input name="title" type="text" value="{doc.title}" required placeholder="Document Title" />
        <input name="doc_id" id="doc_id" type="hidden" value="{doc.id}" />
        
        <div class="control-group">
            <div class="button-group">
                <button type="button" data-action="bold">Bold</button>
                <button type="button" data-action="italic">Italic</button>
                <button type="button" data-action="underline">Underline</button>
                <button type="button" data-action="strike">Strike</button>
                <button type="button" data-action="code">Code</button>
                <button type="button" data-action="link">Link</button>
                <button type="button" data-action="h1">H1</button>
                <button type="button" data-action="h2">H2</button>
                <button type="button" data-action="h3">H3</button>
                <button type="button" data-action="bullet-list">Bullet list</button>
                <button type="button" data-action="ordered-list">Ordered list</button>
                <button type="button" data-action="code-block">Code block</button>
                <button type="button" data-action="blockquote">Blockquote</button>
                <button type="button" data-action="undo">Undo</button>
                <button type="button" data-action="redo">Redo</button>
            </div>
            <div class="editor-container" data-tiptap="" data-initial-html='{doc.content}'></div>
        </div>
        
        <button id="save-btn" type="submit">Save</button>
        <button type="button" onclick="window.location.href='/'">New</button>
    </form>
</div>'''

@app.post("/save")
async def save_document(request: Request):
    """Save or update document (returns status fragment)"""
    form_data = await request.form()
    doc_id = form_data.get("doc_id")
    title = form_data.get("title")
    content = form_data.get("content")

    if not title or not content:
        return '<div id="status" class="error"><p>❌ Title and content are required</p></div>'

    with Session(engine) as dbsession:
        if doc_id:
            doc = dbsession.get(Document, int(doc_id))
            if not doc:
                return '<div id="status" class="error"><p>❌ Document not found</p></div>'
            doc.title = title
            doc.content = content
            doc.updated_at = datetime.now().isoformat()
            action = "updated"
        else:
            doc = Document(title=title, content=content)
            action = "saved"

        dbsession.add(doc)
        dbsession.commit()
        dbsession.refresh(doc)
        saved_doc_id = doc.id

    if action == "saved":
        return f'''<button id="save-btn" type="submit" class="saved" hx-swap-oob="true">✓ Saved</button>
        <input id="doc_id" name="doc_id" type="hidden" value="{saved_doc_id}" hx-swap-oob="true">
        <div hx-get="/documents-list" hx-trigger="load" hx-target="#documents" hx-swap="innerHTML"></div>'''
    else:
        return f'''<button id="save-btn" type="submit" class="saved" hx-swap-oob="true">✓ Saved</button>
        <div hx-get="/documents-list" hx-trigger="load" hx-target="#documents" hx-swap="innerHTML"></div>'''

@app.delete("/delete/{doc_id}")
def delete_document(doc_id: int):
    """Delete document (returns status fragment)"""
    with Session(engine) as dbsession:
        doc = dbsession.get(Document, doc_id)
        if not doc:
            return '<div id="status" class="error"><p>❌ Document not found</p></div>'

        title = doc.title
        dbsession.delete(doc)
        dbsession.commit()

    return f'''<div id="status" class="success" hx-get="/documents-list" hx-trigger="load" hx-target="#documents" hx-swap="innerHTML">
        <p>✅ Document '{title}' deleted successfully!</p>
    </div>'''

@app.get("/documents-list")
def documents_list(request: Request):
    """Return just the documents list fragment"""
    with Session(engine) as dbsession:
        documents = dbsession.exec(select(Document).order_by(Document.updated_at.desc())).all()
    
    html_parts = []
    for d in documents:
        html_parts.append(f'''<div class="document-item">
    <h3>{d.title}</h3>
    <p>Last updated: {d.updated_at[:19]}</p>
    <button hx-get="/load/{d.id}" hx-target="#editor-form" hx-swap="outerHTML">Load</button>
    <button hx-delete="/delete/{d.id}" hx-target="#status" hx-confirm="Delete '{d.title}'?">Delete</button>
</div>''')
    
    if not html_parts:
        return '<p class="text-gray-500">No documents yet. Create your first document above!</p>'
    
    return '\n'.join(html_parts)
