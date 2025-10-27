"""
TipTap Rich Text Editor with Air Framework
Demonstrates embedding TipTap editor with save/load functionality
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
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())

# Create tables
SQLModel.metadata.create_all(engine)

app = air.Air()

def base_layout(*children, is_htmx=False):
    """Layout with TipTap CSS and JS"""
    head = air.Fragment(
        air.Title("TipTap Editor - Air Demo"),
        air.Link(rel="stylesheet", href="https://unpkg.com/@tiptap/pm/style.css"),
        air.Style("""
            body { max-width: 1200px; margin: 0 auto; padding: 20px; font-family: system-ui; }
            .editor-container { border: 1px solid #ddd; border-radius: 8px; padding: 16px; min-height: 300px; }
            .tiptap { outline: none; min-height: 250px; }
            .tiptap p { margin: 1em 0; }
            .tiptap h1 { font-size: 2em; margin: 0.67em 0; }
            .tiptap h2 { font-size: 1.5em; margin: 0.75em 0; }
            .tiptap ul, .tiptap ol { padding-left: 2em; }
            .tiptap code { background: #f4f4f4; padding: 2px 4px; border-radius: 3px; }
            .tiptap pre { background: #f4f4f4; padding: 12px; border-radius: 4px; overflow-x: auto; }
            .tiptap blockquote { border-left: 3px solid #ddd; margin: 1em 0; padding-left: 1em; color: #666; }
            .menu-bar { margin-bottom: 12px; padding: 8px; background: #f8f8f8; border-radius: 4px; }
            .menu-bar button { margin: 2px; padding: 6px 12px; border: 1px solid #ddd; background: white; cursor: pointer; border-radius: 3px; }
            .menu-bar button:hover { background: #f0f0f0; }
            .menu-bar button.is-active { background: #007bff; color: white; border-color: #007bff; }
            .document-list { margin-top: 40px; }
            .document-item { padding: 12px; border: 1px solid #ddd; margin: 8px 0; border-radius: 4px; }
            .document-item:hover { background: #f8f8f8; }
            input[type="text"] { width: 100%; padding: 8px; margin: 8px 0; border: 1px solid #ddd; border-radius: 4px; }
            button.primary { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
            button.primary:hover { background: #0056b3; }
            #status { margin: 12px 0; padding: 12px; border-radius: 4px; }
            .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
            .error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        """),
        air.Script(src="https://unpkg.com/htmx.org@2.0.0"),
        air.Script(type="module", src="https://unpkg.com/@tiptap/core@2.10.3/dist/tiptap-core.js"),
        air.Script(type="module", src="https://unpkg.com/@tiptap/starter-kit@2.10.3/dist/tiptap-starter-kit.js"),
    )
    
    if is_htmx:
        return air.Fragment(*children)
    
    return air.Html(
        air.Head(head),
        air.Body(*children)
    )

@app.get("/")
def index(is_htmx=air.is_htmx_request):
    """Home page with editor and document list"""
    with Session(engine) as session:
        documents = session.exec(select(Document).order_by(Document.updated_at.desc())).all()
    
    editor_section = air.Div(
        air.H1("TipTap Rich Text Editor"),
        air.Div(id="status"),
        air.Form(
            air.Input(type="text", name="title", placeholder="Document Title", required=True, id="doc-title"),
            air.Div(id="editor-container", class_="editor-container"),
            air.Input(type="hidden", name="content", id="editor-content"),
            air.Button("Save Document", type="submit", class_="primary"),
            hx_post="/save",
            hx_target="#status",
            hx_swap="outerHTML",
        ),
        air.Script("""
            (async function() {
                const { Editor } = await import('https://unpkg.com/@tiptap/core@2.10.3/dist/tiptap-core.js');
                const { StarterKit } = await import('https://unpkg.com/@tiptap/starter-kit@2.10.3/dist/tiptap-starter-kit.js');
                
                const editor = new Editor({
                    element: document.getElementById('editor-container'),
                    extensions: [StarterKit],
                    content: '<p>Start writing your document...</p>',
                    editorProps: {
                        attributes: {
                            class: 'tiptap'
                        }
                    }
                });
                
                // Update hidden input before form submit
                document.querySelector('form').addEventListener('htmx:configRequest', function(evt) {
                    document.getElementById('editor-content').value = editor.getHTML();
                });
                
                // Expose editor globally for document loading
                window.tiptapEditor = editor;
            })();
        """)
    )
    
    document_list = air.Div(
        air.H2("Saved Documents"),
        air.Div(
            *[air.Div(
                air.H3(doc.title),
                air.P(f"Last updated: {doc.updated_at[:19]}"),
                air.Button(
                    "Load",
                    hx_get=f"/document/{doc.id}",
                    hx_target="body",
                    hx_swap="outerHTML"
                ),
                air.Button(
                    "Delete",
                    hx_delete=f"/document/{doc.id}",
                    hx_target="#status",
                    hx_confirm=f"Delete '{doc.title}'?"
                ),
                class_="document-item"
            ) for doc in documents],
            id="documents"
        ),
        class_="document-list"
    )
    
    return base_layout(editor_section, document_list, is_htmx=is_htmx)

@app.post("/save")
async def save_document(request: Request):
    """Save or update document"""
    form_data = await request.form()
    title = form_data.get("title")
    content = form_data.get("content")
    
    if not title or not content:
        return air.Div(
            air.P("❌ Title and content are required"),
            id="status",
            class_="error"
        )
    
    with Session(engine) as session:
        # Create new document
        doc = Document(
            title=title,
            content=content,
            updated_at=datetime.now().isoformat()
        )
        session.add(doc)
        session.commit()
    
    return air.Div(
        air.P(f"✅ Document '{title}' saved successfully!"),
        id="status",
        class_="success",
        hx_get="/",
        hx_trigger="load delay:1s",
        hx_target="body",
        hx_swap="outerHTML"
    )

@app.get("/document/{doc_id}")
def load_document(doc_id: int, is_htmx=air.is_htmx_request):
    """Load a document into the editor"""
    with Session(engine) as session:
        doc = session.get(Document, doc_id)
        if not doc:
            return air.Div(
                air.P("❌ Document not found"),
                id="status",
                class_="error"
            )
    
    with Session(engine) as session:
        documents = session.exec(select(Document).order_by(Document.updated_at.desc())).all()
    
    editor_section = air.Div(
        air.H1("TipTap Rich Text Editor"),
        air.Div(
            air.P(f"✅ Loaded document: {doc.title}"),
            id="status",
            class_="success"
        ),
        air.Form(
            air.Input(type="text", name="title", value=doc.title, required=True, id="doc-title"),
            air.Input(type="hidden", name="doc_id", value=str(doc_id)),
            air.Div(id="editor-container", class_="editor-container"),
            air.Input(type="hidden", name="content", id="editor-content"),
            air.Button("Update Document", type="submit", class_="primary"),
            air.Button("New Document", type="button", hx_get="/", hx_target="body", hx_swap="outerHTML"),
            hx_post="/update",
            hx_target="#status",
            hx_swap="outerHTML",
        ),
        air.Script(f"""
            (async function() {{
                const {{ Editor }} = await import('https://unpkg.com/@tiptap/core@2.10.3/dist/tiptap-core.js');
                const {{ StarterKit }} = await import('https://unpkg.com/@tiptap/starter-kit@2.10.3/dist/tiptap-starter-kit.js');
                
                const editor = new Editor({{
                    element: document.getElementById('editor-container'),
                    extensions: [StarterKit],
                    content: {repr(doc.content)},
                    editorProps: {{
                        attributes: {{
                            class: 'tiptap'
                        }}
                    }}
                }});
                
                document.querySelector('form').addEventListener('htmx:configRequest', function(evt) {{
                    document.getElementById('editor-content').value = editor.getHTML();
                }});
                
                window.tiptapEditor = editor;
            }})();
        """)
    )
    
    document_list = air.Div(
        air.H2("Saved Documents"),
        air.Div(
            *[air.Div(
                air.H3(d.title),
                air.P(f"Last updated: {d.updated_at[:19]}"),
                air.Button(
                    "Load",
                    hx_get=f"/document/{d.id}",
                    hx_target="body",
                    hx_swap="outerHTML"
                ),
                air.Button(
                    "Delete",
                    hx_delete=f"/document/{d.id}",
                    hx_target="#status",
                    hx_confirm=f"Delete '{d.title}'?"
                ),
                class_="document-item"
            ) for d in documents],
            id="documents"
        ),
        class_="document-list"
    )
    
    return base_layout(editor_section, document_list, is_htmx=is_htmx)

@app.post("/update")
async def update_document(request: Request):
    """Update existing document"""
    form_data = await request.form()
    doc_id = form_data.get("doc_id")
    title = form_data.get("title")
    content = form_data.get("content")
    
    with Session(engine) as session:
        doc = session.get(Document, int(doc_id))
        if not doc:
            return air.Div(
                air.P("❌ Document not found"),
                id="status",
                class_="error"
            )
        
        doc.title = title
        doc.content = content
        doc.updated_at = datetime.now().isoformat()
        session.add(doc)
        session.commit()
    
    return air.Div(
        air.P(f"✅ Document '{title}' updated successfully!"),
        id="status",
        class_="success"
    )

@app.delete("/document/{doc_id}")
def delete_document(doc_id: int):
    """Delete a document"""
    with Session(engine) as session:
        doc = session.get(Document, doc_id)
        if not doc:
            return air.Div(
                air.P("❌ Document not found"),
                id="status",
                class_="error"
            )
        
        title = doc.title
        session.delete(doc)
        session.commit()
    
    return air.Div(
        air.P(f"✅ Document '{title}' deleted successfully!"),
        id="status",
        class_="success",
        hx_get="/",
        hx_trigger="load delay:1s",
        hx_target="body",
        hx_swap="outerHTML"
    )
