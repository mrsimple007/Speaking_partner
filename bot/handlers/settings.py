from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler

from bot import db, keyboards
from bot.translations import t


async def show_settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    telegram_id = update.effective_user.id
    user = db.get_user_by_telegram_id(telegram_id)
    lang = user.get("ui_language", "en")
    text = t("settings_header", lang)

    if update.callback_query:
        await update.callback_query.message.reply_text(
            text, reply_markup=keyboards.settings_keyboard(lang)
        )
    else:
        await update.message.reply_text(text, reply_markup=keyboards.settings_keyboard(lang))


async def change_ui_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    telegram_id = update.effective_user.id
    user = db.get_user_by_telegram_id(telegram_id)
    lang = user.get("ui_language", "en")
    await query.message.reply_text(
        t("choose_ui_language", lang), reply_markup=keyboards.ui_language_keyboard()
    )


async def apply_new_ui_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    telegram_id = update.effective_user.id
    new_lang = query.data.split(":")[1]
    db.update_user(telegram_id, {"ui_language": new_lang})
    await query.edit_message_text(t("settings_header", new_lang))
    from bot.handlers.menu import show_main_menu
    await show_main_menu(update, context, new_lang)


async def ask_delete_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    telegram_id = update.effective_user.id
    user = db.get_user_by_telegram_id(telegram_id)
    lang = user.get("ui_language", "en")
    await query.message.reply_text(
        t("delete_confirm", lang), reply_markup=keyboards.confirm_delete_keyboard(lang)
    )


async def confirm_delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    telegram_id = update.effective_user.id
    user = db.get_user_by_telegram_id(telegram_id)
    lang = user.get("ui_language", "en") if user else "en"

    # Remove from queue/chat first
    from bot.queue_manager import engine
    await engine.remove_from_queue(telegram_id)
    chat_info = await engine.end_chat(telegram_id)
    if chat_info:
        partner_id = chat_info["partner_id"]
        db.set_status(partner_id, "idle")
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

    db.delete_user(telegram_id)
    await query.edit_message_text(t("account_deleted", lang))


async def cancel_delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    telegram_id = update.effective_user.id
    user = db.get_user_by_telegram_id(telegram_id)
    lang = user.get("ui_language", "en")
    await query.edit_message_text(t("settings_header", lang), reply_markup=keyboards.settings_keyboard(lang))


def settings_handlers() -> list:
    return [
        CallbackQueryHandler(change_ui_language, pattern=r"^settings:ui_lang$"),
        CallbackQueryHandler(apply_new_ui_language, pattern=r"^ui_lang:"),
        CallbackQueryHandler(ask_delete_confirm, pattern=r"^settings:delete$"),
        CallbackQueryHandler(confirm_delete, pattern=r"^delete:confirm$"),
        CallbackQueryHandler(cancel_delete, pattern=r"^delete:cancel$"),
    ]
