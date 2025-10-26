"""
Minimal Air + SQLModel demo with form submission to SQLite database.

Run with:
    fastapi dev database-form/main.py
"""
from contextlib import asynccontextmanager
import air
from sqlmodel import SQLModel, Field, select, Session, create_engine
from pydantic import Field as PydanticField
from fastapi import Depends

engine = create_engine("sqlite:///./contacts.db", echo=False)

def get_session():
    with Session(engine) as session:
        yield session

class Contact(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = PydanticField(min_length=2, max_length=50)
    email: str = air.AirField(type="email", label="Email Address")
    message: str = PydanticField(min_length=10, max_length=500)

class ContactForm(air.AirForm):
    class model(Contact):
        pass

@asynccontextmanager
async def lifespan(app):
    SQLModel.metadata.create_all(engine)
    yield

app = air.Air(lifespan=lifespan)

@app.page
def index(session: Session = Depends(get_session)):
    contacts = session.exec(select(Contact).order_by(Contact.id.desc())).all()
    
    return air.layouts.mvpcss(
        air.Title("Contact Form Demo"),
        air.H1("Contact Form"),
        air.Form(
            ContactForm().render(),
            air.Button("Submit", type="submit"),
            method="post",
            action="/submit"
        ),
        air.H2("Saved Contacts", style="margin-top: 40px;"),
        air.Ul(*[air.Li(f"{c.name} ({c.email}): {c.message}") for c in contacts]) if contacts 
            else air.Ul(air.Li("No contacts yet.", style="color: gray;")),
    )

@app.post("/submit")
async def submit(request: air.Request, session: Session = Depends(get_session)):
    form = await ContactForm.from_request(request)
    
    if form.is_valid:
        session.add(Contact(**form.data.model_dump()))
        session.commit()
        return air.layouts.mvpcss(
            air.H1("Thank you!"),
            air.P(f"Your message has been saved."),
            air.A("Submit another", href="/")
        )
    
    return air.layouts.mvpcss(
        air.H1("Validation Error"),
        air.Form(form.render(), air.Button("Submit", type="submit"), method="post", action="/submit"),
        air.A("Back", href="/")
    )
