The ck-editor folder contains a simple example of using the CKEditor 5 library with Air.

## Usage

To run the example, use the following command:

```bash
python cke_demo.py
```

CKE is different from TipTap in that it comes bundled with things like a toolbar and other features so you don't need to create them from scratch yourself.

## Accessing The Data

You can access data in the editor via the `editor` variable.  In the browser console, run the following:

```javascript
console.log(editor.getData());
```

You can set the data similarly: 

```javascript
// replace the content completely
editor.setData('<p>Hello, world!</p>');
// insert content at the cursor
editor.model.change(writer => {editor.model.insertContent(writer.createText('This is in the middle!'))})
```

There are many more methods and properties you can use to access and manipulate the data in the editor.  See the [CKEditor 5 documentation](https://ckeditor.com/docs/ckeditor5/latest/api/index.html) for more details.