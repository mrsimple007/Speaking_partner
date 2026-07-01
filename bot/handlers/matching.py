from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler

from bot import db, keyboards
from bot.translations import t, language_name, interest_name
from bot.queue_manager import engine, QueueEntry


def _build_queue_entry(user: dict) -> QueueEntry:
    interests = set(db.get_user_interests(user["id"]))
    filter_gender = None
    filter_interests = set()
    if user.get("premium"):
        prefs = user.get("_premium_filters", {})  # set transiently by premium settings flow
        filter_gender = prefs.get("gender")
        filter_interests = set(prefs.get("interests", []))
    return QueueEntry(
        telegram_id=user["telegram_id"],
        native_language=user["native_language"],
        learning_language=user["learning_language"],
        level=user["level"],
        gender=user["gender"],
        interests=interests,
        premium=bool(user.get("premium")),
        filter_gender=filter_gender,
        filter_interests=filter_interests,
    )


async def find_partner_entry(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    telegram_id = update.effective_user.id
    user = db.get_user_by_telegram_id(telegram_id)
    lang = user.get("ui_language", "en")

    if not user.get("native_language") or not user.get("learning_language"):
        await update.callback_query.message.reply_text(t("complete_onboarding_first", lang))
        return

    if engine.is_in_chat(telegram_id):
        await update.callback_query.message.reply_text(t("already_in_chat", lang))
        return

    if engine.is_in_queue(telegram_id):
        await update.callback_query.message.reply_text(t("already_in_queue", lang))
        return

    db.set_status(telegram_id, "searching")
    msg = await update.callback_query.message.reply_text(
        t("searching", lang), reply_markup=keyboards.cancel_search_keyboard(lang)
    )

    entry = _build_queue_entry(user)
    partner_entry = await engine.add_to_queue(entry)

    if partner_entry is None:
        # stays in queue; background poller (see main.py job queue) will
        # notify both users once a later joiner matches them.
        context.bot_data.setdefault("waiting_messages", {})[telegram_id] = msg.message_id
        return

    # Immediate match
    partner_user = db.get_user_by_telegram_id(partner_entry.telegram_id)
    await _create_match_and_notify(context, user, partner_user)


async def _create_match_and_notify(context: ContextTypes.DEFAULT_TYPE, user_a: dict, user_b: dict) -> None:
    match = db.create_match(user_a["id"], user_b["id"])
    await engine.start_chat(user_a["telegram_id"], user_b["telegram_id"], match["id"])

    db.set_status(user_a["telegram_id"], "chatting")
    db.set_status(user_b["telegram_id"], "chatting")

    await _notify_match(context, user_a, user_b)
    await _notify_match(context, user_b, user_a)


async def _notify_match(context: ContextTypes.DEFAULT_TYPE, recipient: dict, partner: dict) -> None:
    lang = recipient.get("ui_language", "en")
    interests = db.get_user_interests(partner["id"])
    interests_str = ", ".join(interest_name(c, lang) for c in interests) or "-"

    text = t(
        "partner_found",
        lang,
        learning=language_name(partner["learning_language"], lang),
        level=partner["level"],
        interests=interests_str,
    )
    await context.bot.send_message(
        chat_id=recipient["telegram_id"],
        text=text,
        reply_markup=keyboards.chat_controls_keyboard(lang),
    )


async def cancel_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    telegram_id = update.effective_user.id
    user = db.get_user_by_telegram_id(telegram_id)
    lang = user.get("ui_language", "en")

    await engine.remove_from_queue(telegram_id)
    db.set_status(telegram_id, "idle")
    context.bot_data.setdefault("waiting_messages", {}).pop(telegram_id, None)

    await query.edit_message_text(t("search_cancelled", lang))
    from bot.handlers.menu import show_main_menu

    await show_main_menu(update, context, lang)


async def queue_matchmaking_tick(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Periodic job (registered in main.py JobQueue) that re-scans the
    waiting queue so two people who joined without a match at insert
    time can still be paired once a compatible partner appears. The
    add_to_queue() call already attempts an immediate match on insert;
    this tick catches edge cases (e.g. both inserted in the same
    millisecond) and acts as a safety net."""
    async with engine._lock:
        entries = list(engine._queue.values())

    matched_ids = set()
    for entry in entries:
        if entry.telegram_id in matched_ids:
            continue
        async with engine._lock:
            if entry.telegram_id not in engine._queue:
                continue
            partner = engine._find_best_match(entry)
            if not partner or partner.telegram_id in matched_ids:
                continue
            del engine._queue[entry.telegram_id]
            del engine._queue[partner.telegram_id]

        matched_ids.add(entry.telegram_id)
        matched_ids.add(partner.telegram_id)

        user_a = db.get_user_by_telegram_id(entry.telegram_id)
        user_b = db.get_user_by_telegram_id(partner.telegram_id)
        if user_a and user_b:
            await _create_match_and_notify(context, user_a, user_b)


def matching_handlers() -> list:
    return [CallbackQueryHandler(cancel_search, pattern=r"^search:cancel$")]
