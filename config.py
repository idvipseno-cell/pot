"""
config.py
---------
قراءة متغيرات البيئة الخاصة بالبوت من ملف .env
"""

import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


def _get_int(name: str, default: int = 0) -> int:
    value = os.getenv(name, str(default))
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


@dataclass
class Config:
    # توكن البوت الذي تحصل عليه من @BotFather
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")

    # آيدي المطور الرئيسي (رقمي) - يُستثنى تلقائياً من شرط الاشتراك الإجباري
    DEV_ID: int = field(default_factory=lambda: _get_int("DEV_ID", 0))

    # قناة الاشتراك الإجباري - يمكن أن تكون بصيغة @username أو -100xxxxxxxxxx
    DEV_CHANNEL: str = os.getenv("DEV_CHANNEL", "")

    # يوزر المطور (بدون @) ليتم استخدامه في أزرار التواصل
    DEV_USERNAME: str = os.getenv("DEV_USERNAME", "")

    # مسار قاعدة البيانات
    DB_PATH: str = os.getenv("DB_PATH", "bot_database.db")


config = Config()
