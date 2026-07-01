from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
)

from bot import db, keyboards
from bot.translations import t, language_name, interest_name

EDIT_NATIVE, EDIT_LEARNING, EDIT_LEVEL, EDIT_GENDER, EDIT_INTERESTS = range(10, 15)


def _format_profile(user: dict, interests: list, lang: str) -> str:
    native = language_name(user.get("native_language", ""), lang)
    learning = language_name(user.get("learning_language", ""), lang)
    level = user.get("level", "-")
    gender_key = f"gender_{user.get('gender', '')}"
    gender = t(gender_key, lang) if gender_key in ("gender_male", "gender_female") else "-"
    interests_str = ", ".join(interest_name(c, lang) for c in interests) or "-"
    premium = "✅" if user.get("premium") else "❌"
    return t(
        "profile_body",
        lang,
        native=native,
        learning=learning,
        level=level,
        gender=gender,
        interests=interests_str,
        premium=premium,
    )


async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    telegram_id = update.effective_user.id
    user = db.get_user_by_telegram_id(telegram_id)
    lang = user.get("ui_language", "en")
    interests = db.get_user_interests(user["id"])

    header = t("profile_header", lang)
    body = _format_profile(user, interests, lang)
    text = f"{header}\n\n{body}"

    if update.callback_query:
        await update.callback_query.message.reply_text(
            text, reply_markup=keyboards.settings_keyboard(lang)
        )
    else:
        await update.message.reply_text(text, reply_markup=keyboards.settings_keyboard(lang))


# ---------------------------------------------------------------
# Edit profile — re-uses onboarding keyboards inline
# ---------------------------------------------------------------
async def start_edit_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    telegram_id = update.effective_user.id
    user = db.get_user_by_telegram_id(telegram_id)
    lang = user.get("ui_language", "en")
    context.user_data["ui_language"] = lang
    context.user_data["interests_selected"] = set(db.get_user_interests(user["id"]))

    await query.message.reply_text(
        t("ask_native_language", lang),
        reply_markup=keyboards.language_keyboard(lang, "edit_native"),
    )
    return EDIT_NATIVE


async def edit_native(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("ui_language", "en")
    context.user_data["native_language"] = query.data.split(":")[1]
    await query.edit_message_text(
        t("ask_learning_language", lang),
        reply_markup=keyboards.language_keyboard(lang, "edit_learning"),
    )
    return EDIT_LEARNING


async def edit_learning(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("ui_language", "en")
    context.user_data["learning_language"] = query.data.split(":")[1]
    await query.edit_message_text(
        t("ask_level", lang), reply_markup=keyboards.level_keyboard(lang, "edit_level")
    )
    return EDIT_LEVEL


async def edit_level(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("ui_language", "en")
    context.user_data["level"] = query.data.split(":")[1]
    await query.edit_message_text(
        t("ask_gender", lang), reply_markup=keyboards.gender_keyboard(lang, "edit_gender")
    )
    return EDIT_GENDER


async def edit_gender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("ui_language", "en")
    context.user_data["gender"] = query.data.split(":")[1]
    await query.edit_message_text(
        t("ask_interests", lang),
        reply_markup=keyboards.interests_keyboard(lang, context.user_data["interests_selected"]),
    )
    return EDIT_INTERESTS


async def edit_toggle_interest(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    lang = context.user_data.get("ui_language", "en")
    code = query.data.split(":")[1]
    selected = context.user_data.setdefault("interests_selected", set())

    if code in selected:
        selected.discard(code)
    elif len(selected) < 5:
        selected.add(code)
    else:
        await query.answer(t("max_interests_reached", lang), show_alert=True)
        return EDIT_INTERESTS

    await query.answer()
    await query.edit_message_reply_markup(
        reply_markup=keyboards.interests_keyboard(lang, selected)
    )
    return EDIT_INTERESTS


async def edit_finish(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("ui_language", "en")
    telegram_id = update.effective_user.id

    user = db.update_user(
        telegram_id,
        {
            "native_language": context.user_data.get("native_language"),
            "learning_language": context.user_data.get("learning_language"),
            "level": context.user_data.get("level"),
            "gender": context.user_data.get("gender"),
        },
    )
    db.set_user_interests(user["id"], list(context.user_data.get("interests_selected", set())))

    await query.edit_message_text(t("interests_saved", lang))
    from bot.handlers.menu import show_main_menu

    await show_main_menu(update, context, lang)
    return ConversationHandler.END


def build_edit_profile_conversation() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(start_edit_profile, pattern=r"^settings:edit_profile$")
        ],
        states={
            EDIT_NATIVE: [CallbackQueryHandler(edit_native, pattern=r"^edit_native:")],
            EDIT_LEARNING: [CallbackQueryHandler(edit_learning, pattern=r"^edit_learning:")],
            EDIT_LEVEL: [CallbackQueryHandler(edit_level, pattern=r"^edit_level:")],
            EDIT_GENDER: [CallbackQueryHandler(edit_gender, pattern=r"^edit_gender:")],
            EDIT_INTERESTS: [
                CallbackQueryHandler(edit_finish, pattern=r"^interest_done$"),
                CallbackQueryHandler(edit_toggle_interest, pattern=r"^interest:"),
            ],
        },
        fallbacks=[],
        name="edit_profile",
        persistent=False,
        per_message=False,
    )