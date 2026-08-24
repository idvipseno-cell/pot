"""
channels.py
-----------
معالجات إدارة قنوات المستخدم: عرض القنوات، تفعيل/تعطيل الإشعارات، حذف قناة.
"""

from aiogram import F, Router
from aiogram.types import CallbackQuery

from bot.database import crud
from bot.keyboards.inline import channel_manage_kb, channels_list_kb, confirm_delete_kb

router = Router(name="channels")


@router.callback_query(F.data == "my_channels")
async def my_channels_cb(callback: CallbackQuery) -> None:
    channels = await crud.get_user_channels(callback.from_user.id)
    if not channels:
        await callback.answer(
            "لا توجد لديك أي قنوات مسجلة بعد.\nأضف البوت كمشرف في قناتك ليتم تسجيلها تلقائياً.",
            show_alert=True,
        )
        return
    await callback.message.edit_text(
        f"📡 قنواتك المسجلة ({len(channels)}):\n\nاضغط على أي قناة لإدارتها.",
        reply_markup=channels_list_kb(channels),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("channel_"))
async def channel_manage_cb(callback: CallbackQuery) -> None:
    pk_id = int(callback.data.split("_")[1])
    channel = await crud.get_channel_by_pk(pk_id)
    if channel is None or channel.owner_id != callback.from_user.id:
        await callback.answer("⛔ هذه القناة غير موجودة أو لا تملك صلاحية إدارتها.", show_alert=True)
        return

    status = "مفعّلة ✅" if channel.notifications_enabled else "معطّلة ❌"
    text = (
        f"⚙️ <b>إدارة القناة:</b> {channel.title}\n\n"
        f"🆔 المعرف: <code>{channel.channel_id}</code>\n"
        f"🔔 حالة الإشعارات: {status}\n"
        f"📅 تاريخ الإضافة: {channel.added_at.strftime('%Y-%m-%d %H:%M')}"
    )
    await callback.message.edit_text(text, reply_markup=channel_manage_kb(channel))
    await callback.answer()


@router.callback_query(F.data.startswith("toggle_"))
async def toggle_cb(callback: CallbackQuery) -> None:
    pk_id = int(callback.data.split("_")[1])
    channel = await crud.get_channel_by_pk(pk_id)
    if channel is None or channel.owner_id != callback.from_user.id:
        await callback.answer("⛔ غير مصرح لك بهذا الإجراء.", show_alert=True)
        return

    new_status = await crud.toggle_notifications(pk_id)
    await callback.answer("🔔 تم تفعيل الإشعارات" if new_status else "🔕 تم تعطيل الإشعارات")
    await channel_manage_cb(callback)


@router.callback_query(F.data.startswith("delete_"))
async def delete_prompt_cb(callback: CallbackQuery) -> None:
    pk_id = int(callback.data.split("_")[1])
    channel = await crud.get_channel_by_pk(pk_id)
    if channel is None or channel.owner_id != callback.from_user.id:
        await callback.answer("⛔ غير مصرح لك بهذا الإجراء.", show_alert=True)
        return
    await callback.message.edit_text(
        f"⚠️ هل أنت متأكد من حذف قناة «{channel.title}» من قائمة المتابعة؟\n"
        "لن يصلك أي إشعار مغادرة بعد الحذف (يمكنك إعادة إضافتها لاحقاً).",
        reply_markup=confirm_delete_kb(pk_id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("confirmdel_"))
async def confirm_delete_cb(callback: CallbackQuery) -> None:
    pk_id = int(callback.data.split("_")[1])
    channel = await crud.get_channel_by_pk(pk_id)
    if channel is None or channel.owner_id != callback.from_user.id:
        await callback.answer("⛔ غير مصرح لك بهذا الإجراء.", show_alert=True)
        return

    await crud.delete_channel(pk_id)
    await callback.answer("🗑 تم حذف القناة بنجاح", show_alert=True)
    await my_channels_cb(callback)
