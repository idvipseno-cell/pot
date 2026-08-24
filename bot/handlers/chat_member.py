"""
chat_member.py
--------------
- تسجيل القناة تلقائياً عند رفع البوت مشرفاً فيها (my_chat_member).
- رصد مغادرة/طرد الأعضاء من القناة وإشعار مالكها (chat_member).

ملاحظة مهمة: حتى تصل تحديثات chat_member الخاصة بأعضاء القناة (وليس البوت نفسه)،
يجب أن يكون البوت مشرفاً في القناة، ويجب تمرير "chat_member" ضمن allowed_updates
عند بدء الاستماع للتحديثات (تم ذلك في main.py).
"""

from datetime import datetime

from aiogram import F, Router
from aiogram.enums import ChatMemberStatus, ChatType
from aiogram.types import ChatMemberUpdated

from bot.database import crud

router = Router(name="chat_member")

ACTIVE_STATUSES = {
    ChatMemberStatus.MEMBER,
    ChatMemberStatus.ADMINISTRATOR,
    ChatMemberStatus.CREATOR,
    ChatMemberStatus.RESTRICTED,
}
INACTIVE_STATUSES = {ChatMemberStatus.LEFT, ChatMemberStatus.KICKED}


@router.my_chat_member(F.chat.type == ChatType.CHANNEL)
async def on_bot_status_change(event: ChatMemberUpdated) -> None:
    """يُستدعى عند تغيّر حالة عضوية البوت نفسه داخل القناة (تمت إضافته/ترقيته/إزالته)."""
    old_status = event.old_chat_member.status
    new_status = event.new_chat_member.status

    # الحالة 1: تمت ترقية البوت إلى مشرف -> تسجيل القناة
    if new_status == ChatMemberStatus.ADMINISTRATOR and old_status != ChatMemberStatus.ADMINISTRATOR:
        owner = event.from_user  # الشخص الذي قام برفع البوت كمشرف
        await crud.get_or_create_user(owner.id, owner.username, owner.full_name)
        await crud.add_or_update_channel(
            channel_id=event.chat.id,
            title=event.chat.title or "بدون اسم",
            owner_id=owner.id,
        )
        try:
            await event.bot.send_message(
                owner.id,
                (
                    "✅ <b>تم تسجيل قناتك بنجاح!</b>\n\n"
                    f"📡 القناة: <b>{event.chat.title}</b>\n"
                    f"🆔 المعرف: <code>{event.chat.id}</code>\n\n"
                    "ستصلك من الآن إشعارات فورية وتفصيلية عند مغادرة أي عضو لهذه القناة."
                ),
            )
        except Exception:
            # قد يكون المستخدم لم يبدأ محادثة خاصة مع البوت بعد
            pass

    # الحالة 2: تمت إزالة البوت أو تخفيض صلاحياته إلى غير مشرف -> إيقاف المراقبة
    elif new_status in INACTIVE_STATUSES or (
        new_status == ChatMemberStatus.MEMBER and old_status == ChatMemberStatus.ADMINISTRATOR
    ):
        channel = await crud.get_channel_by_telegram_id(event.chat.id)
        if channel:
            try:
                await event.bot.send_message(
                    channel.owner_id,
                    f"⚠️ تمت إزالة صلاحيات الإشراف عن البوت في قناة «{channel.title}»، "
                    "وتم إيقاف مراقبتها تلقائياً.",
                )
            except Exception:
                pass
            await crud.delete_channel(channel.id)


@router.chat_member(F.chat.type == ChatType.CHANNEL)
async def on_member_status_change(event: ChatMemberUpdated) -> None:
    """يُستدعى عند تغيّر حالة أي عضو آخر داخل القناة (انضمام/مغادرة/طرد)."""
    old_status = event.old_chat_member.status
    new_status = event.new_chat_member.status

    left_now = new_status in INACTIVE_STATUSES
    was_active = old_status in ACTIVE_STATUSES

    if not (left_now and was_active):
        return  # ليس حدث مغادرة فعلي (مثلاً: انضمام جديد)

    channel = await crud.get_channel_by_telegram_id(event.chat.id)
    if channel is None or not channel.notifications_enabled:
        return

    member = event.old_chat_member.user
    full_name = member.full_name or "غير معروف"

    if member.username:
        username_line = f"<a href='https://t.me/{member.username}'>@{member.username}</a>"
    else:
        username_line = "لا يوجد معرف يوزر (Username)"

    # ملاحظة: تليكرام لا يسمح للبوتات بالحصول على رقم هاتف أي عضو إطلاقاً،
    # إلا في حال شارك العضو رقمه صراحةً مع هذا البوت مسبقاً عبر زر "مشاركة جهة الاتصال".
    phone_line = (
        "🔒 غير متوفر — لا يمكن لتليكرام تزويد البوتات برقم الهاتف "
        "إلا إذا شاركه العضو مسبقاً مع البوت مباشرة (سياسة خصوصية تليكرام)."
    )

    leave_type = "تم طرده من القناة 🚫" if new_status == ChatMemberStatus.KICKED else "غادر القناة طوعاً 🚪"
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    text = (
        "🔔 <b>تنبيه: مغادرة عضو من قناتك</b>\n\n"
        f"📡 القناة: <b>{channel.title}</b>\n"
        f"👤 الاسم الكامل: {full_name}\n"
        f"🔗 المعرف: {username_line}\n"
        f"🆔 الآيدي (User ID): <code>{member.id}</code>\n"
        f"📱 رقم الهاتف: {phone_line}\n"
        f"📌 نوع المغادرة: {leave_type}\n"
        f"🕒 التاريخ والوقت: {now_str}"
    )

    try:
        await event.bot.send_message(channel.owner_id, text, disable_web_page_preview=True)
    except Exception:
        pass
