from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, func
from datetime import datetime
from app.config import settings

# Support both PostgreSQL and SQLite
if settings.database_url.startswith("sqlite"):
    engine = create_async_engine(settings.database_url, echo=True, connect_args={"check_same_thread": False})
else:
    engine = create_async_engine(settings.database_url, echo=True)

async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

async def get_async_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session