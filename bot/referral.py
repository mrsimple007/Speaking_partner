"""
Referral program handlers: personal invite links, badge display, the
public /leaderboard, and the success notifications sent to both sides
of a completed referral.

How a "successful" referral gets counted
-----------------------------------------
1. User A opens Invite Friends (menu button) or runs /invite/share and
   gets   https://t.me/<bot_username>?start=ref_<CODE>
2. User B taps the link — Telegram delivers `/start ref_<CODE>` to the
   bot, which is captured and, once B *finishes* onboarding, resolved
   and recorded via db.record_referral_async (see onboarding.py's
   start() and _resolve_referral()).
3. The moment that recording succeeds, onboarding.py calls
   notify_referral_success() below, which pings A ("your friend joined!")
   and B ("welcome, here's your own link") — each with Share + Find
   Partner buttons so the loop keeps going.

Counting only on *completed* onboarding (not the raw /start tap) is
what makes a referral "successful," and record_referral is idempotent
so a retried call can't double-notify.
"""
from urllib.parse import quote

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

from bot import db, keyboards
from bot.translations import t
from bot.referrals import get_badge


def _badge_line(lang: str, count: int) -> str:
    badge = get_badge(count)
    if not badge:
        return t("badge_none", lang)
    emoji, name_key = badge
    return f"{emoji} {t(name_key, lang)}"


def _invite_link(bot_username: str, code: str) -> str:
    return f"https://t.me/{bot_username}?start=ref_{code}"


def _invite_text(lang: str, link: str, count: int) -> str:
    return t("invite_header", lang, link=link, count=count, badge=_badge_line(lang, count))


def _share_url(link: str, text: str) -> str:
    # Opens Telegram's native "forward to a chat" sheet, pre-filled
    # with the given text (which already contains the link).
    return f"https://t.me/share/url?url={quote(link, safe='')}&text={quote(text, safe='')}"


async def show_invite(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    telegram_id = update.effective_user.id
    user = await db.get_user_by_telegram_id_async(telegram_id)
    if not user:
        return
    lang = user.get("ui_language", "en")

    from bot.handlers.subscribe import ensure_subscribed
    if not await ensure_subscribed(update, context, lang):
        return

    code = await db.ensure_referral_code_async(telegram_id)
    me = await context.bot.get_me()
    link = _invite_link(me.username, code)

    count = user.get("referral_count", 0) or 0
    text = _invite_text(lang, link, count)
    keyboard = keyboards.share_referral_keyboard(lang, _share_url(link, text))

    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.message.reply_text(
            text, disable_web_page_preview=True, reply_markup=keyboard
        )
    else:
        await update.message.reply_text(
            text, disable_web_page_preview=True, reply_markup=keyboard
        )


async def notify_referral_success(context: ContextTypes.DEFAULT_TYPE, referrer: dict, new_user: dict) -> None:
    """Called exactly once, right after a referral is newly recorded
    (see onboarding.py's _resolve_referral). Notifies both sides:

      - the referrer, that their friend joined + a fresh share link
        reflecting their bumped-up count
      - the new joiner, welcoming them + handing them their own
        referral link so the chain keeps going

    Both messages get the same Share + Find Partner buttons. Best-effort:
    a failed send here (e.g. the referrer blocked the bot) never bubbles
    up and breaks the new user's onboarding.
    """
    me = await context.bot.get_me()

    # --- tell the referrer ---
    try:
        referrer_lang = referrer.get("ui_language", "en")
        referrer_code = referrer.get("referral_code") or await db.ensure_referral_code_async(
            referrer["telegram_id"]
        )
        referrer_link = _invite_link(me.username, referrer_code)
        # referral_count in `referrer` was fetched before record_referral
        # incremented it — bump locally so the share card is accurate
        # without an extra DB round trip.
        updated_count = (referrer.get("referral_count") or 0) + 1
        friend_name = (
            new_user.get("first_name") or new_user.get("username") or t("referral_someone", referrer_lang)
        )

        referrer_text = t("referral_success_referrer", referrer_lang, name=friend_name)
        referrer_share_text = _invite_text(referrer_lang, referrer_link, updated_count)
        referrer_keyboard = keyboards.referral_success_keyboard(
            referrer_lang, _share_url(referrer_link, referrer_share_text)
        )
        await context.bot.send_message(
            chat_id=referrer["telegram_id"],
            text=referrer_text,
            reply_markup=referrer_keyboard,
        )
    except Exception:
        pass

    # --- welcome the new joiner ---
    try:
        joiner_lang = new_user.get("ui_language", "en")
        joiner_code = await db.ensure_referral_code_async(new_user["telegram_id"])
        joiner_link = _invite_link(me.username, joiner_code)

        joiner_text = t("referral_welcome_joined", joiner_lang, link=joiner_link)
        joiner_share_text = _invite_text(joiner_lang, joiner_link, 0)
        joiner_keyboard = keyboards.referral_success_keyboard(
            joiner_lang, _share_url(joiner_link, joiner_share_text)
        )
        await context.bot.send_message(
            chat_id=new_user["telegram_id"],
            text=joiner_text,
            reply_markup=joiner_keyboard,
        )
    except Exception:
        pass


async def leaderboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    telegram_id = update.effective_user.id
    user = await db.get_user_by_telegram_id_async(telegram_id)
    lang = user.get("ui_language", "en") if user else "en"

    from bot.handlers.subscribe import ensure_subscribed
    if not await ensure_subscribed(update, context, lang):
        return

    # Build the user's own share button up front — shown whether the
    # board is empty or full, since the point of /leaderboard is to
    # nudge them toward climbing it, not just display a scoreboard.
    keyboard = None
    if user:
        me = await context.bot.get_me()
        code = await db.ensure_referral_code_async(telegram_id)
        link = _invite_link(me.username, code)
        share_text = _invite_text(lang, link, user.get("referral_count", 0) or 0)
        keyboard = keyboards.share_referral_keyboard(lang, _share_url(link, share_text))

    top = await db.get_referral_leaderboard_async(limit=10)
    if not top:
        text = t("leaderboard_empty", lang) + "\n\n" + t("leaderboard_cta", lang)
        await update.message.reply_text(text, reply_markup=keyboard)
        return

    medals = ["🥇", "🥈", "🥉"]
    lines = [t("leaderboard_header", lang), ""]
    for i, row in enumerate(top):
        rank = medals[i] if i < len(medals) else f"{i + 1}."
        name = row.get("first_name") or row.get("username") or "—"
        count = row.get("referral_count", 0) or 0
        badge = get_badge(count)
        emoji = badge[0] if badge else ""
        lines.append(f"{rank} {name} — {count} {emoji}")

    # Personal status, so the leaderboard tells the reader where *they*
    # stand, not just who's already winning.
    if user:
        my_count = user.get("referral_count", 0) or 0
        lines.append("")
        lines.append(t("leaderboard_your_stats", lang, count=my_count, badge=_badge_line(lang, my_count)))

    # Explicit call to action — how to get on (or climb) the board.
    lines.append("")
    lines.append(t("leaderboard_cta", lang))

    await update.message.reply_text("\n".join(lines), reply_markup=keyboard)


def referral_handlers() -> list:
    return [
        CommandHandler("invite", show_invite),
        CommandHandler("share", show_invite),  # alias — same link/badge card as /invite
        CommandHandler("leaderboard", leaderboard_command),
    ]