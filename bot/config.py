import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")


# Only this admin can press Approve / Decline
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID", "")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "@admin")

# Two card numbers for manual transfers
CARD_NUMBER   = os.getenv("CARD_NUMBER",   "0000 0000 0000 0001")
CARD_NUMBER_2 = os.getenv("CARD_NUMBER_2", "0000 0000 0000 0002")

# Telegram Stars price per plan
PREMIUM_STARS = {
    "1_month":   int(os.getenv("PREMIUM_STARS_1_MONTH",  "150")),
    "3_months":  int(os.getenv("PREMIUM_STARS_3_MONTHS", "400")),
    "6_months":  int(os.getenv("PREMIUM_STARS_6_MONTHS", "700")),
    "1_year":    int(os.getenv("PREMIUM_STARS_1_YEAR",  "1100")),
}

MAX_INTERESTS = 20
WAITING_QUEUE_POLL_SECONDS = 2


ADMIN_IDS = [
    "8437026582",  # Main admin - always gets notifications
    # "8126290272",  # MR_2
    # "999932510",   # MrSimple07
]