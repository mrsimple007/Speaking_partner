import logging
from telegram.constants import ChatAction

logger = logging.getLogger(__name__)


async def typing(context, chat_id: int) -> None:
    """Show a 'typing...' indicator before the bot replies. Never raises."""
    try:
        await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    except Exception:
        logger.debug("Failed to send typing action to %s", chat_id, exc_info=True)