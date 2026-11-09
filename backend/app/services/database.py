from pathlib import Path
from typing import Any
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from app.core.config import settings

def normalize_database_url(url: str) -> str:
    if url.startswith("postgresql+psycopg://"):
        return url.replace("postgresql+psycopg://", "postgresql+psycopg_async://", 1)
    return url

if settings.database_url.startswith("sqlite"):
    Path("./data").mkdir(exist_ok=True)

engine: AsyncEngine = create_async_engine(normalize_database_url(settings.database_url), pool_pre_ping=True)

async def execute_query(sql: str, params: dict) -> list[dict[str, Any]]:
    async with engine.connect() as conn:
        result = await conn.execute(text(sql), params)
        return [dict(row._mapping) for row in result.fetchall()]
