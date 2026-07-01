# LangBridge — Anonymous Language Exchange Telegram Bot

MVP implementation. Python · python-telegram-bot v20 · Supabase (PostgreSQL).

---

## Project Structure

```
langbridge/
├── main.py                   ← entrypoint, wires all handlers
├── requirements.txt
├── .env.example              ← copy to .env and fill in
├── sql/
│   └── supabase_schema.sql   ← run once in Supabase SQL editor
└── bot/
    ├── config.py             ← reads .env
    ├── db.py                 ← Supabase data-access layer
    ├── queue_manager.py      ← in-memory matching engine + active chat tracker
    ├── keyboards.py          ← all InlineKeyboardMarkup builders
    ├── translations.py       ← all UI strings in UZ / RU / EN
    └── handlers/
        ├── onboarding.py     ← /start → UI lang → native → learning → level → gender → interests
        ├── menu.py           ← main menu router
        ├── matching.py       ← find partner, cancel search, queue tick job
        ├── chat.py           ← message relay + Next/End/Report buttons
        ├── profile.py        ← show profile + edit profile conversation
        ├── premium.py        ← Telegram Stars + manual card transfer + admin confirm
        ├── settings.py       ← change UI language, delete account
        └── admin.py          ← /admin stats, ban, payments, broadcast
```

---

## Quick Start

### 1. Create the bot
Talk to [@BotFather](https://t.me/BotFather), create a bot, copy the token.

### 2. Set up Supabase
- Create a free project at [supabase.com](https://supabase.com)
- Open **SQL Editor** and run the entire contents of `sql/supabase_schema.sql`
- Go to **Project Settings → API** and copy:
  - Project URL → `SUPABASE_URL`
  - `service_role` key → `SUPABASE_SERVICE_KEY`

### 3. Configure environment
```bash
cp .env.example .env
# Edit .env with your values
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Run
```bash
python main.py
```

---

## Environment Variables

| Variable | Description |
|---|---|
| `BOT_TOKEN` | Telegram bot token from BotFather |
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_SERVICE_KEY` | Supabase service role key (server-side only, never expose) |
| `ADMIN_TELEGRAM_IDS` | Comma-separated Telegram IDs of admins |
| `ADMIN_CARD_NUMBER` | Card number shown to users for manual transfer |
| `ADMIN_CARD_HOLDER` | Card holder name |
| `ADMIN_TRANSFER_NOTE` | Extra note shown with transfer instructions |
| `PREMIUM_PRICE_STARS` | Price in Telegram Stars (integer) |
| `PREMIUM_PRICE_UZS` | Price in UZS for manual transfer (string) |
| `PREMIUM_DURATION_DAYS` | How many days one Premium purchase gives |

---

## Admin Commands

All commands only work for Telegram IDs listed in `ADMIN_TELEGRAM_IDS`.

| Command | Action |
|---|---|
| `/admin` | Stats dashboard (users, chats, queue size, reports) |
| `/admin ban <telegram_id>` | Ban a user |
| `/admin unban <telegram_id>` | Lift a ban |
| `/admin payments` | List pending manual transfer payments |
| `/admin broadcast <message>` | Send a message to all non-banned users |

---

## User Commands

| Command | Action |
|---|---|
| `/start` | Onboarding (or main menu if already registered) |
| `/menu` | Show main menu |
| `/profile` | Show your profile |
| `/premium` | Show Premium purchase options |

---

## Matching Logic

Priority order when searching for a partner:

1. **Native ↔ Learning exact swap** — User A's native is User B's learning and vice versa.
2. **Same learning language** — Both learning the same language (peer learners).
3. **Closest level** among those — Level distance minimized (A1..C2 scale).

Premium users can additionally filter by **gender** and **shared interests**.

---

## Payments

**Telegram Stars** — Handled natively; activation is instant and automatic.

**Manual card transfer** — User sends a screenshot of the bank transfer receipt.
The screenshot is forwarded to all admin Telegram IDs with Confirm / Reject buttons.
Admin taps Confirm → Premium activates for that user immediately.

---

## Deploying to Production

The bot runs fine on any VPS or free-tier service (Railway, Render, Fly.io).

```bash
# Using Railway (example)
railway new
railway add
railway up
```

For webhook mode instead of polling, change `main.py`:
```python
app.run_webhook(
    listen="0.0.0.0",
    port=8443,
    webhook_url="https://yourdomain.com/webhook",
)
```
