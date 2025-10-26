"""
Minimal Air + SQLModel demo with form submission to SQLite database.
"""
from contextlib import asynccontextmanager
import air
from sqlmodel import SQLModel, Field, select, Session, create_engine

engine = create_engine("sqlite:///./contacts.db")

@asynccontextmanager
async def lifespan(app):
    SQLModel.metadata.create_all(engine)
    yield

class Contact(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    email: str
    message: str

class ContactForm(air.AirForm):
    class model(SQLModel):
        name: str = air.AirField(min_length=2, max_length=50)
        email: str = air.AirField(type="email", label="Email Address")
        message: str = air.AirField(min_length=10, max_length=500)

app = air.Air(lifespan=lifespan)

@app.page
def index():
    with Session(engine) as session:
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
async def submit(request: air.Request):
    form = await ContactForm.from_request(request)
    
    if form.is_valid:
        with Session(engine) as session:
            session.add(Contact(**form.data.model_dump()))
            session.commit()
        return air.layouts.mvpcss(
            air.H1("Thank you!"),
            air.P("Your message has been saved."),
            air.A("Submit another", href="/")
        )
    
    return air.layouts.mvpcss(
        air.H1("Validation Error"),
        air.Form(form.render(), air.Button("Submit", type="submit"), method="post", action="/submit"),
        air.A("Back", href="/")
    )
