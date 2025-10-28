"""
TipTap Rich Text Editor with Air Framework
Minimal example using Jinja templates and HTMX
"""
import air
import json
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
    with Session(engine) as dbsession:
        documents = dbsession.exec(select(Document).order_by(Document.updated_at.desc())).all()
    return jinja(request, name="index.html", documents=documents, doc=None)

@app.get("/load/{doc_id}")
def load_document(doc_id: int, request: Request):
    """Load document into editor (returns form fragment)"""
    with Session(engine) as dbsession:
        doc = dbsession.get(Document, doc_id)
        if not doc:
            return '<div id="editor-form"><p class="error">Document not found</p></div>'

    initial_content = json.dumps(doc.content)
    return jinja(request, name="editor-form.html", doc=doc, initial_content=initial_content)

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

    return f'''<div id="status" class="success" hx-get="/documents-list" hx-trigger="load delay:500ms" hx-target="#documents" hx-swap="innerHTML">
        <p>✅ Document '{title}' {action} successfully!</p>
    </div>'''

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

    return f'''<div id="status" class="success" hx-get="/" hx-trigger="load delay:1s" hx-target="#app" hx-swap="innerHTML">
        <p>✅ Document '{title}' deleted successfully!</p>
    </div>'''

@app.get("/documents-list")
def documents_list(request: Request):
    """Return just the documents list fragment"""
    with Session(engine) as dbsession:
        documents = dbsession.exec(select(Document).order_by(Document.updated_at.desc())).all()
    return jinja(request, name="documents-list.html", documents=documents)
