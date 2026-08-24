"""
start.py
--------
معالج أمر /start وقوائم التنقل الرئيسية (المساعدة، رجوع، تحقق من الاشتراك).
"""

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message

from bot.database import crud
from bot.keyboards.inline import main_menu_kb
from config import config

router = Router(name="start")

WELCOME_TEXT = (
    "👋 أهلاً بك <b>{name}</b> في بوت مراقبة القنوات!\n\n"
    "🔹 يتيح لك هذا البوت مراقبة قنواتك بشكل احترافي، حيث يرسل لك إشعاراً فورياً "
    "وتفصيلياً كلما غادر أحد الأعضاء قناتك.\n\n"
    "📌 <b>طريقة الاستخدام:</b>\n"
    "1️⃣ أضف البوت كمشرف (Admin) في قناتك.\n"
    "2️⃣ سيتم تسجيل القناة تلقائياً باسمك في قاعدة البيانات.\n"
    "3️⃣ استقبل إشعارات مغادرة الأعضاء فوراً في الخاص.\n\n"
    "استخدم الأزرار أدناه للبدء 👇"
)

HELP_TEXT = (
    "📖 <b>دليل الاستخدام</b>\n\n"
    "• أضف البوت مشرفاً في قناتك بصلاحيات كاملة (يفضل تفعيل جميع الصلاحيات).\n"
    "• سيتم تسجيل القناة تلقائياً باسمك فور رفع البوت كمشرف فيها.\n"
    "• من قائمة «قنواتي» يمكنك تفعيل/تعطيل الإشعارات أو حذف أي قناة من المتابعة.\n"
    "• عند مغادرة أي عضو للقناة، ستصلك رسالة خاصة تحتوي على بياناته الكاملة.\n"
)


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await crud.get_or_create_user(message.from_user.id, message.from_user.username, message.from_user.full_name)
    bot_info = await message.bot.get_me()
    await message.answer(
        WELCOME_TEXT.format(name=message.from_user.full_name),
        reply_markup=main_menu_kb(bot_info.username),
    )


@router.callback_query(F.data == "check_sub")
async def check_sub_cb(callback: CallbackQuery) -> None:
    # في هذه المرحلة يكون الـ Middleware قد تحقق فعلاً من الاشتراك للسماح بالوصول هنا
    await crud.get_or_create_user(callback.from_user.id, callback.from_user.username, callback.from_user.full_name)
    bot_info = await callback.bot.get_me()
    await callback.message.edit_text(
        "✅ تم التحقق من اشتراكك بنجاح!\n\n" + WELCOME_TEXT.format(name=callback.from_user.full_name),
        reply_markup=main_menu_kb(bot_info.username),
    )
    await callback.answer("تم التحقق ✅")


@router.callback_query(F.data == "back_main")
async def back_main_cb(callback: CallbackQuery) -> None:
    bot_info = await callback.bot.get_me()
    await callback.message.edit_text(
        WELCOME_TEXT.format(name=callback.from_user.full_name),
        reply_markup=main_menu_kb(bot_info.username),
    )
    await callback.answer()


@router.callback_query(F.data == "help")
async def help_cb(callback: CallbackQuery) -> None:
    bot_info = await callback.bot.get_me()
    text = HELP_TEXT
    if config.DEV_USERNAME:
        text += f"\nللدعم الفني تواصل مع: @{config.DEV_USERNAME}"
    await callback.message.edit_text(text, reply_markup=main_menu_kb(bot_info.username))
    await callback.answer()
