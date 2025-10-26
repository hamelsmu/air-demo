"""
Minimal Air + SQLModel demo with form submission to SQLite database.

Run with:
    fastapi dev database-form/main.py
"""
from contextlib import asynccontextmanager
import air
from sqlmodel import SQLModel, Field, select, Session, create_engine
from pydantic import BaseModel, Field as PydanticField
from fastapi import Depends

# Database setup
DATABASE_URL = "sqlite:///./contacts.db"
engine = create_engine(DATABASE_URL, echo=False)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

# Database model
class Contact(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    email: str
    message: str

# Form validation model
class ContactModel(BaseModel):
    name: str = PydanticField(min_length=2, max_length=50)
    email: str = air.AirField(type="email", label="Email Address")
    message: str = PydanticField(min_length=10, max_length=500)

class ContactForm(air.AirForm):
    model = ContactModel

@asynccontextmanager
async def lifespan(app):
    create_db_and_tables()
    yield

app = air.Air(lifespan=lifespan)

@app.page
def index(session: Session = Depends(get_session)):
    """Home page with form and list of contacts"""
    form = ContactForm()
    
    # Fetch all contacts
    contacts = session.exec(select(Contact).order_by(Contact.id.desc())).all()
    
    contact_list = [
        air.Li(f"{c.name} ({c.email}): {c.message}")
        for c in contacts
    ] if contacts else [air.Li("No contacts yet.", style="color: gray;")]
    
    return air.layouts.mvpcss(
        air.Title("Contact Form Demo"),
        air.H1("Contact Form"),
        air.Form(
            form.render(),
            air.Button("Submit", type="submit", style="margin-top: 10px;"),
            method="post",
            action="/submit"
        ),
        air.H2("Saved Contacts", style="margin-top: 40px;"),
        air.Ul(*contact_list),
    )

@app.post("/submit")
async def submit(
    request: air.Request,
    session: Session = Depends(get_session)
):
    """Handle form submission and save to database"""
    form = await ContactForm.from_request(request)
    
    if form.is_valid:
        contact = Contact(**form.data.model_dump())
        session.add(contact)
        session.commit()
        session.refresh(contact)
        
        return air.layouts.mvpcss(
            air.Title("Success!"),
            air.H1("Thank you!"),
            air.P(f"Your message has been saved, {contact.name}."),
            air.A("Submit another", href="/", style="color: blue;")
        )
    
    return air.layouts.mvpcss(
        air.Title("Error"),
        air.H1("Validation Error"),
        air.Form(
            form.render(),
            air.Button("Submit", type="submit", style="margin-top: 10px;"),
            method="post",
            action="/submit"
        ),
        air.A("Back", href="/", style="color: blue;")
    )
