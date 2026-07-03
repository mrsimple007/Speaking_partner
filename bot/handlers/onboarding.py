from datetime import datetime

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    CallbackQueryHandler,
)

from bot import config, db, keyboards
from bot.translations import t

import logging
logger = logging.getLogger(__name__)


# Conversation states
CHOOSING_UI_LANG, NATIVE_LANG, LEARNING_LANG, LEVEL, GENDER, INTERESTS = range(6)


# ───────────────────────────────────────────────────────────────
# NEW-USER ADMIN NOTIFICATION
# ───────────────────────────────────────────────────────────────
async def _notify_admins_new_user(context, telegram_id: int, tg_user) -> None:
    """Send a short new-user card to all notification admins."""
    try:
        # Count total users
        total = db.supabase.table("lingo_users").select("id", count="exact").execute().count or "?"

        username = tg_user.username
        name     = tg_user.full_name or f"User_{telegram_id}"
        now      = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        text = (
            f"👤 <b>New User Joined</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🆔 ID: <code>{telegram_id}</code>\n"
            f"📛 Name: {name}\n"
        )
        if username:
            text += f"🔗 Username: @{username}\n"
        text += (
            f"📅 Date: {now}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👥 Total users: <b>{total}</b>"
        )

        for admin_id in config.ADMIN_IDS:
            try:
                await context.bot.send_message(
                    chat_id=admin_id, text=text, parse_mode=ParseMode.HTML
                )
            except Exception as e:
                pass  # don't crash onboarding if admin notify fails
    except Exception:
        pass


# ───────────────────────────────────────────────────────────────
# /start
# ───────────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    telegram_id = update.effective_user.id
    user = db.get_user_by_telegram_id(telegram_id)

    if user and user.get("onboarding_step") is None:
        # Already onboarded → go straight to main menu
        from bot.handlers.menu import show_main_menu
        await show_main_menu(update, context, user["ui_language"])
        return ConversationHandler.END

    # Brand-new user → show language picker and notify admins
    is_new = user is None
    await update.message.reply_text(
        "Tilni tanlang / Выберите язык / Choose language:",
        reply_markup=keyboards.ui_language_keyboard(),
    )

    if is_new:
        await _notify_admins_new_user(context, telegram_id, update.effective_user)

    return CHOOSING_UI_LANG


# ───────────────────────────────────────────────────────────────
# STEP 1 — UI language
# ───────────────────────────────────────────────────────────────
async def choose_ui_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    lang = query.data.split(":")[1]
    telegram_id = update.effective_user.id
    tg_user = update.effective_user

    user = db.get_user_by_telegram_id(telegram_id)
    if not user:
        user = db.create_user(
            telegram_id,
            ui_language=lang,
            first_name=tg_user.first_name or "",
            last_name=tg_user.last_name or "",
            username=tg_user.username or "",
        )
        logger.info("New user created: telegram_id=%s ui_language=%s", telegram_id, lang)
    else:
        db.update_user(telegram_id, {"ui_language": lang})
        logger.info("Existing user updated ui_language: telegram_id=%s -> %s", telegram_id, lang)

    context.user_data["ui_language"] = lang
    context.user_data["interests_selected"] = set()

    await query.edit_message_text(f"{t('welcome', lang)}\n\n{t('start_intro', lang)}")
    await query.message.reply_text(
        t("ask_native_language", lang),
        reply_markup=keyboards.language_keyboard(lang, "native"),
    )
    return NATIVE_LANG


# ───────────────────────────────────────────────────────────────
# STEP 2 — Native language
# ───────────────────────────────────────────────────────────────
async def choose_native_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    lang   = context.user_data.get("ui_language", "en")
    native = query.data.split(":")[1]
    context.user_data["native_language"] = native

    await query.edit_message_text(
        t("ask_learning_language", lang),
        reply_markup=keyboards.language_keyboard(lang, "learning"),
    )
    return LEARNING_LANG


# ───────────────────────────────────────────────────────────────
# STEP 3 — Learning language
# ───────────────────────────────────────────────────────────────
async def choose_learning_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    lang     = context.user_data.get("ui_language", "en")
    learning = query.data.split(":")[1]
    context.user_data["learning_language"] = learning

    await query.edit_message_text(
        t("ask_level", lang),
        reply_markup=keyboards.level_keyboard(lang),
    )
    return LEVEL


# ───────────────────────────────────────────────────────────────
# STEP 4 — Level
# ───────────────────────────────────────────────────────────────
async def choose_level(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    lang  = context.user_data.get("ui_language", "en")
    level = query.data.split(":")[1]
    context.user_data["level"] = level

    await query.edit_message_text(
        t("ask_gender", lang),
        reply_markup=keyboards.gender_keyboard(lang),
    )
    return GENDER


# ───────────────────────────────────────────────────────────────
# STEP 5 — Gender
# ───────────────────────────────────────────────────────────────
async def choose_gender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    lang   = context.user_data.get("ui_language", "en")
    gender = query.data.split(":")[1]
    context.user_data["gender"] = gender

    await query.edit_message_text(
        t("ask_interests", lang),
        reply_markup=keyboards.interests_keyboard(lang, context.user_data["interests_selected"]),
    )
    return INTERESTS


# ───────────────────────────────────────────────────────────────
# STEP 6 — Interests (toggles)
# ───────────────────────────────────────────────────────────────
async def toggle_interest(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query    = update.callback_query
    lang     = context.user_data.get("ui_language", "en")
    code     = query.data.split(":")[1]
    selected = context.user_data.setdefault("interests_selected", set())

    if code in selected:
        selected.discard(code)
    elif len(selected) < 5:
        selected.add(code)
    else:
        await query.answer(t("max_interests_reached", lang), show_alert=True)
        return INTERESTS

    await query.answer()
    await query.edit_message_reply_markup(
        reply_markup=keyboards.interests_keyboard(lang, selected)
    )
    return INTERESTS


async def finish_interests(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query       = update.callback_query
    await query.answer()
    lang        = context.user_data.get("ui_language", "en")
    telegram_id = update.effective_user.id

    user = db.update_user(
        telegram_id,
        {
            "native_language":   context.user_data.get("native_language"),
            "learning_language": context.user_data.get("learning_language"),
            "level":             context.user_data.get("level"),
            "gender":            context.user_data.get("gender"),
            "onboarding_step":   None,
            "status":            "idle",
        },
    )
    db.set_user_interests(user["id"], list(context.user_data.get("interests_selected", set())))

    logger.info(
        "Onboarding completed: telegram_id=%s native=%s learning=%s level=%s",
        telegram_id,
        context.user_data.get("native_language"),
        context.user_data.get("learning_language"),
        context.user_data.get("level"),
    )

    await query.edit_message_text(t("interests_saved", lang))

    from bot.handlers.menu import show_main_menu
    await show_main_menu(update, context, lang)
    return ConversationHandler.END


# ───────────────────────────────────────────────────────────────
# CONVERSATION HANDLER
# ───────────────────────────────────────────────────────────────
def build_onboarding_conversation() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING_UI_LANG: [CallbackQueryHandler(choose_ui_language, pattern=r"^ui_lang:")],
            NATIVE_LANG:      [CallbackQueryHandler(choose_native_language, pattern=r"^native:")],
            LEARNING_LANG:    [CallbackQueryHandler(choose_learning_language, pattern=r"^learning:")],
            LEVEL:            [CallbackQueryHandler(choose_level, pattern=r"^level:")],
            GENDER:           [CallbackQueryHandler(choose_gender, pattern=r"^gender:")],
            INTERESTS: [
                CallbackQueryHandler(finish_interests, pattern=r"^interest_done$"),
                CallbackQueryHandler(toggle_interest,  pattern=r"^interest:"),
            ],
        },
        fallbacks=[CommandHandler("start", start)],
        name="onboarding",
        persistent=False,
    )
