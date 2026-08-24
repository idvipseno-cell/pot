"""
crud.py
-------
عمليات الإضافة/القراءة/التعديل/الحذف (CRUD) على قاعدة البيانات.
كل دالة تفتح جلستها الخاصة بشكل مستقل حتى يسهل استدعاؤها من أي مكان في المشروع.
"""

from typing import List, Optional

from sqlalchemy import func, select

from bot.database.db import async_session
from bot.database.models import Channel, User


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------
async def get_or_create_user(user_id: int, username: Optional[str], full_name: str) -> User:
    async with async_session() as session:
        user = await session.get(User, user_id)
        if user is None:
            user = User(id=user_id, username=username, full_name=full_name)
            session.add(user)
            await session.commit()
            await session.refresh(user)
        else:
            changed = False
            if user.username != username:
                user.username = username
                changed = True
            if user.full_name != full_name:
                user.full_name = full_name
                changed = True
            if changed:
                await session.commit()
        return user


async def count_users() -> int:
    async with async_session() as session:
        result = await session.execute(select(func.count()).select_from(User))
        return result.scalar_one()


# ---------------------------------------------------------------------------
# Channels
# ---------------------------------------------------------------------------
async def add_or_update_channel(channel_id: int, title: str, owner_id: int) -> Channel:
    async with async_session() as session:
        result = await session.execute(select(Channel).where(Channel.channel_id == channel_id))
        channel = result.scalar_one_or_none()
        if channel is None:
            channel = Channel(channel_id=channel_id, title=title, owner_id=owner_id)
            session.add(channel)
        else:
            channel.title = title
            channel.owner_id = owner_id
            channel.notifications_enabled = True
        await session.commit()
        await session.refresh(channel)
        return channel


async def get_user_channels(owner_id: int) -> List[Channel]:
    async with async_session() as session:
        result = await session.execute(
            select(Channel).where(Channel.owner_id == owner_id).order_by(Channel.added_at.desc())
        )
        return list(result.scalars().all())


async def get_channel_by_pk(pk_id: int) -> Optional[Channel]:
    async with async_session() as session:
        return await session.get(Channel, pk_id)


async def get_channel_by_telegram_id(channel_id: int) -> Optional[Channel]:
    async with async_session() as session:
        result = await session.execute(select(Channel).where(Channel.channel_id == channel_id))
        return result.scalar_one_or_none()


async def delete_channel(pk_id: int) -> bool:
    async with async_session() as session:
        channel = await session.get(Channel, pk_id)
        if channel is None:
            return False
        await session.delete(channel)
        await session.commit()
        return True


async def toggle_notifications(pk_id: int) -> Optional[bool]:
    async with async_session() as session:
        channel = await session.get(Channel, pk_id)
        if channel is None:
            return None
        channel.notifications_enabled = not channel.notifications_enabled
        await session.commit()
        return channel.notifications_enabled


async def count_channels() -> int:
    async with async_session() as session:
        result = await session.execute(select(func.count()).select_from(Channel))
        return result.scalar_one()
