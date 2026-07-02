import asyncio
import time
from telegram import Bot
from telegram.error import TelegramError
import aiohttp
from dotenv import load_dotenv
import os
import logging
from supabase import create_client, Client

load_dotenv(dotenv_path=".env")
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.ERROR)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get('BOT_TOKEN')

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "999932510"))

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing required environment variables: SUPABASE_URL and SUPABASE_KEY")

if not BOT_TOKEN:
    raise ValueError("Missing required environment variable: BOT_TOKEN")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

MAX_CONCURRENT = 30
BATCH_SIZE = 100
DELAY = 1.0


# ─────────────────────────────────────────────
# DATA FETCHING
# ─────────────────────────────────────────────

def fetch_users():
    """Fetch all non-banned users for broadcast.

    lingo_users has no first_name column, so messages are not
    personalised by name (unlike the presentation bot this was
    ported from). If you want a name, either add a first_name
    column and populate it during onboarding, or fetch it live
    via bot.get_chat(telegram_id) before sending (slower, one
    extra Telegram API call per user).
    """
    try:
        response = (
            supabase.table("lingo_users")
            .select("telegram_id,ui_language,banned")
            .eq("banned", False)
            .execute()
        )
        users = []
        for row in response.data:
            users.append({
                "id": row["telegram_id"],
                "language": row.get("ui_language") or "en"
            })
        return users
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        return []


def fetch_user_by_id(telegram_id: int):
    """Fetch a single user by telegram_id directly from Supabase."""
    try:
        response = (
            supabase.table("lingo_users")
            .select("telegram_id,ui_language")
            .eq("telegram_id", telegram_id)
            .limit(1)
            .execute()
        )
        if response.data:
            row = response.data[0]
            return {
                "id": row["telegram_id"],
                "language": row.get("ui_language") or "en"
            }
        return None
    except Exception as e:
        logger.error(f"Error fetching user {telegram_id}: {e}")
        return None


# ─────────────────────────────────────────────
# MESSAGE GENERATION
# ─────────────────────────────────────────────
# NOTE: placeholder copy — replace with your actual announcement.
# The quiz-service text from the source bot doesn't apply here, so
# this is generic "premium features" promo text for LingoMatch.

def generate_message(language):
    if language == "ru":
        return (
            "🎉 <b>Новости LingoMatch!</b>\n\n"
            "Теперь доступна <b>Premium подписка</b> — быстрее находите партнёров "
            "и настраивайте фильтры поиска по полу и интересам!\n\n"
            "✅ Приоритетный подбор партнёра\n"
            "✅ Фильтры по полу и интересам\n"
            "✅ Больше интересов в профиле\n\n"
            "📩 Подробнее — просто откройте /premium в боте."
        )

    elif language == "uz":
        return (
            "🎉 <b>LingoMatch yangiliklari!</b>\n\n"
            "Endi <b>Premium obuna</b> mavjud — hamkorni tezroq toping va "
            "jins hamda qiziqishlar bo'yicha filtrlardan foydalaning!\n\n"
            "✅ Ustuvor hamkor tanlash\n"
            "✅ Jins va qiziqishlar bo'yicha filtrlar\n"
            "✅ Profilda ko'proq qiziqishlar\n\n"
            "📩 Batafsil — botda /premium buyrug'ini yuboring."
        )

    # default: en
    return (
        "🎉 <b>News from LingoMatch!</b>\n\n"
        "<b>Premium</b> is now available — find partners faster and set "
        "filters by gender and interests!\n\n"
        "✅ Priority matching\n"
        "✅ Gender & interest filters\n"
        "✅ More interests on your profile\n\n"
        "📩 Learn more — just send /premium in the bot."
    )


# ─────────────────────────────────────────────
# SENDING
# ─────────────────────────────────────────────

async def send_message_safe(session, bot_token, chat_id, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML',
        'disable_web_page_preview': True
    }

    try:
        async with session.post(url, json=payload) as response:
            if response.status == 200:
                return {"success": True, "chat_id": chat_id}
            else:
                error_text = await response.text()
                return {"success": False, "chat_id": chat_id, "error": error_text}
    except Exception as e:
        return {"success": False, "chat_id": chat_id, "error": str(e)}


async def send_batch_users(batch: list, bot_token: str) -> list:
    """Send localized messages to a batch of users."""
    connector = aiohttp.TCPConnector(limit=MAX_CONCURRENT)
    timeout = aiohttp.ClientTimeout(total=30)

    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        tasks = [
            send_message_safe(session, bot_token, user["id"], generate_message(user["language"]))
            for user in batch
        ]
        return await asyncio.gather(*tasks, return_exceptions=True)


# ─────────────────────────────────────────────
# BROADCAST RUNNER
# ─────────────────────────────────────────────

def format_duration(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.1f}s"
    minutes = int(seconds // 60)
    secs = seconds % 60
    return f"{minutes}m {secs:.1f}s"


def print_summary(label: str, successful: int, failed: int, elapsed: float):
    total = successful + failed
    rate = (successful / total * 100) if total > 0 else 0.0
    print("\n" + "=" * 50)
    print(f"BROADCAST COMPLETED — {label}")
    print("=" * 50)
    print(f"✅ Successfully sent : {successful}")
    print(f"❌ Failed            : {failed}")
    print(f"📊 Success rate      : {rate:.1f}%")
    print(f"⏱️  Time elapsed      : {format_duration(elapsed)}")
    print("=" * 50)


async def send_to_all_users():
    users = fetch_users()
    if not users:
        print("No users found.")
        return

    print(f"Sending to {len(users)} users...")
    start_time = time.time()
    successful = failed = 0
    total_batches = (len(users) + BATCH_SIZE - 1) // BATCH_SIZE

    for i in range(0, len(users), BATCH_SIZE):
        batch = users[i:i + BATCH_SIZE]
        batch_num = (i // BATCH_SIZE) + 1
        print(f"Batch {batch_num}/{total_batches} ({len(batch)} users)...")

        try:
            results = await send_batch_users(batch, BOT_TOKEN)
            for result in results:
                if isinstance(result, Exception) or not result.get("success"):
                    failed += 1
                else:
                    successful += 1
        except Exception as e:
            logger.error(f"Error in batch {batch_num}: {e}")
            failed += len(batch)

        if i + BATCH_SIZE < len(users):
            await asyncio.sleep(DELAY)

    print_summary("USERS", successful, failed, time.time() - start_time)


# ─────────────────────────────────────────────
# TEST SEND
# ─────────────────────────────────────────────

async def send_test_message(telegram_id: int, language: str = "en"):
    """Send a test message to a single user."""
    user = fetch_user_by_id(telegram_id)
    lang = user["language"] if user else language

    message = generate_message(lang)
    bot = Bot(token=BOT_TOKEN)

    try:
        await bot.send_message(
            chat_id=telegram_id,
            text=message,
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
        print(f"✅ Test message sent to {telegram_id} (lang={lang})")
    except TelegramError as e:
        logger.error(f"Failed to send test message to {telegram_id}: {e}")


# ─────────────────────────────────────────────
# MAIN MENU
# ─────────────────────────────────────────────

async def main():
    users = fetch_users()

    print("=" * 50)
    print("LINGOMATCH BROADCAST")
    print("=" * 50)
    print(f"Total users  : {len(users)}")
    print("\nWhat would you like to do?")
    print("  1. Send messages to all users")
    print("  2. Send test message to a specific user")
    print("  3. Send test message to admin")
    print("  4. Exit")

    choice = input("\nEnter choice (1-4): ").strip()

    if choice == "1":
        confirm = input(f"\nSend to {len(users)} users? (yes/no): ").lower().strip()
        if confirm in ("yes", "y"):
            await send_to_all_users()
        else:
            print("Cancelled.")

    elif choice == "2":
        raw_id = input("Enter telegram_id: ").strip()
        try:
            test_id = int(raw_id)
        except ValueError:
            print("Invalid telegram_id — must be an integer.")
            return
        lang = input("Language (en/ru/uz) [default: en]: ").lower().strip()
        if lang not in ("en", "ru", "uz"):
            lang = "en"
        await send_test_message(test_id, lang)

    elif choice == "3":
        lang = input("Language (en/ru/uz) [default: en]: ").lower().strip()
        if lang not in ("en", "ru", "uz"):
            lang = "en"
        await send_test_message(ADMIN_ID, lang)

    elif choice == "4":
        print("Goodbye.")

    else:
        print("Invalid choice. Please enter 1–4.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
    except Exception as e:
        print(f"Fatal error: {e}")
        logger.error(f"Main error: {e}", exc_info=True)