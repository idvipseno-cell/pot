"""
force_sub.py
------------
Middleware للتحقق من اشتراك المستخدم في قناة المطور قبل السماح له باستخدام أي أمر
أو زر في البوت (باستثناء المطور نفسه).
"""

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.enums import ChatMemberStatus
from aiogram.types import CallbackQuery, Message, TelegramObject, Update

from bot.keyboards.inline import force_sub_kb
from config import config

ALLOWED_STATUSES = {ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR}

FORCE_SUB_TEXT = (
    "⚠️ <b>الاشتراك في القناة إجباري لاستخدام البوت</b>\n\n"
    "يرجى الاشتراك في قناتنا الرسمية أولاً، ثم اضغط على زر (تحقق من الاشتراك) بالأسفل."
)


class ForceSubMiddleware(BaseMiddleware):
    """يحجب أي تفاعل (رسالة/زر) قبل التأكد من اشتراك المستخدم بقناة المطور."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        # إن لم يتم ضبط قناة اشتراك إجباري، تجاوز الفحص بالكامل
        if not config.DEV_CHANNEL:
            return await handler(event, data)

        user = data.get("event_from_user")
        if user is None:
            return await handler(event, data)

        # استثناء المطور من شرط الاشتراك
        if config.DEV_ID and user.id == config.DEV_ID:
            return await handler(event, data)

        bot = data["bot"]
        try:
            member = await bot.get_chat_member(chat_id=config.DEV_CHANNEL, user_id=user.id)
            is_subscribed = member.status in ALLOWED_STATUSES
        except Exception:
            # في حال تعذر التحقق (البوت ليس مشرفاً في القناة مثلاً) نسمح بالمرور
            # لتفادي حجب البوت بالكامل عن كل المستخدمين بسبب خطأ إعداد
            is_subscribed = True

        if is_subscribed:
            return await handler(event, data)

        if isinstance(event, Message):
            await event.answer(FORCE_SUB_TEXT, reply_markup=force_sub_kb())
        elif isinstance(event, CallbackQuery):
            await event.answer("⚠️ يجب الاشتراك في القناة أولاً!", show_alert=True)
            if event.message:
                await event.message.answer(FORCE_SUB_TEXT, reply_markup=force_sub_kb())

        return None
