"""
main.py
-------
نقطة انطلاق البوت: تهيئة قاعدة البيانات، تسجيل الميدل وير والراوترات، وبدء الاستماع للتحديثات.
"""

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.database.db import init_db
from bot.handlers import admin, channels, chat_member, start
from bot.middlewares.force_sub import ForceSubMiddleware
from config import config


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger = logging.getLogger(__name__)

    if not config.BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN غير موجود! تأكد من إعداد ملف .env بشكل صحيح (راجع .env.example).")

    logger.info("تهيئة قاعدة البيانات...")
    await init_db()

    bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    # تسجيل الميدل وير (الاشتراك الإجباري) على الرسائل والأزرار فقط
    dp.message.middleware(ForceSubMiddleware())
    dp.callback_query.middleware(ForceSubMiddleware())

    # تسجيل الراوترات
    dp.include_router(admin.router)
    dp.include_router(start.router)
    dp.include_router(channels.router)
    dp.include_router(chat_member.router)

    await bot.delete_webhook(drop_pending_updates=True)

    logger.info("تم تشغيل البوت بنجاح، بانتظار التحديثات...")
    await dp.start_polling(
        bot,
        allowed_updates=["message", "callback_query", "chat_member", "my_chat_member"],
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("تم إيقاف البوت يدوياً.")
