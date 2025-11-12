# TipTap Rich Text Editor with Air Framework

A minimal example demonstrating how to integrate TipTap rich text editor with the Air framework (FastAPI + HTMX).


# Install dependencies
uv add air sqlmodel "fastapi[standard]"
```

## Running the Application

```bash
# From the rich-text-editor directory
fastapi dev
```

Then open http://localhost:8000 in your browser.


## Getting Data Out of the Editor

You get the data out of the editor with the `editor.getHTML()` method.  Try this in the browser console:

```javascript
editor = document.querySelector('#editor-form form')._editor.getHTML()
console.log(editor.getHTML());
```

You can change the content like this:

```javascript
// change the content
editor.commands.setContent('<p>I am setting the content now</p>')
// insert content at the cursor
editor.commands.insertContent('This is in the middle!!')
```

There are many more methods and properties you can use to access and manipulate the data in the editor.  See the [TipTap documentation](https://tiptap.dev/docs) for more details.