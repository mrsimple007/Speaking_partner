"""
Premium subscription flow for LangBridge.

Plans  : 1 month / 3 months / 6 months / 1 year
Payment: Telegram Stars (instant) or manual card transfer (admin confirm).

Admin flow for manual payments
──────────────────────────────
1. User picks a plan → picks "Card" → sees card numbers + instructions.
2. Bot sends a notification to ALL NOTIFICATION_ADMIN_IDS with
   [✅ Approve] [❌ Decline] buttons.
3. Only the ADMIN_CHAT_ID account can actually press those buttons.
4. On Approve  → premium activated, user notified, all admin messages updated.
5. On Decline  → user notified with reason, all admin messages updated.

Receipt submission
──────────────────
User can also send a photo / document / text directly to the bot after
paying and it is forwarded to all admins (without approve/decline buttons —
that notification already carries the buttons).
"""
import logging
from datetime import datetime, timedelta, timezone

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    LabeledPrice,
    Update,
)
from telegram.constants import ParseMode
from telegram.ext import (
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    PreCheckoutQueryHandler,
    filters,
)

from bot import config, db, keyboards
from bot.translations import t

logger = logging.getLogger(__name__)

# ───────────────────────────────────────────────────────────────
# PLAN DEFINITIONS
# ───────────────────────────────────────────────────────────────
SUBSCRIPTION_PLANS = {
    "1_month": {
        "price_uzs":    30_000,
        "duration_days": 30,
    },
    "3_months": {
        "price_uzs":    50_000,
        "duration_days": 90,
        "discount":    "44% OFF",
    },
    "6_months": {
        "price_uzs":    90_000,
        "duration_days": 180,
        "discount":    "50% OFF",
    },
    "1_year": {
        "price_uzs":   150_000,
        "duration_days": 365,
        "discount":    "58% OFF",
    },
}


def _plan_name(plan_key: str, lang: str) -> str:
    names = {
        "uz": {"1_month": "1 oylik",   "3_months": "3 oylik",    "6_months": "6 oylik",    "1_year": "1 yillik"},
        "ru": {"1_month": "1 месяц",   "3_months": "3 месяца",   "6_months": "6 месяцев",  "1_year": "1 год"},
        "en": {"1_month": "1 month",   "3_months": "3 months",   "6_months": "6 months",   "1_year": "1 year"},
    }
    return names.get(lang, names["en"]).get(plan_key, plan_key)


def _plan_buttons(lang: str) -> list:
    labels = {
        "uz": {
            "1_month":  "📅 1 oy — 30,000 so'm",
            "3_months": "🔥 3 oy — 50,000 so'm (44% OFF)",
            "6_months": "💎 6 oy — 90,000 so'm (50% OFF)",
            "1_year":   "⭐ 1 yil — 150,000 so'm (58% OFF)",
        },
        "ru": {
            "1_month":  "📅 1 месяц — 30,000 сум",
            "3_months": "🔥 3 месяца — 50,000 сум (44% OFF)",
            "6_months": "💎 6 месяцев — 90,000 сум (50% OFF)",
            "1_year":   "⭐ 1 год — 150,000 сум (58% OFF)",
        },
        "en": {
            "1_month":  "📅 1 month — 30,000 UZS",
            "3_months": "🔥 3 months — 50,000 UZS (44% OFF)",
            "6_months": "💎 6 months — 90,000 UZS (50% OFF)",
            "1_year":   "⭐ 1 year — 150,000 UZS (58% OFF)",
        },
    }
    row_labels = labels.get(lang, labels["en"])
    return [
        [InlineKeyboardButton(row_labels["1_month"],  callback_data="subplan:1_month")],
        [InlineKeyboardButton(row_labels["3_months"], callback_data="subplan:3_months")],
        [InlineKeyboardButton(row_labels["6_months"], callback_data="subplan:6_months")],
        [InlineKeyboardButton(row_labels["1_year"],   callback_data="subplan:1_year")],
    ]


# ───────────────────────────────────────────────────────────────
# PREMIUM PAGE  (show_premium)
# ───────────────────────────────────────────────────────────────
async def show_premium(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    telegram_id = update.effective_user.id
    user = db.get_user_by_telegram_id(telegram_id)
    lang = user.get("ui_language", "en") if user else "en"

    features = {
        "uz": (
            "✨ <b>Premium imkoniyatlari:</b>\n"
            "• Cheksiz hamkorlar\n"
            "• Jins bo'yicha filtr\n"
            "• Qiziqishlar bo'yicha filtr\n"
            "• Navbatda ustuvorlik"
        ),
        "ru": (
            "✨ <b>Возможности Premium:</b>\n"
            "• Неограниченные совпадения\n"
            "• Фильтр по полу\n"
            "• Фильтр по интересам\n"
            "• Приоритет в очереди"
        ),
        "en": (
            "✨ <b>Premium Features:</b>\n"
            "• Unlimited matches\n"
            "• Gender filter\n"
            "• Interest filter\n"
            "• Priority queue"
        ),
    }
    plans_header = {"uz": "💰 <b>Obuna rejalari:</b>", "ru": "💰 <b>Планы подписки:</b>", "en": "💰 <b>Subscription Plans:</b>"}
    choose     = {"uz": "\n👇 Rejani tanlang:", "ru": "\n👇 Выберите план:", "en": "\n👇 Choose your plan:"}

    text = (
        t("premium_header", lang) + "\n\n"
        + features.get(lang, features["en"]) + "\n\n"
        + plans_header.get(lang, plans_header["en"]) + "\n"
        "📅 <b>1 oy/мес/month</b>  —  <code>30,000</code> UZS\n"
        "📅 <b>3 oy/мес/months</b> —  <s>90,000</s> <code>50,000</code> UZS  <b>(44% OFF)</b>\n"
        "📅 <b>6 oy/мес/months</b> —  <s>180,000</s> <code>90,000</code> UZS  <b>(50% OFF)</b>\n"
        "📅 <b>1 yil/год/year</b>  —  <s>360,000</s> <code>150,000</code> UZS  <b>(58% OFF)</b>"
        + choose.get(lang, choose["en"])
    )

    kb = InlineKeyboardMarkup(_plan_buttons(lang))

    if update.callback_query:
        try:
            await update.callback_query.edit_message_text(text, parse_mode=ParseMode.HTML, reply_markup=kb)
        except Exception:
            await update.callback_query.message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=kb)
    else:
        await update.message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=kb)


# ───────────────────────────────────────────────────────────────
# STEP 1 — User selects a plan
# ───────────────────────────────────────────────────────────────
async def handle_plan_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    plan_key = query.data.split(":")[1]
    if plan_key not in SUBSCRIPTION_PLANS:
        return

    telegram_id = update.effective_user.id
    user = db.get_user_by_telegram_id(telegram_id)
    lang = user.get("ui_language", "en") if user else "en"

    plan = SUBSCRIPTION_PLANS[plan_key]
    plan_name = _plan_name(plan_key, lang)
    context.user_data["selected_plan"] = plan_key

    method_title = {
        "uz": f"💳 <b>To'lov usulini tanlang</b>\n\n📦 Obuna: <b>{plan_name}</b>\n💰 Narx: <b>{plan['price_uzs']:,} so'm</b>",
        "ru": f"💳 <b>Выберите способ оплаты</b>\n\n📦 Подписка: <b>{plan_name}</b>\n💰 Цена: <b>{plan['price_uzs']:,} сум</b>",
        "en": f"💳 <b>Choose payment method</b>\n\n📦 Plan: <b>{plan_name}</b>\n💰 Price: <b>{plan['price_uzs']:,} UZS</b>",
    }
    btn_card  = {"uz": "💳 Karta orqali",        "ru": "💳 Картой",        "en": "💳 Card Payment"}
    btn_stars = {"uz": "⭐ Telegram Stars",       "ru": "⭐ Telegram Stars", "en": "⭐ Telegram Stars"}
    btn_back  = {"uz": "« Orqaga",               "ru": "« Назад",          "en": "« Back"}

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(btn_card.get(lang, btn_card["en"]),   callback_data=f"subpay:card:{plan_key}")],
        [InlineKeyboardButton(btn_stars.get(lang, btn_stars["en"]), callback_data=f"subpay:stars:{plan_key}")],
        [InlineKeyboardButton(btn_back.get(lang, btn_back["en"]),   callback_data="menu:premium")],
    ])

    await query.edit_message_text(method_title.get(lang, method_title["en"]), parse_mode=ParseMode.HTML, reply_markup=kb)


# ───────────────────────────────────────────────────────────────
# STEP 2a — Card payment: show instructions + notify admins
# ───────────────────────────────────────────────────────────────
CARD_INSTRUCTIONS = {
    "uz": """💳 <b>Obuna sotib olish</b>

📦 Obuna: <b>{plan_name}</b>
💰 Narx: <b>{price:,} so'm</b>

📋 <b>To'lov tartibi:</b>
1️⃣ 30 daqiqa ichida quyidagi kartalardan biriga {price:,} so'm o'tkazing:
   <code>{card1}</code>
   yoki
   <code>{card2}</code>

2️⃣ To'lov chekini (screenshot) shu botga yuboring

3️⃣ Admin tasdiqlagach obuna faollashtiriladi

⚠️ <b>Muhim:</b> Chekni botga yuboring — adminlar ko'radi!""",

    "ru": """💳 <b>Купить подписку</b>

📦 Подписка: <b>{plan_name}</b>
💰 Цена: <b>{price:,} сум</b>

📋 <b>Порядок оплаты:</b>
1️⃣ Переведите {price:,} сум на одну из карт в течение 30 минут:
   <code>{card1}</code>
   или
   <code>{card2}</code>

2️⃣ Отправьте чек оплаты (скриншот) в этот бот

3️⃣ Подписка активируется после подтверждения админа

⚠️ <b>Важно:</b> Отправьте чек боту — его увидят админы!""",

    "en": """💳 <b>Buy Subscription</b>

📦 Plan: <b>{plan_name}</b>
💰 Price: <b>{price:,} UZS</b>

📋 <b>Payment steps:</b>
1️⃣ Transfer {price:,} UZS to one of the cards within 30 minutes:
   <code>{card1}</code>
   or
   <code>{card2}</code>

2️⃣ Send your payment receipt (screenshot) to this bot

3️⃣ Subscription activates after admin confirmation

⚠️ <b>Important:</b> Send the receipt here — admins will see it!""",
}


async def handle_card_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    parts = query.data.split(":")          # subpay:card:1_month
    plan_key = parts[2]
    if plan_key not in SUBSCRIPTION_PLANS:
        return

    telegram_id = update.effective_user.id
    user = db.get_user_by_telegram_id(telegram_id)
    lang = user.get("ui_language", "en") if user else "en"
    plan = SUBSCRIPTION_PLANS[plan_key]
    plan_name = _plan_name(plan_key, lang)

    # Save pending payment to DB
    payment_row = db.create_payment(
        user_id=user["id"],
        method="manual_transfer",
        amount=plan["price_uzs"],
        currency="UZS",
    )

    # Store in bot_data so approve/decline handlers can find it
    payment_key = f"payment_{telegram_id}_{plan['price_uzs']}"
    context.bot_data[payment_key] = {
        "messages": {},                # admin_id → message_id
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "is_subscription": True,
        "subscription_plan": plan_key,
        "payment_id": payment_row["id"],
    }
    # Also flag bot to receive receipt
    context.user_data["awaiting_receipt"] = True
    context.user_data["receipt_plan_key"] = plan_key
    context.user_data["receipt_payment_key"] = payment_key

    text = CARD_INSTRUCTIONS.get(lang, CARD_INSTRUCTIONS["en"]).format(
        plan_name=plan_name,
        price=plan["price_uzs"],
        card1=config.CARD_NUMBER,
        card2=config.CARD_NUMBER_2,
    )

    btn_back = {"uz": "« Orqaga", "ru": "« Назад", "en": "« Back"}
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(btn_back.get(lang, btn_back["en"]), callback_data="menu:premium")]
    ])

    await query.edit_message_text(text, parse_mode=ParseMode.HTML, reply_markup=kb)

    # Notify all admins
    await _send_payment_request_to_admins(
        context=context,
        telegram_id=telegram_id,
        user_name=update.effective_user.full_name,
        username=update.effective_user.username,
        plan_key=plan_key,
        plan_name=plan_name,
        amount_uzs=plan["price_uzs"],
        payment_key=payment_key,
    )


async def _send_payment_request_to_admins(
    context, telegram_id, user_name, username,
    plan_key, plan_name, amount_uzs, payment_key
):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user_info = f"👤 User ID: <code>{telegram_id}</code>\n👤 Name: {user_name}\n"
    if username:
        user_info += f"👤 Username: @{username}\n"

    text = (
        f"💳 <b>New Subscription Payment Request</b>\n"
        f"📅 Time: {timestamp}\n"
        f"{user_info}"
        f"📦 Plan: <b>{plan_name}</b>\n"
        f"💰 Amount: <b>{amount_uzs:,} UZS</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━"
    )
    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Approve", callback_data=f"admpay:approve:{telegram_id}:{amount_uzs}:{plan_key}"),
        InlineKeyboardButton("❌ Decline", callback_data=f"admpay:decline:{telegram_id}:{amount_uzs}:{plan_key}"),
    ]])

    for admin_id in config.NOTIFICATION_ADMIN_IDS:
        try:
            sent = await context.bot.send_message(
                chat_id=admin_id, text=text, parse_mode=ParseMode.HTML, reply_markup=kb
            )
            context.bot_data[payment_key]["messages"][admin_id] = sent.message_id
        except Exception as e:
            logger.error(f"Failed to notify admin {admin_id}: {e}")


# ───────────────────────────────────────────────────────────────
# RECEIPT SUBMISSION (user sends photo/doc/text after paying)
# ───────────────────────────────────────────────────────────────
async def handle_receipt_submission(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.user_data.get("awaiting_receipt"):
        return

    msg = update.message
    is_photo    = bool(msg.photo)
    is_document = bool(msg.document)
    is_text     = bool(msg.text and not msg.text.startswith("/"))
    if not (is_photo or is_document or is_text):
        return

    telegram_id = update.effective_user.id
    user = db.get_user_by_telegram_id(telegram_id)
    lang = user.get("ui_language", "en") if user else "en"
    user_name = update.effective_user.full_name
    username  = update.effective_user.username

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user_line = f"👤 User ID: <code>{telegram_id}</code>\n👤 Name: {user_name}\n"
    if username:
        user_line += f"👤 Username: @{username}\n"

    admin_text = (
        f"📸 <b>Payment Receipt Received</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📅 Time: {timestamp}\n"
        f"{user_line}"
        f"━━━━━━━━━━━━━━━━━━━━━━"
    )

    contact_kb = None
    if username:
        contact_kb = InlineKeyboardMarkup([[
            InlineKeyboardButton("💬 Contact User", url=f"https://t.me/{username}")
        ]])

    # Attach proof to DB payment if we have the payment_id
    payment_key = context.user_data.get("receipt_payment_key")
    payment_info = context.bot_data.get(payment_key, {})
    payment_id = payment_info.get("payment_id")

    for admin_id in config.NOTIFICATION_ADMIN_IDS:
        try:
            if is_photo:
                file_id = msg.photo[-1].file_id
                cap = admin_text + (f"\n\n📝 {msg.caption}" if msg.caption else "")
                await context.bot.send_photo(chat_id=admin_id, photo=file_id, caption=cap,
                                             parse_mode=ParseMode.HTML, reply_markup=contact_kb)
                if payment_id:
                    db.attach_payment_proof(payment_id, file_id)
            elif is_document:
                file_id = msg.document.file_id
                cap = admin_text + (f"\n\n📝 {msg.caption}" if msg.caption else "")
                await context.bot.send_document(chat_id=admin_id, document=file_id, caption=cap,
                                                parse_mode=ParseMode.HTML, reply_markup=contact_kb)
                if payment_id:
                    db.attach_payment_proof(payment_id, file_id)
            else:
                full = admin_text + f"\n\n💬 <b>Message:</b>\n{msg.text}"
                await context.bot.send_message(chat_id=admin_id, text=full,
                                               parse_mode=ParseMode.HTML, reply_markup=contact_kb)
        except Exception as e:
            logger.error(f"Failed to forward receipt to admin {admin_id}: {e}")

    context.user_data["awaiting_receipt"] = False

    confirm = {
        "uz": "✅ Chek muvaffaqiyatli yuborildi!\n\nAdmin tez orada ko'rib chiqadi va obunani faollashtiradi.",
        "ru": "✅ Чек успешно отправлен!\n\nАдмин скоро проверит и активирует подписку.",
        "en": "✅ Receipt sent successfully!\n\nAdmin will review it shortly and activate your subscription.",
    }
    await msg.reply_text(confirm.get(lang, confirm["en"]))


# ───────────────────────────────────────────────────────────────
# ADMIN: APPROVE
# ───────────────────────────────────────────────────────────────
async def admin_approve(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if str(query.from_user.id) != str(config.ADMIN_CHAT_ID):
        await query.answer("⛔ Admin only.", show_alert=True)
        return

    try:
        # callback: admpay:approve:<telegram_id>:<amount>:<plan_key>
        _, _, raw_id, raw_amount, plan_key = query.data.split(":", 4)
        telegram_id = int(raw_id)
        amount_uzs  = int(raw_amount)

        payment_key  = f"payment_{telegram_id}_{amount_uzs}"
        payment_info = context.bot_data.get(payment_key, {})
        payment_id   = payment_info.get("payment_id")

        # Activate premium in DB
        plan = SUBSCRIPTION_PLANS.get(plan_key, {})
        days = plan.get("duration_days", 30)
        db.activate_premium(telegram_id, days)
        if payment_id:
            db.confirm_payment(payment_id, admin_note=f"approved by {query.from_user.id}")

        # Fetch user info for admin message
        try:
            tg_user  = await context.bot.get_chat(telegram_id)
            uname    = tg_user.first_name or f"User_{telegram_id}"
            username = tg_user.username
        except Exception:
            uname, username = f"User_{telegram_id}", None

        user   = db.get_user_by_telegram_id(telegram_id)
        lang   = user.get("ui_language", "en") if user else "en"
        pname  = _plan_name(plan_key, lang)

        # Work out expiry date
        until = datetime.now(timezone.utc) + timedelta(days=days)
        end_str = until.strftime("%d.%m.%Y")

        approved_by = query.from_user.username or query.from_user.first_name
        orig_time   = payment_info.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        done_time   = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        admin_update = (
            f"✅ <b>APPROVED</b> by @{approved_by}\n"
            f"🌟 <b>Subscription Payment</b>\n"
            f"📅 Request: {orig_time}\n"
            f"👤 User ID: <code>{telegram_id}</code>\n"
            f"👤 Name: {uname}\n"
        )
        if username:
            admin_update += f"👤 @{username}\n"
        admin_update += (
            f"📦 Plan: <b>{pname}</b>\n"
            f"💰 Amount: <b>{amount_uzs:,} UZS</b>\n"
            f"⏰ Valid until: <b>{end_str}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"⏰ Approved: {done_time}"
        )

        # Update message for the admin who pressed Approve
        await query.edit_message_text(admin_update, parse_mode=ParseMode.HTML)

        # Update all other admins' copies
        for aid, mid in payment_info.get("messages", {}).items():
            if str(aid) != str(query.from_user.id):
                try:
                    await context.bot.edit_message_text(
                        chat_id=aid, message_id=mid,
                        text=admin_update, parse_mode=ParseMode.HTML
                    )
                except Exception as e:
                    logger.error(f"Could not update admin {aid} message: {e}")

        context.bot_data.pop(payment_key, None)

        # Notify user
        activate_msg = {
            "uz": f"🎉 <b>Obuna faollashtirildi!</b>\n\n📦 Reja: <b>{pname}</b>\n⏰ Amal qilish muddati: <b>{end_str}</b>\n\nRahmat!",
            "ru": f"🎉 <b>Подписка активирована!</b>\n\n📦 План: <b>{pname}</b>\n⏰ Действует до: <b>{end_str}</b>\n\nСпасибо!",
            "en": f"🎉 <b>Subscription activated!</b>\n\n📦 Plan: <b>{pname}</b>\n⏰ Valid until: <b>{end_str}</b>\n\nThank you!",
        }
        try:
            await context.bot.send_message(
                chat_id=telegram_id,
                text=activate_msg.get(lang, activate_msg["en"]),
                parse_mode=ParseMode.HTML,
                reply_markup=keyboards.main_menu_keyboard(lang),
            )
        except Exception as e:
            logger.error(f"Failed to notify user {telegram_id}: {e}")

        await query.answer("✅ Subscription activated!", show_alert=True)

    except Exception as e:
        logger.error(f"admin_approve error: {e}", exc_info=True)
        await query.answer("❌ Error. Check logs.", show_alert=True)


# ───────────────────────────────────────────────────────────────
# ADMIN: DECLINE
# ───────────────────────────────────────────────────────────────
async def admin_decline(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if str(query.from_user.id) != str(config.ADMIN_CHAT_ID):
        await query.answer("⛔ Admin only.", show_alert=True)
        return

    try:
        _, _, raw_id, raw_amount, plan_key = query.data.split(":", 4)
        telegram_id = int(raw_id)
        amount_uzs  = int(raw_amount)

        payment_key  = f"payment_{telegram_id}_{amount_uzs}"
        payment_info = context.bot_data.get(payment_key, {})
        payment_id   = payment_info.get("payment_id")

        if payment_id:
            db.reject_payment(payment_id, admin_note=f"declined by {query.from_user.id}")

        try:
            tg_user  = await context.bot.get_chat(telegram_id)
            uname    = tg_user.first_name or f"User_{telegram_id}"
            username = tg_user.username
        except Exception:
            uname, username = f"User_{telegram_id}", None

        user = db.get_user_by_telegram_id(telegram_id)
        lang = user.get("ui_language", "en") if user else "en"
        pname = _plan_name(plan_key, lang)

        declined_by = query.from_user.username or query.from_user.first_name
        orig_time   = payment_info.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        done_time   = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        admin_update = (
            f"❌ <b>DECLINED</b> by @{declined_by}\n"
            f"🌟 <b>Subscription Payment</b>\n"
            f"📅 Request: {orig_time}\n"
            f"👤 User ID: <code>{telegram_id}</code>\n"
            f"👤 Name: {uname}\n"
        )
        if username:
            admin_update += f"👤 @{username}\n"
        admin_update += (
            f"📦 Plan: <b>{pname}</b>\n"
            f"💰 Amount: <b>{amount_uzs:,} UZS</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"⏰ Declined: {done_time}"
        )

        await query.edit_message_text(admin_update, parse_mode=ParseMode.HTML)

        for aid, mid in payment_info.get("messages", {}).items():
            if str(aid) != str(query.from_user.id):
                try:
                    await context.bot.edit_message_text(
                        chat_id=aid, message_id=mid,
                        text=admin_update, parse_mode=ParseMode.HTML
                    )
                except Exception as e:
                    logger.error(f"Could not update admin {aid} message: {e}")

        context.bot_data.pop(payment_key, None)

        decline_msg = {
            "uz": f"❌ <b>To'lovingiz rad etildi.</b>\n\n📦 Reja: {pname}\n💰 Miqdor: {amount_uzs:,} so'm\n\nSavollar bo'lsa: {config.ADMIN_USERNAME}",
            "ru": f"❌ <b>Ваш платёж отклонён.</b>\n\n📦 План: {pname}\n💰 Сумма: {amount_uzs:,} сум\n\nВопросы: {config.ADMIN_USERNAME}",
            "en": f"❌ <b>Your payment was declined.</b>\n\n📦 Plan: {pname}\n💰 Amount: {amount_uzs:,} UZS\n\nContact: {config.ADMIN_USERNAME}",
        }
        try:
            await context.bot.send_message(
                chat_id=telegram_id,
                text=decline_msg.get(lang, decline_msg["en"]),
                parse_mode=ParseMode.HTML,
            )
        except Exception as e:
            logger.error(f"Failed to notify user {telegram_id}: {e}")

        await query.answer("❌ Payment declined.", show_alert=True)

    except Exception as e:
        logger.error(f"admin_decline error: {e}", exc_info=True)
        await query.answer("❌ Error. Check logs.", show_alert=True)


# ───────────────────────────────────────────────────────────────
# TELEGRAM STARS PAYMENT
# ───────────────────────────────────────────────────────────────
async def handle_stars_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    parts    = query.data.split(":")          # subpay:stars:1_month
    plan_key = parts[2]
    if plan_key not in SUBSCRIPTION_PLANS:
        return

    telegram_id = update.effective_user.id
    user = db.get_user_by_telegram_id(telegram_id)
    lang = user.get("ui_language", "en") if user else "en"
    plan_name = _plan_name(plan_key, lang)
    stars     = config.PREMIUM_STARS.get(plan_key, 150)

    context.user_data["stars_plan_key"] = plan_key

    await context.bot.send_invoice(
        chat_id=telegram_id,
        title=f"LangBridge Premium — {plan_name}",
        description=t("premium_features", lang),
        payload=f"premium:{telegram_id}:{plan_key}",
        currency="XTR",
        prices=[LabeledPrice(plan_name, stars)],
        provider_token=""
    )


async def pre_checkout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.pre_checkout_query.answer(ok=True)


async def successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    telegram_id = update.effective_user.id
    user = db.get_user_by_telegram_id(telegram_id)
    lang = user.get("ui_language", "en") if user else "en"

    payload = update.message.successful_payment.telegram_payment_charge_id
    plan_key = context.user_data.pop("stars_plan_key", "1_month")
    plan = SUBSCRIPTION_PLANS.get(plan_key, SUBSCRIPTION_PLANS["1_month"])
    plan_name = _plan_name(plan_key, lang)

    db.activate_premium(telegram_id, plan["duration_days"])

    payment_row = db.create_payment(
        user_id=user["id"], method="telegram_stars",
        amount=config.PREMIUM_STARS.get(plan_key), currency="XTR",
    )
    db.confirm_payment(payment_row["id"], admin_note=f"stars charge_id:{payload}")

    until   = datetime.now(timezone.utc) + timedelta(days=plan["duration_days"])
    end_str = until.strftime("%d.%m.%Y")

    ok_msg = {
        "uz": f"🎉 <b>To'lov muvaffaqiyatli!</b>\n\n📦 Reja: <b>{plan_name}</b>\n⏰ Amal qilish muddati: <b>{end_str}</b>",
        "ru": f"🎉 <b>Оплата прошла успешно!</b>\n\n📦 План: <b>{plan_name}</b>\n⏰ Действует до: <b>{end_str}</b>",
        "en": f"🎉 <b>Payment successful!</b>\n\n📦 Plan: <b>{plan_name}</b>\n⏰ Valid until: <b>{end_str}</b>",
    }
    await update.message.reply_text(
        ok_msg.get(lang, ok_msg["en"]),
        parse_mode=ParseMode.HTML,
        reply_markup=keyboards.main_menu_keyboard(lang),
    )


# ───────────────────────────────────────────────────────────────
# HANDLER LIST  (imported by main.py)
# ───────────────────────────────────────────────────────────────
def premium_handlers() -> list:
    return [
        # Plan selection
        CallbackQueryHandler(handle_plan_selection,   pattern=r"^subplan:"),
        # Payment method
        CallbackQueryHandler(handle_card_payment,     pattern=r"^subpay:card:"),
        CallbackQueryHandler(handle_stars_payment,    pattern=r"^subpay:stars:"),
        # Admin approve / decline
        CallbackQueryHandler(admin_approve,           pattern=r"^admpay:approve:"),
        CallbackQueryHandler(admin_decline,           pattern=r"^admpay:decline:"),
        # Telegram Stars
        PreCheckoutQueryHandler(pre_checkout),
        MessageHandler(filters.SUCCESSFUL_PAYMENT,    successful_payment),
        # Receipt (must be LAST so it doesn't swallow unrelated messages)
        MessageHandler(
            (filters.PHOTO | filters.Document.ALL | filters.TEXT) & ~filters.COMMAND,
            handle_receipt_submission,
        ),
    ]
