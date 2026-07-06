"""
Referral program handlers: personal invite links, badge display, and
the public /leaderboard.

How a "successful" referral gets counted
-----------------------------------------
1. User A opens Invite Friends (menu button) or runs /invite and gets
       https://t.me/<bot_username>?start=ref_<CODE>
2. User B taps the link — Telegram delivers `/start ref_<CODE>` to the
   bot, which lands in the onboarding ConversationHandler's entry
   point (bot/handlers/onboarding.py).
3. That entry point needs two small additions (not in this file, since
   onboarding.py wasn't part of this changeset — see the two snippets
   below):

   a) On /start, stash the code for later:

        args = context.args
        if args and args[0].startswith("ref_"):
            context.user_data["referral_code"] = args[0][len("ref_"):]

   b) Once B *finishes* onboarding (profile + interests saved, right
      before "interests_saved" is shown), resolve and record it:

        from bot import db
        code = context.user_data.pop("referral_code", None)
        if code:
            referrer = await db.get_user_by_referral_code_async(code)
            if referrer:
                await db.record_referral_async(referrer["id"], new_user["id"])

   Counting only on *completed* onboarding (not on the raw /start tap)
   is what makes a referral "successful" per the announcement, and
   `record_referral` itself is idempotent so retries can't double-count.
"""
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

from bot import db
from bot.translations import t
from bot.referrals import get_badge


def _badge_line(lang: str, count: int) -> str:
    badge = get_badge(count)
    if not badge:
        return t("badge_none", lang)
    emoji, name_key = badge
    return f"{emoji} {t(name_key, lang)}"


async def show_invite(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    telegram_id = update.effective_user.id
    user = await db.get_user_by_telegram_id_async(telegram_id)
    if not user:
        return
    lang = user.get("ui_language", "en")

    code = await db.ensure_referral_code_async(telegram_id)
    me = await context.bot.get_me()
    link = f"https://t.me/{me.username}?start=ref_{code}"

    count = user.get("referral_count", 0) or 0
    text = t(
        "invite_header",
        lang,
        link=link,
        count=count,
        badge=_badge_line(lang, count),
    )

    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.message.reply_text(text, disable_web_page_preview=True)
    else:
        await update.message.reply_text(text, disable_web_page_preview=True)


async def leaderboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    telegram_id = update.effective_user.id
    user = await db.get_user_by_telegram_id_async(telegram_id)
    lang = user.get("ui_language", "en") if user else "en"

    top = await db.get_referral_leaderboard_async(limit=10)
    if not top:
        await update.message.reply_text(t("leaderboard_empty", lang))
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

    await update.message.reply_text("\n".join(lines))


def referral_handlers() -> list:
    return [
        CommandHandler("share", show_invite),
        CommandHandler("leaderboard", leaderboard_command),
    ]