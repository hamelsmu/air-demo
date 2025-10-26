"""
Minimal Air + SQLModel demo with Jinja templates and HTML5 validation.
Uses browser validation instead of server-side Pydantic validation.
"""
import air
from sqlmodel import SQLModel, Field, select, Session, create_engine
from air.requests import Request

# Database setup
engine = create_engine("sqlite:///./contacts.db")

class Contact(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    email: str
    message: str

# Create tables (idempotent - safe to call multiple times)
SQLModel.metadata.create_all(engine)

app = air.Air()
jinja = air.JinjaRenderer(directory="templates")

@app.get("/")
def index(request: Request):
    with Session(engine) as dbsession:
        contacts = dbsession.exec(select(Contact).order_by(Contact.id.desc())).all()
    
    return jinja(
        request,
        name="form.html",
        contacts=contacts
    )

@app.post("/submit")
async def submit(request: Request):
    form_data = await request.form()
    
    # Save to database (HTML5 validates in browser before submission)
    with Session(engine) as dbsession:
        contact = Contact(
            name=form_data.get("name"),
            email=form_data.get("email"),
            message=form_data.get("message")
        )
        dbsession.add(contact)
        dbsession.commit()
    
    return jinja(request, name="success.html")
