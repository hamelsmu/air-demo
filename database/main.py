"""Minimal Air + SQLModel database demo.

Run with:
    fastapi dev database/main.py
"""
import air
from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import SQLModel, select, Field, create_engine
from typing import AsyncGenerator

# Synchronous engine for database setup
sync_engine = create_engine("sqlite:///air_demo.db", echo=True)

# Async engine for database operations
async_engine = create_async_engine(
    "sqlite+aiosqlite:///air_demo.db",
    echo=True,
    future=True,
)

# Async session configuration
async_session = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def _get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

get_async_session = Depends(_get_async_session)

class Item(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str

# Create tables
SQLModel.metadata.create_all(sync_engine)

app = air.Air()

@app.page
async def index(session: AsyncSession = get_async_session):
    """Home page displaying all items"""
    stmt = select(Item)
    result = await session.exec(stmt)
    items = result.all()

    return air.layouts.mvpcss(
        air.Title("Air Database Demo"),
        air.H1("Air Database Demo"),
        air.P("Add items to the database and see them appear below."),
        air.Form(
            air.Input(type="text", name="name", placeholder="Item name", required=True),
            air.Button("Add Item", type="submit"),
            hx_post="/add",
            hx_target="#items-list",
            hx_swap="beforeend",
            style="margin-bottom: 20px;"
        ),
        air.H2("Items"),
        air.Ul(*[air.Li(item.name, id=f"item-{item.id}") for item in items], id="items-list")
    )

@app.post("/add")
async def add_item(name: str, session: AsyncSession = get_async_session):
    """Add a new item to the database"""
    item = Item(name=name)
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return air.Li(item.name, id=f"item-{item.id}")
