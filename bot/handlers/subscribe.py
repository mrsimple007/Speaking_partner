"""
Force-subscription gate: users must join every channel in
config.REQUIRED_CHANNELS before using any post-onboarding feature
(Find Partner, Profile, Settings, Premium, Invite/Leaderboard).

Deliberately NOT checked during onboarding itself — a brand-new user
must always be able to finish signing up. The gate is applied at the
entry points reached *after* onboarding: see the `ensure_subscribed()`
calls in handlers/menu.py, handlers/profile.py, handlers/referral.py,
and the /menu /profile /premium shortcuts in main.py.

Toggle this whole feature off (or change the channel list) via
FORCE_SUBSCRIPTION_ENABLED / REQUIRED_CHANNELS in bot/config.py — no
code changes needed for that.
"""
import asyncio
import logging

from telegram import ChatMember, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, ContextTypes

from bot import config
from bot.translations import t

logger = logging.getLogger(__name__)


def _is_enabled(value) -> bool:
    """Normalizes FORCE_SUBSCRIPTION_ENABLED regardless of whether
    config.py holds a real bool (from the os.getenv(...) == "true"
    pattern) or someone hand-edited it to a plain string like "false".

    This matters because bool("false") is True in Python — a bare
    `if not config.FORCE_SUBSCRIPTION_ENABLED` would silently treat
    FORCE_SUBSCRIPTION_ENABLED = "false" as *enabled*, which is exactly
    the trap here."""
    if isinstance(value, str):
        return value.strip().lower() not in ("false", "0", "no", "off", "")
    return bool(value)


async def _check_single_channel(context: ContextTypes.DEFAULT_TYPE, channel: dict, telegram_id: int) -> bool:
    try:
        member = await context.bot.get_chat_member(chat_id=channel["id"], user_id=telegram_id)
        return member.status not in (ChatMember.LEFT, ChatMember.BANNED)
    except Exception as e:
        # If the bot can't check (not admin in the channel, channel
        # deleted, etc.) fail closed — treat as "not subscribed" rather
        # than silently letting everyone through.
        logger.error("Subscription check failed for channel=%s user=%s: %s", channel.get("id"), telegram_id, e)
        return False


async def check_subscriptions(context: ContextTypes.DEFAULT_TYPE, telegram_id: int) -> list:
    """Returns the subset of REQUIRED_CHANNELS the user is NOT
    subscribed to. Empty list = fully subscribed. Channels are checked
    in parallel so N channels cost roughly one round-trip, not N."""
    if not config.REQUIRED_CHANNELS:
        return []

    results = await asyncio.gather(
        *[_check_single_channel(context, ch, telegram_id) for ch in config.REQUIRED_CHANNELS],
        return_exceptions=True,
    )
    return [
        channel
        for channel, is_subscribed in zip(config.REQUIRED_CHANNELS, results)
        if is_subscribed is not True
    ]


def _subscription_keyboard(lang: str, unsubscribed: list) -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(f"📢 {ch['name']}", url=ch["url"])] for ch in unsubscribed]
    rows.append(
        [InlineKeyboardButton(t("subscription_check_button", lang), callback_data="check_subscription")]
    )
    return InlineKeyboardMarkup(rows)


async def _send_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE, lang: str, unsubscribed: list) -> None:
    text = t("subscription_required", lang)
    keyboard = _subscription_keyboard(lang, unsubscribed)
    telegram_id = update.effective_user.id
    try:
        if update.callback_query:
            # The button that triggered this may belong to a message we
            # can't/shouldn't edit (e.g. mid-conversation) — always send
            # a fresh message so the prompt is never silently dropped.
            await context.bot.send_message(
                chat_id=telegram_id, text=text, reply_markup=keyboard, parse_mode="HTML"
            )
        else:
            await update.message.reply_text(text, reply_markup=keyboard, parse_mode="HTML")
    except Exception:
        logger.exception("Failed to send subscription prompt to %s", telegram_id)


async def ensure_subscribed(update: Update, context: ContextTypes.DEFAULT_TYPE, lang: str) -> bool:
    """Call this at the top of any post-onboarding entry point. Returns
    True if the user may proceed as normal. Returns False if a join
    prompt was just sent instead — the caller should return immediately
    without doing anything else.

    Example:
        if not await ensure_subscribed(update, context, lang):
            return
        # ... normal handler logic ...
    """
    if not _is_enabled(config.FORCE_SUBSCRIPTION_ENABLED) or not config.REQUIRED_CHANNELS:
        return True

    telegram_id = update.effective_user.id
    if telegram_id in config.ADMIN_IDS:
        return True

    unsubscribed = await check_subscriptions(context, telegram_id)
    if not unsubscribed:
        return True

    await _send_prompt(update, context, lang, unsubscribed)
    return False


async def handle_subscription_check(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the '✅ Check Subscription' button."""
    from bot import db

    query = update.callback_query
    telegram_id = update.effective_user.id

    user = await db.get_user_by_telegram_id_async(telegram_id)
    lang = user.get("ui_language", "en") if user else "en"

    await query.answer(t("subscription_checking", lang))

    unsubscribed = await check_subscriptions(context, telegram_id)
    if unsubscribed:
        try:
            await query.edit_message_text(
                t("subscription_still_required", lang),
                reply_markup=_subscription_keyboard(lang, unsubscribed),
                parse_mode="HTML",
            )
        except Exception:
            pass
        return

    try:
        await query.edit_message_text(t("subscription_success", lang), parse_mode="HTML")
    except Exception:
        pass

    if user:
        from bot.handlers.menu import show_main_menu
        await show_main_menu(update, context, lang)


def subscription_handlers() -> list:
    return [CallbackQueryHandler(handle_subscription_check, pattern=r"^check_subscription$")]