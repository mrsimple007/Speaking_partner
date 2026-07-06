from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler

from bot import db, keyboards
from bot.translations import t
from bot.handlers.profile import format_profile_text, format_profile_body
from bot.utils import typing

async def show_main_menu(update, context, lang):
    telegram_id = update.effective_user.id
    await typing(context, telegram_id)  # optional, from earlier fix

    user = db.get_user_by_telegram_id(telegram_id)
    interests = db.get_user_interests(user["id"])

    name = update.effective_user.first_name or ""
    header = t("main_menu_header", lang, name=name)
    body = format_profile_body(user, interests, lang)
    footer = t("main_menu_footer", lang)
    text = f"{header}\n\n{body}\n{footer}"

    if update.callback_query:
        await update.callback_query.message.reply_text(text, reply_markup=keyboards.main_menu_keyboard(lang))
    else:
        await update.message.reply_text(text, reply_markup=keyboards.main_menu_keyboard(lang))



async def menu_router(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Routes top-level main-menu button presses to the right module.
    Imported lazily inside to avoid circular imports."""
    query = update.callback_query
    await query.answer()
    action = query.data.split(":")[1]
    telegram_id = update.effective_user.id
    user = db.get_user_by_telegram_id(telegram_id)
    if not user:
        return
    lang = user.get("ui_language", "en")

    if action == "find":
        from bot.handlers.matching import find_partner_entry

        await find_partner_entry(update, context)
    elif action == "profile":
        from bot.handlers.profile import show_profile

        await show_profile(update, context)
    elif action == "invite":
        from bot.referral import show_invite

        await show_invite(update, context)
    elif action == "premium":
        from bot.handlers.premium import show_premium

        await show_premium(update, context)
    elif action == "settings":
        from bot.handlers.settings import show_settings

        await show_settings(update, context)


def menu_handler() -> CallbackQueryHandler:
    return CallbackQueryHandler(menu_router, pattern=r"^menu:")