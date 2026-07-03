"""
LingoMatch Bot — entrypoint.

Handler priority (python-telegram-bot processes in registration order):
  1. Onboarding ConversationHandler   ← catches /start + onboarding callbacks
  2. Edit-profile ConversationHandler ← catches profile-edit callbacks
  3. Premium handlers                 ← plan selection, card/stars, admin approve/decline,
                                         receipt submission (photo/doc/text while awaiting_receipt)
  4. Main-menu router                 ← menu: callbacks
  5. Matching handlers                ← search:cancel
  6. In-chat controls                 ← chat:end / chat:next / chat:report / report_reason:
  7. Settings handlers                ← settings: / delete: / ui_lang:
  8. Admin commands                   ← /admin
  9. Convenience commands             ← /menu /profile /premium
 10. Message relay                    ← everything else (MessageHandler ALL)
"""
import logging

from telegram.ext import Application, CommandHandler

from bot.config import BOT_TOKEN, WAITING_QUEUE_POLL_SECONDS
from bot.handlers.onboarding import build_onboarding_conversation
from bot.handlers.menu       import menu_handler
from bot.handlers.matching   import matching_handlers, queue_matchmaking_tick
from bot.handlers.chat       import chat_handlers, priority_relay_handler
from bot.handlers.profile    import build_edit_profile_conversation
from bot.handlers.premium    import premium_handlers
from bot.handlers.settings   import settings_handlers
from bot.handlers.admin      import admin_handler
from telegram.ext import CommandHandler 


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()

    # 0. Priority relay guard — must win over any other catch-all
    #    MessageHandler whenever the sender is mid-chat.
    app.add_handler(priority_relay_handler(), group=-1)

    # 1. Onboarding
    app.add_handler(build_onboarding_conversation())

    # 2. Edit profile
    app.add_handler(build_edit_profile_conversation())

    # 3. Premium (includes receipt MessageHandler + admin approve/decline)
    for h in premium_handlers():
        app.add_handler(h)

    # 4. Main menu
    app.add_handler(menu_handler())

    # 5. Matching
    for h in matching_handlers():
        app.add_handler(h)

    # 6. In-chat controls + message relay (relay is last inside this list)
    for h in chat_handlers():
        app.add_handler(h)

    # 7. Settings
    for h in settings_handlers():
        app.add_handler(h)

    # 8. Admin
    app.add_handler(admin_handler())

    # 9. Convenience shortcuts
    app.add_handler(CommandHandler("menu",    _show_menu))
    app.add_handler(CommandHandler("profile", _show_profile))
    app.add_handler(CommandHandler("premium", _show_premium))

    # Background job: retry unmatched queue entries every N seconds
    app.job_queue.run_repeating(
        queue_matchmaking_tick,
        interval=WAITING_QUEUE_POLL_SECONDS,
        first=WAITING_QUEUE_POLL_SECONDS,
    )

    logger.info("LingoMatch bot starting — long polling...")
    app.run_polling(drop_pending_updates=True)


async def _show_menu(update, context):
    from bot import db
    user = db.get_user_by_telegram_id(update.effective_user.id)
    if user:
        from bot.handlers.menu import show_main_menu
        await show_main_menu(update, context, user.get("ui_language", "en"))


async def _show_profile(update, context):
    from bot.handlers.profile import show_profile
    await show_profile(update, context)


async def _show_premium(update, context):
    from bot.handlers.premium import show_premium
    await show_premium(update, context)


if __name__ == "__main__":
    main()
