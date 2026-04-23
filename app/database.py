import aiosqlite
from app.config import settings
from collections.abc import AsyncGenerator

async def get_db() -> AsyncGenerator[aiosqlite.Connection, None]:
    """
    FastAPI dependency that provides an async SQLite connection.
    Ensures foreign keys are enabled and uses Row factory for dict-like access.
    """
    async with aiosqlite.connect(settings.DATABASE_URL) as db:
        db.row_factory = aiosqlite.Row
        await db.execute("PRAGMA foreign_keys = ON")
        yield db
