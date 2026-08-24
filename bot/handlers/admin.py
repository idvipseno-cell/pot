"""
admin.py
--------
لوحة إحصائيات خاصة بالمطور الرئيسي فقط.
"""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.database import crud
from config import config

router = Router(name="admin")


@router.message(Command("stats"))
async def stats_cmd(message: Message) -> None:
    if not config.DEV_ID or message.from_user.id != config.DEV_ID:
        return  # تجاهل تام لغير المطور (لا رسالة رفض حتى لا يُكشف الأمر)

    users_count = await crud.count_users()
    channels_count = await crud.count_channels()

    await message.answer(
        "📊 <b>إحصائيات البوت</b>\n\n"
        f"👥 عدد المستخدمين المسجلين: <b>{users_count}</b>\n"
        f"📡 عدد القنوات قيد المراقبة: <b>{channels_count}</b>"
    )
