"""
Admin commands — only work for telegram IDs listed in ADMIN_TELEGRAM_IDS.
/admin                 — show stats dashboard
/admin ban <id>        — ban a user by their Telegram ID
/admin unban <id>      — lift a ban
/admin payments        — list pending manual payments
"""
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from bot import db, config
from bot.queue_manager import engine


def _require_admin(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id not in config.ADMIN_TELEGRAM_IDS:
            return
        await func(update, context)
    return wrapper


@_require_admin
async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    args = context.args or []
    if not args:
        # Show stats
        stats = db.get_admin_stats()
        lines = [
            "📊 *LangBridge Admin Stats*",
            f"Total users: {stats.get('total_users', 0)}",
            f"Active (24h): {stats.get('active_users_24h', 0)}",
            f"Premium users: {stats.get('premium_users', 0)}",
            f"Matches today: {stats.get('matches_today', 0)}",
            f"Avg chat duration: {int(stats.get('avg_chat_duration_seconds') or 0)}s",
            f"Reports today: {stats.get('reports_today', 0)}",
            f"Queue size now: {len(engine._queue)}",
            f"Active chats now: {len(engine._active_chats) // 2}",
        ]
        await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
        return

    subcmd = args[0].lower()

    if subcmd == "ban" and len(args) >= 2:
        target_id = int(args[1])
        db.update_user(target_id, {"banned": True, "status": "banned"})
        await engine.remove_from_queue(target_id)
        await update.message.reply_text(f"✅ User {target_id} banned.")

    elif subcmd == "unban" and len(args) >= 2:
        target_id = int(args[1])
        db.update_user(target_id, {"banned": False, "status": "idle"})
        await update.message.reply_text(f"✅ User {target_id} unbanned.")

    elif subcmd == "payments":
        # List last 10 pending manual payments
        rows = (
            db.supabase.table("lingo_payments")
            .select("id, user_id, amount, currency, created_at, lingo_users(telegram_id)")
            .eq("status", "pending")
            .eq("method", "manual_transfer")
            .order("created_at", desc=True)
            .limit(10)
            .execute()
            .data
        )
        if not rows:
            await update.message.reply_text("No pending manual payments.")
            return
        lines = ["💳 *Pending manual payments*"]
        for r in rows:
            tg_id = r.get("lingo_users", {}).get("telegram_id", "?")
            lines.append(
                f"ID {r['id']} | User {tg_id} | {r['amount']} {r['currency']} | {r['created_at'][:10]}"
            )
        await update.message.reply_text("\n".join(lines), parse_mode="Markdown")

    elif subcmd == "broadcast" and len(args) >= 2:
        # /admin broadcast Your message here
        msg = " ".join(args[1:])
        users = (
            db.supabase.table("lingo_users")
            .select("telegram_id")
            .neq("banned", True)
            .execute()
            .data
        )
        sent = 0
        for u in users:
            try:
                await context.bot.send_message(chat_id=u["telegram_id"], text=msg)
                sent += 1
            except Exception:
                pass
        await update.message.reply_text(f"✅ Broadcast sent to {sent} users.")

    else:
        await update.message.reply_text(
            "Usage:\n/admin\n/admin ban <id>\n/admin unban <id>\n/admin payments\n/admin broadcast <msg>"
        )


def admin_handler() -> CommandHandler:
    return CommandHandler("admin", admin_command)