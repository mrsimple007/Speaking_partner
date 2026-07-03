"""
Handles message relay between two matched users and in-chat button actions
(Next Partner, End Chat, Report).
"""
from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler, MessageHandler, filters

from bot import db, keyboards
from bot.translations import t
from bot.queue_manager import engine
from bot.handlers.matching import _create_match_and_notify, _build_queue_entry
from bot.utils import typing


from telegram.ext import ApplicationHandlerStop

PARTNER_PREFIX = "👤 Partner: "  # or "\n" if you want it more explicit


async def relay_priority_guard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Runs in an early handler group so an active chat can never be
    intercepted by another catch-all MessageHandler registered later
    in the default group (e.g. premium's receipt-upload handler).

    If the sender is in an active chat, relay immediately and stop all
    further handler processing for this update. Otherwise, do nothing
    and let normal handler resolution continue as before.
    """
    telegram_id = update.effective_user.id
    if engine.is_in_chat(telegram_id):
        await relay_message(update, context)
        raise ApplicationHandlerStop


def priority_relay_handler():
    return MessageHandler(
        filters.ALL & ~filters.COMMAND & ~filters.UpdateType.EDITED_MESSAGE,
        relay_priority_guard,
    )

# ---------------------------------------------------------------
# Message relay — forward everything the user types to their partner
# ---------------------------------------------------------------
async def relay_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    telegram_id = update.effective_user.id
    chat_info = engine.get_chat(telegram_id)

    if not chat_info:
        user = db.get_user_by_telegram_id(telegram_id)
        if user:
            lang = user.get("ui_language", "en")
            await update.message.reply_text(
                t("not_in_chat", lang), reply_markup=keyboards.main_menu_keyboard(lang)
            )
        return

    partner_id = chat_info["partner_id"]
    match_id = chat_info["match_id"]
    await typing(context, partner_id)


    user = db.get_user_by_telegram_id(telegram_id)
    db.log_message(match_id, user["id"])
    db.touch_last_active(telegram_id)

    msg = update.message
    try:
        if msg.text:
            await context.bot.send_message(chat_id=partner_id, text=f"{PARTNER_PREFIX}{msg.text}")
        elif msg.photo:
            await context.bot.send_photo(
                chat_id=partner_id,
                photo=msg.photo[-1].file_id,
                caption=f"{PARTNER_PREFIX}{msg.caption}" if msg.caption else PARTNER_PREFIX.strip(),
            )
        elif msg.sticker:
            await context.bot.send_sticker(chat_id=partner_id, sticker=msg.sticker.file_id)
        elif msg.voice:
            await context.bot.send_voice(chat_id=partner_id, voice=msg.voice.file_id)
        elif msg.video:
            await context.bot.send_video(
                chat_id=partner_id, video=msg.video.file_id,
                caption=f"{PARTNER_PREFIX}{msg.caption}" if msg.caption else PARTNER_PREFIX.strip(),
            )
        elif msg.audio:
            await context.bot.send_audio(
                chat_id=partner_id, audio=msg.audio.file_id,
                caption=f"{PARTNER_PREFIX}{msg.caption}" if msg.caption else PARTNER_PREFIX.strip(),
            )
        elif msg.document:
            await context.bot.send_document(
                chat_id=partner_id, document=msg.document.file_id,
                caption=f"{PARTNER_PREFIX}{msg.caption}" if msg.caption else PARTNER_PREFIX.strip(),
            )
        elif msg.video_note:
            await context.bot.send_video_note(chat_id=partner_id, video_note=msg.video_note.file_id)
    except Exception:
        pass


# ---------------------------------------------------------------
# In-chat button: End Chat
# ---------------------------------------------------------------
async def end_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    telegram_id = update.effective_user.id
    user = db.get_user_by_telegram_id(telegram_id)
    lang = user.get("ui_language", "en")

    chat_info = await engine.end_chat(telegram_id)
    if not chat_info:
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text(
            t("not_in_chat", lang), reply_markup=keyboards.main_menu_keyboard(lang)
        )
        return

    match_id = chat_info["match_id"]
    await typing(context, partner_id)

    partner_id = chat_info["partner_id"]

    db.end_match(match_id, "end")
    db.set_status(telegram_id, "idle")
    db.set_status(partner_id, "idle")

    # Remove chat control keyboard from this user's last message
    await query.edit_message_reply_markup(reply_markup=None)
    await query.message.reply_text(
        t("chat_ended_by_you", lang), reply_markup=keyboards.main_menu_keyboard(lang)
    )

    # Notify partner
    partner_user = db.get_user_by_telegram_id(partner_id)
    partner_lang = partner_user.get("ui_language", "en") if partner_user else "en"
    try:
        await context.bot.send_message(
            chat_id=partner_id,
            text=t("partner_left", partner_lang),
            reply_markup=keyboards.main_menu_keyboard(partner_lang),
        )
    except Exception:
        pass


# ---------------------------------------------------------------
# In-chat button: Next Partner
# ---------------------------------------------------------------
async def next_partner(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    telegram_id = update.effective_user.id
    user = db.get_user_by_telegram_id(telegram_id)
    lang = user.get("ui_language", "en")

    chat_info = await engine.end_chat(telegram_id)
    if chat_info:
        match_id = chat_info["match_id"]
        await typing(context, partner_id)

        partner_id = chat_info["partner_id"]

        db.end_match(match_id, "next")
        db.set_status(partner_id, "idle")

        # Notify old partner that this user left
        partner_user = db.get_user_by_telegram_id(partner_id)
        if partner_user:
            partner_lang = partner_user.get("ui_language", "en")
            try:
                await context.bot.send_message(
                    chat_id=partner_id,
                    text=t("partner_left", partner_lang),
                    reply_markup=keyboards.main_menu_keyboard(partner_lang),
                )
            except Exception:
                pass

    await query.edit_message_reply_markup(reply_markup=None)
    await query.message.reply_text(t("searching_new_partner", lang))

    # Re-queue this user immediately
    db.set_status(telegram_id, "searching")
    entry = _build_queue_entry(user)
    partner_entry = await engine.add_to_queue(entry)

    if partner_entry:
        partner_user = db.get_user_by_telegram_id(partner_entry.telegram_id)
        await _create_match_and_notify(context, user, partner_user)
    else:
        await query.message.reply_text(
            t("searching", lang), reply_markup=keyboards.cancel_search_keyboard(lang)
        )


# ---------------------------------------------------------------
# In-chat button: Report
# ---------------------------------------------------------------
async def report_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    telegram_id = update.effective_user.id
    user = db.get_user_by_telegram_id(telegram_id)
    lang = user.get("ui_language", "en")

    chat_info = engine.get_chat(telegram_id)
    if not chat_info:
        return

    # Store partner id temporarily for use in reason callback
    context.user_data["report_partner_id"] = chat_info["partner_id"]
    context.user_data["report_match_id"] = chat_info["match_id"]

    await query.message.reply_text(
        t("report_reason_prompt", lang),
        reply_markup=keyboards.report_reasons_keyboard(lang),
    )


async def submit_report(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    telegram_id = update.effective_user.id
    user = db.get_user_by_telegram_id(telegram_id)
    lang = user.get("ui_language", "en")

    reason = query.data.split(":")[1]
    partner_telegram_id = context.user_data.pop("report_partner_id", None)
    match_id = context.user_data.pop("report_match_id", None)

    if partner_telegram_id:
        partner_user = db.get_user_by_telegram_id(partner_telegram_id)
        if partner_user:
            db.create_report(
                reporter_id=user["id"],
                reported_id=partner_user["id"],
                reason=reason,
                match_id=match_id,
            )

    await query.edit_message_text(t("report_submitted", lang))

    # After report, end the chat and return to menu
    chat_info = await engine.end_chat(telegram_id)
    if chat_info:
        db.end_match(chat_info["match_id"], "report")
        db.set_status(telegram_id, "idle")
        partner_id = chat_info["partner_id"]
        db.set_status(partner_id, "idle")
        try:
            partner_user = db.get_user_by_telegram_id(partner_id)
            if partner_user:
                partner_lang = partner_user.get("ui_language", "en")
                await context.bot.send_message(
                    chat_id=partner_id,
                    text=t("partner_left", partner_lang),
                    reply_markup=keyboards.main_menu_keyboard(partner_lang),
                )
        except Exception:
            pass

    await query.message.reply_text(
        t("main_menu", lang), reply_markup=keyboards.main_menu_keyboard(lang)
    )


def chat_handlers() -> list:
    return [
        CallbackQueryHandler(end_chat, pattern=r"^chat:end$"),
        CallbackQueryHandler(next_partner, pattern=r"^chat:next$"),
        CallbackQueryHandler(report_prompt, pattern=r"^chat:report$"),
        CallbackQueryHandler(submit_report, pattern=r"^report_reason:"),
        MessageHandler(
            filters.ALL & ~filters.COMMAND & ~filters.UpdateType.EDITED_MESSAGE,
            relay_message,
        ),
    ]
