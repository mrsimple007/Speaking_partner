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

# Flip to True to attach the banner image; put the file next to this
# script as referral_banner.jpg (or point REFERRAL_IMAGE_PATH at it).
WITH_IMAGE = True
REFERRAL_IMAGE_PATH = "ChatGPT Image 6 июл. 2026 г., 12_20_02.png"

# ─────────────────────────────────────────────
# DATA FETCHING
# ─────────────────────────────────────────────

def fetch_users():
    try:
        response = (
            supabase.table("lingo_users")
            .select("telegram_id,ui_language,banned")
            .eq("banned", False)
            .execute()
        )
        return [
            {"id": row["telegram_id"], "language": row.get("ui_language") or "en"}
            for row in response.data
        ]
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        return []


def fetch_user_by_id(telegram_id: int):
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
            return {"id": row["telegram_id"], "language": row.get("ui_language") or "en"}
        return None
    except Exception as e:
        logger.error(f"Error fetching user {telegram_id}: {e}")
        return None


# ─────────────────────────────────────────────
# MESSAGE — referral feature announcement
# ─────────────────────────────────────────────

def generate_message(language):
    if language == "ru":
        return (
            "🎉 <b>Новая функция — приглашай друзей!</b>\n\n"
            "📤 /share — получить свою ссылку\n"
            "🏆 /leaderboard — топ пригласивших\n\n"
            "Приглашай больше — получай значки 🏅\n"
            "3 друга → 📣 Амбассадор, 10 → 🚀 Строитель сообщества, "
            "50 → 🌍 Глобальный коннектор, 100 → 👑 Легенда.\n\n"
            "А топ приглашающих получает бонус — быстрее находит партнёров ⚡\n\n"
            "Просто и легко — начни прямо сейчас!"
        )
    elif language == "uz":
        return (
            "🎉 <b>Botimizda Yangi funksiya — do'stlaringizni taklif qiling!</b>\n\n"
            "📤 /share orqali havolangizni oling\n"
            "🏆 /leaderboard — eng ko'p do'st taklif qilganlar ro'yxati\n\n"
            "Ko'proq taklif qiling va medallar oling 🏅\n"
            "3 ta do'st → 📣 Ambassador, 10 ta → 🚀 Community Builder, "
            "50 ta → 🌍 Global Connector, 100 ta → 👑 Legend.\n\n"
            "Eng faol taklif qiluvchilar juda ko'plab imkoniyatga ega bo'lishadi! ⚡\n\n"
            "/share qilib hoziroq boshlang!"
        )
    return (
        "🎉 <b>New feature — invite friends!</b>\n\n"
        "📤 /share — get your invite link\n"
        "🏆 /leaderboard — see the top referrers\n\n"
        "Invite more, earn badges 🏅\n"
        "3 friends → 📣 Ambassador, 10 → 🚀 Community Builder, "
        "50 → 🌍 Global Connector, 100 → 👑 Legend.\n\n"
        "Top referrers also get matched with partners faster ⚡\n\n"
        "Easy and simple — start now!"
    )

# ─────────────────────────────────────────────
# IMAGE LOADING
# ─────────────────────────────────────────────

def load_image_bytes(path: str = REFERRAL_IMAGE_PATH):
    if not path or not os.path.isfile(path):
        logger.error(f"Image file not found: {path}")
        return None
    with open(path, "rb") as f:
        return f.read()


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
            error_text = await response.text()
            return {"success": False, "chat_id": chat_id, "error": error_text}
    except Exception as e:
        return {"success": False, "chat_id": chat_id, "error": str(e)}


async def send_photo_safe(session, bot_token, chat_id, photo_bytes, caption=None):
    url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
    form = aiohttp.FormData()
    form.add_field("chat_id", str(chat_id))
    form.add_field("photo", photo_bytes, filename="announcement.jpg", content_type="image/jpeg")
    if caption:
        form.add_field("caption", caption)
        form.add_field("parse_mode", "HTML")
    try:
        async with session.post(url, data=form) as response:
            if response.status == 200:
                return {"success": True, "chat_id": chat_id}
            error_text = await response.text()
            return {"success": False, "chat_id": chat_id, "error": error_text}
    except Exception as e:
        return {"success": False, "chat_id": chat_id, "error": str(e)}


async def send_to_user(session, bot_token, user, photo_bytes):
    """Sends the announcement to one user — as a photo+caption if we
    have image bytes (the message is short enough to fit Telegram's
    1024-char caption limit), otherwise as plain text."""
    message = generate_message(user["language"])
    if photo_bytes:
        return await send_photo_safe(session, bot_token, user["id"], photo_bytes, caption=message)
    return await send_message_safe(session, bot_token, user["id"], message)


async def send_batch_users(batch: list, bot_token: str, photo_bytes) -> list:
    connector = aiohttp.TCPConnector(limit=MAX_CONCURRENT)
    timeout = aiohttp.ClientTimeout(total=30)
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        tasks = [send_to_user(session, bot_token, user, photo_bytes) for user in batch]
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


def print_summary(successful: int, failed: int, elapsed: float):
    total = successful + failed
    rate = (successful / total * 100) if total > 0 else 0.0
    print("\n" + "=" * 50)
    print("BROADCAST COMPLETED")
    print("=" * 50)
    print(f"✅ Successfully sent : {successful}")
    print(f"❌ Failed            : {failed}")
    print(f"📊 Success rate      : {rate:.1f}%")
    print(f"⏱️  Time elapsed      : {format_duration(elapsed)}")
    print("=" * 50)


async def send_to_all_users():
    photo_bytes = load_image_bytes() if WITH_IMAGE else None
    if WITH_IMAGE and photo_bytes is None:
        print(f"⚠️  Couldn't load image at '{REFERRAL_IMAGE_PATH}' — sending text only.")

    users = fetch_users()
    if not users:
        print("No users found.")
        return

    print(f"Sending to {len(users)} users{' (with image)' if photo_bytes else ''}...")
    start_time = time.time()
    successful = failed = 0
    total_batches = (len(users) + BATCH_SIZE - 1) // BATCH_SIZE

    for i in range(0, len(users), BATCH_SIZE):
        batch = users[i:i + BATCH_SIZE]
        batch_num = (i // BATCH_SIZE) + 1
        print(f"Batch {batch_num}/{total_batches} ({len(batch)} users)...")
        try:
            results = await send_batch_users(batch, BOT_TOKEN, photo_bytes)
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

    print_summary(successful, failed, time.time() - start_time)


# ─────────────────────────────────────────────
# TEST SEND
# ─────────────────────────────────────────────

async def send_test_message(telegram_id: int, language: str = "en"):
    user = fetch_user_by_id(telegram_id)
    lang = user["language"] if user else language
    message = generate_message(lang)
    bot = Bot(token=BOT_TOKEN)

    try:
        if WITH_IMAGE:
            photo_bytes = load_image_bytes()
            if photo_bytes:
                await bot.send_photo(chat_id=telegram_id, photo=photo_bytes, caption=message, parse_mode="HTML")
                print(f"✅ Test message sent to {telegram_id} (lang={lang}, with image)")
                return
            print(f"⚠️  Couldn't load image at '{REFERRAL_IMAGE_PATH}' — sending text only.")

        await bot.send_message(chat_id=telegram_id, text=message, parse_mode="HTML", disable_web_page_preview=True)
        print(f"✅ Test message sent to {telegram_id} (lang={lang})")
    except TelegramError as e:
        logger.error(f"Failed to send test message to {telegram_id}: {e}")


# ─────────────────────────────────────────────
# MAIN MENU
# ─────────────────────────────────────────────

async def main():
    users = fetch_users()

    print("=" * 50)
    print("LINGOMATCH BROADCAST — Referral Feature Announcement")
    print(f"WITH_IMAGE = {WITH_IMAGE}")
    print("=" * 50)
    print(f"Total users  : {len(users)}")
    print("\nWhat would you like to do?")
    print("  1. Send to all users")
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