"""
inline.py
---------
جميع لوحات المفاتيح الشفافة (Inline Keyboards) المستخدمة في البوت.
"""

from typing import Iterable

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.database.models import Channel
from config import config


def _channel_join_url() -> str:
    channel = config.DEV_CHANNEL
    if channel.startswith("@"):
        return f"https://t.me/{channel[1:]}"
    if channel.startswith("https://") or channel.startswith("http://"):
        return channel
    return f"https://t.me/{channel}"


def main_menu_kb(bot_username: str) -> InlineKeyboardMarkup:
    """القائمة الرئيسية التي تظهر بعد /start."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="➕ إضافة البوت إلى قناتك",
            url=f"https://t.me/{bot_username}?startchannel=true&admin=delete_messages+invite_users+restrict_members",
        )
    )
    builder.row(
        InlineKeyboardButton(text="📡 قنواتي", callback_data="my_channels"),
        InlineKeyboardButton(text="ℹ️ المساعدة", callback_data="help"),
    )
    if config.DEV_USERNAME:
        builder.row(
            InlineKeyboardButton(text="👨‍💻 تواصل مع المطور", url=f"https://t.me/{config.DEV_USERNAME}")
        )
    return builder.as_markup()


def force_sub_kb() -> InlineKeyboardMarkup:
    """لوحة الاشتراك الإجباري."""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📢 اشترك في القناة", url=_channel_join_url()))
    builder.row(InlineKeyboardButton(text="✅ تحقق من الاشتراك", callback_data="check_sub"))
    return builder.as_markup()


def channels_list_kb(channels: Iterable[Channel]) -> InlineKeyboardMarkup:
    """قائمة قنوات المستخدم."""
    builder = InlineKeyboardBuilder()
    for ch in channels:
        status_icon = "🔔" if ch.notifications_enabled else "🔕"
        builder.row(
            InlineKeyboardButton(text=f"{status_icon} {ch.title}", callback_data=f"channel_{ch.id}")
        )
    builder.row(InlineKeyboardButton(text="🔙 رجوع للقائمة الرئيسية", callback_data="back_main"))
    return builder.as_markup()


def channel_manage_kb(channel: Channel) -> InlineKeyboardMarkup:
    """لوحة إدارة قناة محددة."""
    builder = InlineKeyboardBuilder()
    toggle_text = "🔕 تعطيل الإشعارات" if channel.notifications_enabled else "🔔 تفعيل الإشعارات"
    builder.row(InlineKeyboardButton(text=toggle_text, callback_data=f"toggle_{channel.id}"))
    builder.row(InlineKeyboardButton(text="🗑 حذف القناة من المتابعة", callback_data=f"delete_{channel.id}"))
    builder.row(InlineKeyboardButton(text="🔙 رجوع لقنواتي", callback_data="my_channels"))
    return builder.as_markup()


def confirm_delete_kb(pk_id: int) -> InlineKeyboardMarkup:
    """تأكيد حذف قناة."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ تأكيد الحذف", callback_data=f"confirmdel_{pk_id}"),
        InlineKeyboardButton(text="❌ إلغاء", callback_data=f"channel_{pk_id}"),
    )
    return builder.as_markup()
