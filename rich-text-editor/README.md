# TipTap Rich Text Editor with Air Framework

A minimal example demonstrating how to integrate TipTap rich text editor with the Air framework (FastAPI + HTMX).

## Features

- **Rich Text Editing**: Full-featured editor with formatting options (headings, lists, bold, italic, code, etc.)
- **Save/Load Documents**: Store documents in SQLite database
- **CRUD Operations**: Create, read, update, and delete documents
- **HTMX Integration**: Seamless updates without page reloads
- **TipTap Editor**: Modern, extensible rich text editor

## Installation

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv add air sqlmodel "fastapi[standard]"
```

## Running the Application

```bash
# From the rich-text-editor directory
fastapi dev main.py
```

Then open http://localhost:8000 in your browser.

## How It Works

### TipTap Integration

TipTap is loaded via CDN as ES modules:

```javascript
const { Editor } = await import('@tiptap/core');
const { StarterKit } = await import('@tiptap/starter-kit');
```

The editor is initialized with the StarterKit extension which includes:
- Basic formatting (bold, italic, code)
- Headings (H1-H6)
- Lists (ordered and unordered)
- Blockquotes
- Code blocks
- And more

### Data Flow

1. **Creating/Editing**: User types in TipTap editor
2. **Saving**: On form submit, editor HTML is captured and sent to FastAPI via HTMX POST
3. **Storage**: Document stored in SQLite database using SQLModel
4. **Loading**: Clicking "Load" on a document retrieves content and populates editor
5. **Updating**: Modified documents can be updated or saved as new

### HTMX Integration

The app uses HTMX for seamless interactions:
- Form submissions via `hx-post`
- Document loading via `hx-get`
- Deletion via `hx-delete`
- Auto-refresh after operations with `hx-trigger="load delay:1s"`

### Database Schema

```python
class Document(SQLModel, table=True):
    id: int | None
    title: str
    content: str  # HTML from TipTap
    created_at: str
    updated_at: str
```

## Extending This Example

### Adding More TipTap Features

TipTap has many extensions available:

```javascript
import { Highlight } from '@tiptap/extension-highlight';
import { TextAlign } from '@tiptap/extension-text-align';
import { Table } from '@tiptap/extension-table';

const editor = new Editor({
    extensions: [
        StarterKit,
        Highlight,
        TextAlign.configure({ types: ['heading', 'paragraph'] }),
        Table
    ]
});
```

### Adding a Toolbar

Create custom toolbar buttons:

```html
<div class="menu-bar">
    <button onclick="editor.chain().focus().toggleBold().run()">Bold</button>
    <button onclick="editor.chain().focus().toggleItalic().run()">Italic</button>
    <button onclick="editor.chain().focus().toggleHeading({ level: 1 }).run()">H1</button>
</div>
```

### Future Enhancements

This example can be extended with:
- **Comments**: Add TipTap's Comment extension or build custom annotations
- **AI Integration**: Add AI writing assistance via custom commands
- **Collaboration**: Use Yjs for real-time collaborative editing
- **Export**: Convert to PDF, Markdown, or DOCX
- **Rich Media**: Add image uploads, embeds, and attachments

## Related Links

- [TipTap Documentation](https://tiptap.dev/docs)
- [Air Framework Docs](https://feldroy.github.io/air/)
- [HTMX Documentation](https://htmx.org/docs/)
