from sqlalchemy.ext.asyncio import (AsyncSession, create_async_engine, async_sessionmaker)
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

DATABASE_URL = "sqlite+aiosqlite:///./database.db"

engine = create_async_engine(DATABASE_URL, connect_args={"check_same_thread": False})

async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db() -> AsyncSession: #type: ignore
    async with async_session_maker() as session:
        yield session

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

