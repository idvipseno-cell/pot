"""
db.py
-----
إعداد المحرك (Engine) والجلسات (Sessions) غير المتزامنة لقاعدة بيانات SQLite.
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from bot.database.models import Base
from config import config

engine = create_async_engine(f"sqlite+aiosqlite:///{config.DB_PATH}", echo=False)

async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def init_db() -> None:
    """إنشاء الجداول تلقائياً إن لم تكن موجودة."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
