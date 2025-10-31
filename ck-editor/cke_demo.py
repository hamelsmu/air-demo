import os
import air

app = air.Air()
jinja = air.JinjaRenderer(directory=".")

@app.get("/")
def index(request: air.Request):
    return jinja(
        request, 
        "cke.html",
        ckeditor_license_key=os.getenv("CKEDITOR_LICENSE_KEY", "")
    )

