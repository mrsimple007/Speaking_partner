import asyncio
import time
from aiogram import html
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

TOKEN_SimplePPT = os.environ.get('TELEGRAM_BOT_SimplePresentation_maker_bot')
TOKEN_Partner=os.environ.get('BOT_TOKEN')

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "999932510"))

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing required environment variables: SUPABASE_URL and SUPABASE_KEY")

if not TOKEN_SimplePPT:
    raise ValueError("Missing required environment variable: TELEGRAM_BOT_SimplePresentation_maker_bot")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

MAX_CONCURRENT = 30
BATCH_SIZE = 100
DELAY = 1.0


# ─────────────────────────────────────────────
# DATA FETCHING
# ─────────────────────────────────────────────

def fetch_users():
    try:
        response = supabase.table("presentation_users").select("user_id,first_name,language").execute()
        users = []
        for row in response.data:
            users.append({
                "id": row["user_id"],
                "name": row.get("first_name") or "Friend",
                "language": row.get("language") or "en"
            })
        return users
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        return []


def fetch_user_by_id(user_id: int):
    """Fetch a single user by ID directly from Supabase."""
    try:
        response = (
            supabase.table("presentation_users")
            .select("user_id,first_name,language")
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )
        if response.data:
            row = response.data[0]
            return {
                "id": row["user_id"],
                "name": row.get("first_name") or "Friend",
                "language": row.get("language") or "en"
            }
        return None
    except Exception as e:
        logger.error(f"Error fetching user {user_id}: {e}")
        return None


def fetch_groups():
    try:
        response = supabase.table("groups_simpleslides").select("id,title").execute()
        groups = []
        for row in response.data:
            groups.append({
                "id": row["id"],
                "title": row.get("title") or "Group"
            })
        return groups
    except Exception as e:
        logger.error(f"Error fetching groups: {e}")
        return []


# ─────────────────────────────────────────────
# MESSAGE GENERATION
# ─────────────────────────────────────────────

def escape_markdown_v2(text: str) -> str:
    special_chars = r'_*[]()~`>#+-=|{}.!'
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text


def generate_message(name, language):
    if language == "en":
        return (
            "🎉 <b>Good news, {name}!</b>\n\n"
            "We now offer a <b>Quiz Preparation Service</b> — fast, affordable, and high quality!\n\n"
            "✅ Send us your Hemis or final exam tests and we'll convert them into ready-to-use quiz format!\n\n"
            "We split 300–400–500 questions into sections and deliver them as fully prepared quizzes. "
            "Perfect for memorizing and studying for final exams!\n\n"
            "📄 Supports PDF, Word, and TXT files!\n\n"
            "📩 Feel free to reach out:\n"
            "@SimpleLearn_main_admin\n\n"
            "Here you can see examples of completed work:\n"
            "https://t.me/talabaga_tezkor_yordam"
        ).format(name=name)

    elif language == "ru":
        return (
            "🎉 <b>Хорошие новости, {name}!</b>\n\n"
            "Теперь мы предлагаем <b>услугу подготовки квизов</b> — быстро, недорого и качественно!\n\n"
            "✅ Отправьте нам ваши тесты Hemis или итоговые экзамены — мы преобразуем их в готовый формат квиза!\n\n"
            "Разделим 300–400–500 вопросов на блоки и подготовим всё в удобном виде. "
            "Идеально для запоминания и подготовки к итоговым экзаменам!\n\n"
            "📄 Поддерживаются форматы PDF, Word и TXT!\n\n"
            "📩 Обращайтесь без стеснения:\n"
            "@SimpleLearn_main_admin\n\n"
            "Здесь вы можете увидеть примеры выполненных работ:\n"
            "https://t.me/talabaga_tezkor_yordam"
        ).format(name=name)

    elif language == "uz":
        return (
            "🎉 <b>Ajoyib xabar, {name}!</b>\n\n"
            "Endi biz <b>Quiz tayyorlash xizmatini</b> taqdim etamiz — tez, arzon va sifatli!\n\n"
            "✅ Hemis yoki yakuniy imtihon testlaringizni yuboring — biz ularni tayyor quiz holatiga keltirib beramiz!\n\n"
            "100–200–300–400–500 va shu kabi ko'p savolli fayllarni bo'limlarga ajratib, to'liq tayyor quiz ko'rinishida topshiramiz. "
            "Yakuniy testlarni yodlash uchun ideal yechim!\n\n"
            "📄 PDF, Word, TXT, PPT va istalgan boshqa formatlarini qabul qilamiz!\n\n"
            "📩 Bemalol murojaat qilsangiz bo'ladi:\n"
            "@SimpleLearn_main_admin\n\n"
            "Bu yerda esa qilingan ishlardan na'munalarni ko'rishingiz mumkin:\n"
            "https://t.me/talabaga_tezkor_yordam"
        ).format(name=name)

def generate_group_message():
    return (
        "🎁 <b>Earn bonus points by sharing Simple Slides!</b>\n\n"
        "Did you know you can now earn points just by inviting friends?\n\n"
        "• 🔗 Type /share to get your referral link\n"
        "• ⭐ Earn points for every person who joins\n"
        "• 🎯 Use points to unlock more features\n\n"
        "👉 Try it now: @SimplePresentation_maker_bot\n"
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
    """Send personalised messages to a batch of users."""
    connector = aiohttp.TCPConnector(limit=MAX_CONCURRENT)
    timeout = aiohttp.ClientTimeout(total=30)

    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        tasks = [
            send_message_safe(session, bot_token, user["id"], generate_message(user["name"], user["language"]))
            for user in batch
        ]
        return await asyncio.gather(*tasks, return_exceptions=True)


async def send_batch_groups(batch: list, bot_token: str) -> list:
    """Send messages to a batch of groups."""
    connector = aiohttp.TCPConnector(limit=MAX_CONCURRENT)
    timeout = aiohttp.ClientTimeout(total=30)

    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        tasks = [
            send_message_safe(session, bot_token, group["id"], generate_group_message(group["title"]))
            for group in batch
        ]
        return await asyncio.gather(*tasks, return_exceptions=True)


# ─────────────────────────────────────────────
# BROADCAST RUNNERS
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
            results = await send_batch_users(batch, TOKEN_SimplePPT)
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


async def send_to_all_groups():
    groups = fetch_groups()
    if not groups:
        print("No groups found.")
        return

    print(f"Sending to {len(groups)} groups...")
    start_time = time.time()
    successful = failed = 0
    total_batches = (len(groups) + BATCH_SIZE - 1) // BATCH_SIZE

    for i in range(0, len(groups), BATCH_SIZE):
        batch = groups[i:i + BATCH_SIZE]
        batch_num = (i // BATCH_SIZE) + 1
        print(f"Batch {batch_num}/{total_batches} ({len(batch)} groups)...")

        try:
            results = await send_batch_groups(batch, TOKEN_SimplePPT)
            for result in results:
                if isinstance(result, Exception) or not result.get("success"):
                    failed += 1
                else:
                    successful += 1
        except Exception as e:
            logger.error(f"Error in batch {batch_num}: {e}")
            failed += len(batch)

        if i + BATCH_SIZE < len(groups):
            await asyncio.sleep(DELAY)

    print_summary("GROUPS", successful, failed, time.time() - start_time)


# ─────────────────────────────────────────────
# TEST SEND
# ─────────────────────────────────────────────

async def send_test_message(user_id: int, language: str = "en"):
    """Send a test message to a single user."""
    user = fetch_user_by_id(user_id)

    name = user["name"] if user else "Friend"
    lang = user["language"] if user else language

    message = generate_message(name, lang)
    bot = Bot(token=TOKEN_SimplePPT)

    try:
        await bot.send_message(
            chat_id=user_id,
            text=message,
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
        print(f"✅ Test message sent to {user_id} (lang={lang})")
    except TelegramError as e:
        # print(f"❌ Failed to send to {user_id}: {e}")
        logger.error(f"Failed to send test message to {user_id}: {e}")

# ─────────────────────────────────────────────
# MAIN MENU
# ─────────────────────────────────────────────

async def main():
    users = fetch_users()
    groups = fetch_groups()

    print("=" * 50)
    print("SIMPLESLIDES BROADCAST")
    print("=" * 50)
    print(f"Total users  : {len(users)}")
    print(f"Total groups : {len(groups)}")
    print("\nWhat would you like to do?")
    print("  1. Send messages to all users")
    print("  2. Send test message to a specific user")
    print("  3. Send test message to admin")
    print("  4. Send messages to all groups")
    print("  5. Exit")

    choice = input("\nEnter choice (1-5): ").strip()

    if choice == "1":
        confirm = input(f"\nSend to {len(users)} users? (yes/no): ").lower().strip()
        if confirm in ("yes", "y"):
            await send_to_all_users()
        else:
            print("Cancelled.")

    elif choice == "2":
        raw_id = input("Enter user ID: ").strip()
        try:
            test_user_id = int(raw_id)
        except ValueError:
            print("Invalid user ID — must be an integer.")
            return
        lang = input("Language (en/ru/uz) [default: en]: ").lower().strip()
        if lang not in ("en", "ru", "uz"):
            lang = "en"
        await send_test_message(test_user_id, lang)

    elif choice == "3":
        lang = input("Language (en/ru/uz) [default: en]: ").lower().strip()
        if lang not in ("en", "ru", "uz"):
            lang = "en"
        await send_test_message(ADMIN_ID, lang)

    elif choice == "4":
        confirm = input(f"\nSend to {len(groups)} groups? (yes/no): ").lower().strip()
        if confirm in ("yes", "y"):
            await send_to_all_groups()
        else:
            print("Cancelled.")

    elif choice == "5":
        print("Goodbye.")

    else:
        print("Invalid choice. Please enter 1–5.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
    except Exception as e:
        print(f"Fatal error: {e}")
        logger.error(f"Main error: {e}", exc_info=True)