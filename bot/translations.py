"""
All bot-facing UI strings live here, keyed by short identifiers.
Supported UI languages: 'uz' (Uzbek), 'ru' (Russian), 'en' (English).

Usage:
    from bot.translations import t
    t("welcome", lang="uz")
"""

TRANSLATIONS = {
    "choose_ui_language": {
        "uz": "Iltimos, bot tilini tanlang:",
        "ru": "Пожалуйста, выберите язык интерфейса:",
        "en": "Please choose the bot interface language:",
    },
    "welcome": {
        "uz": "Xush kelibsiz!\nKeling, til o'rganish uchun hamkor topamiz.",
        "ru": "Добро пожаловать!\nДавайте найдём вам языкового партнёра.",
        "en": "Welcome!\nLet's find your language partner.",
    },
    "ask_native_language": {
        "uz": "1-qadam: Sizning ona tilingiz qaysi?",
        "ru": "Шаг 1: Какой ваш родной язык?",
        "en": "Step 1: What is your native language?",
    },
    "ask_learning_language": {
        "uz": "2-qadam: Qaysi tilni o'rganmoqchisiz?",
        "ru": "Шаг 2: Какой язык вы хотите изучать?",
        "en": "Step 2: Which language do you want to learn?",
    },
    "ask_level": {
        "uz": "3-qadam: Til darajangiz qanday?",
        "ru": "Шаг 3: Каков ваш уровень языка?",
        "en": "Step 3: What is your language level?",
    },
    "ask_gender": {
        "uz": "4-qadam: Jinsingiz?",
        "ru": "Шаг 4: Ваш пол?",
        "en": "Step 4: Your gender?",
    },
    "ask_interests": {
        "uz": "5-qadam: Qiziqishlaringizni tanlang (maksimum 5 ta).",
        "ru": "Шаг 5: Выберите ваши интересы (максимум 5).",
        "en": "Step 5: Select your interests (maximum 5).",
    },
    "interests_saved": {
        "uz": "Ajoyib! Profilingiz saqlandi.",
        "ru": "Отлично! Ваш профиль сохранён.",
        "en": "Great! Your profile has been saved.",
    },
    "done_button": {
        "uz": "✅ Tayyor",
        "ru": "✅ Готово",
        "en": "✅ Done",
    },
    "main_menu": {
        "uz": "Asosiy menyu",
        "ru": "Главное меню",
        "en": "Main menu",
    },
    "menu_find_partner": {
        "uz": "🔍 Hamkor topish",
        "ru": "🔍 Найти партнёра",
        "en": "🔍 Find Partner",
    },
    "menu_profile": {
        "uz": "👤 Profil",
        "ru": "👤 Профиль",
        "en": "👤 Profile",
    },
    "menu_premium": {
        "uz": "⭐ Premium",
        "ru": "⭐ Премиум",
        "en": "⭐ Premium",
    },
    "menu_settings": {
        "uz": "⚙️ Sozlamalar",
        "ru": "⚙️ Настройки",
        "en": "⚙️ Settings",
    },
    "searching": {
        "uz": "🔎 Hamkor qidirilmoqda...\nO'rtacha kutish vaqti: ~30 soniya\nTopilganda avtomatik ulanasiz.",
        "ru": "🔎 Ищем партнёра...\nСреднее время ожидания: ~30 секунд\nВы будете подключены автоматически.",
        "en": "🔎 Looking for a partner...\nAverage waiting time: ~30 seconds\nYou will be connected automatically.",
    },
    "search_cancelled": {
        "uz": "Qidiruv bekor qilindi.",
        "ru": "Поиск отменён.",
        "en": "Search cancelled.",
    },
    "cancel_search_button": {
        "uz": "❌ Qidiruvni bekor qilish",
        "ru": "❌ Отменить поиск",
        "en": "❌ Cancel search",
    },
    "partner_found": {
        "uz": "🎉 Hamkor topildi!\nO'rganayotgan tili: {learning}\nDaraja: {level}\nQiziqishlari: {interests}\n\nSalom bering 👋",
        "ru": "🎉 Партнёр найден!\nИзучаемый язык: {learning}\nУровень: {level}\nИнтересы: {interests}\n\nПоздоровайтесь 👋",
        "en": "🎉 Partner Found!\nLearning language: {learning}\nLevel: {level}\nInterests: {interests}\n\nSay hello 👋",
    },
    "chat_controls_hint": {
        "uz": "Chat davomida tugmalardan foydalaning: Keyingisi / Tugatish / Shikoyat",
        "ru": "Во время чата используйте кнопки: Следующий / Завершить / Пожаловаться",
        "en": "During the chat use the buttons: Next / End / Report",
    },
    "next_partner_button": {
        "uz": "⏭ Keyingi hamkor",
        "ru": "⏭ Следующий партнёр",
        "en": "⏭ Next Partner",
    },
    "end_chat_button": {
        "uz": "🚪 Suhbatni tugatish",
        "ru": "🚪 Завершить чат",
        "en": "🚪 End Chat",
    },
    "report_button": {
        "uz": "🚩 Shikoyat qilish",
        "ru": "🚩 Пожаловаться",
        "en": "🚩 Report User",
    },
    "chat_ended_by_you": {
        "uz": "Suhbat tugatildi. Asosiy menyuga qaytdingiz.",
        "ru": "Чат завершён. Вы вернулись в главное меню.",
        "en": "Chat ended. You're back at the main menu.",
    },
    "partner_left": {
        "uz": "Hamkoringiz suhbatni tark etdi.",
        "ru": "Ваш партнёр покинул чат.",
        "en": "Your partner left the chat.",
    },
    "searching_new_partner": {
        "uz": "Yangi hamkor qidirilmoqda...",
        "ru": "Ищем нового партнёра...",
        "en": "Searching for another partner...",
    },
    "not_in_chat": {
        "uz": "Siz hozir suhbatda emassiz. Hamkor topish uchun menyudan foydalaning.",
        "ru": "Вы сейчас не в чате. Используйте меню, чтобы найти партнёра.",
        "en": "You're not in a chat right now. Use the menu to find a partner.",
    },
    "report_reason_prompt": {
        "uz": "Shikoyat sababini tanlang:",
        "ru": "Выберите причину жалобы:",
        "en": "Select a reason for the report:",
    },
    "report_reason_spam": {"uz": "Spam", "ru": "Спам", "en": "Spam"},
    "report_reason_advertising": {"uz": "Reklama", "ru": "Реклама", "en": "Advertising"},
    "report_reason_harassment": {"uz": "Tahqirlash", "ru": "Домогательства", "en": "Harassment"},
    "report_reason_inappropriate": {
        "uz": "Nomaqbul til",
        "ru": "Неприемлемый язык",
        "en": "Inappropriate language",
    },
    "report_reason_other": {"uz": "Boshqa", "ru": "Другое", "en": "Other"},
    "report_submitted": {
        "uz": "Shikoyatingiz qabul qilindi. Rahmat!",
        "ru": "Ваша жалоба принята. Спасибо!",
        "en": "Your report has been submitted. Thank you!",
    },
    "profile_header": {
        "uz": "👤 Sizning profilingiz",
        "ru": "👤 Ваш профиль",
        "en": "👤 Your profile",
    },
    "profile_body": {
        "uz": "Ona tili: {native}\nO'rganayotgan til: {learning}\nDaraja: {level}\nJins: {gender}\nQiziqishlar: {interests}\nPremium: {premium}",
        "ru": "Родной язык: {native}\nИзучаемый язык: {learning}\nУровень: {level}\nПол: {gender}\nИнтересы: {interests}\nПремиум: {premium}",
        "en": "Native language: {native}\nLearning language: {learning}\nLevel: {level}\nGender: {gender}\nInterests: {interests}\nPremium: {premium}",
    },
    "edit_profile_button": {
        "uz": "✏️ Profilni tahrirlash",
        "ru": "✏️ Редактировать профиль",
        "en": "✏️ Edit profile",
    },
    "premium_header": {
        "uz": "⭐ LangBridge Premium",
        "ru": "⭐ LangBridge Премиум",
        "en": "⭐ LangBridge Premium",
    },
    "premium_features": {
        "uz": "Imkoniyatlar:\n• Cheksiz hamkorlar\n• Faqat erkak/ayol filtri\n• Qiziqish bo'yicha filtr\n• Navbatda ustuvorlik",
        "ru": "Возможности:\n• Неограниченные совпадения\n• Фильтр по полу\n• Фильтр по интересам\n• Приоритет в очереди",
        "en": "Features:\n• Unlimited matches\n• Gender filter\n• Interest filter\n• Priority queue",
    },
    "pay_with_stars_button": {
        "uz": "⭐ Telegram Stars orqali to'lash",
        "ru": "⭐ Оплатить через Telegram Stars",
        "en": "⭐ Pay with Telegram Stars",
    },
    "pay_with_transfer_button": {
        "uz": "💳 Karta orqali o'tkazma",
        "ru": "💳 Перевод на карту",
        "en": "💳 Pay via card transfer",
    },
    "transfer_instructions": {
        "uz": "Quyidagi kartaga {amount} so'm o'tkazing:\n\nKarta raqami: {card}\nKarta egasi: {holder}\n\n{note}\n\nO'tkazma chekining skrinshotini shu yerga yuboring.",
        "ru": "Переведите {amount} сум на карту:\n\nНомер карты: {card}\nВладелец карты: {holder}\n\n{note}\n\nОтправьте скриншот чека сюда.",
        "en": "Transfer {amount} UZS to the card below:\n\nCard number: {card}\nCard holder: {holder}\n\n{note}\n\nSend a screenshot of the transfer receipt here.",
    },
    "transfer_proof_received": {
        "uz": "Skrinshot qabul qilindi! Admin tasdiqlagach, Premium faollashadi.",
        "ru": "Скриншот получен! Премиум активируется после подтверждения админом.",
        "en": "Screenshot received! Premium will activate once an admin confirms it.",
    },
    "premium_activated": {
        "uz": "🎉 Premium faollashtirildi!",
        "ru": "🎉 Премиум активирован!",
        "en": "🎉 Premium activated!",
    },
    "stars_payment_success": {
        "uz": "To'lov muvaffaqiyatli! Premium faollashtirildi.",
        "ru": "Оплата прошла успешно! Премиум активирован.",
        "en": "Payment successful! Premium has been activated.",
    },
    "settings_header": {
        "uz": "⚙️ Sozlamalar",
        "ru": "⚙️ Настройки",
        "en": "⚙️ Settings",
    },
    "settings_change_ui_language": {
        "uz": "🌐 Interfeys tilini o'zgartirish",
        "ru": "🌐 Изменить язык интерфейса",
        "en": "🌐 Change interface language",
    },
    "settings_delete_account": {
        "uz": "🗑 Akkauntni o'chirish",
        "ru": "🗑 Удалить аккаунт",
        "en": "🗑 Delete account",
    },
    "delete_confirm": {
        "uz": "Rostdan ham akkauntingizni butunlay o'chirmoqchimisiz? Bu qaytarib bo'lmaydi.",
        "ru": "Вы уверены, что хотите полностью удалить аккаунт? Это необратимо.",
        "en": "Are you sure you want to permanently delete your account? This cannot be undone.",
    },
    "confirm_yes": {"uz": "Ha, o'chirish", "ru": "Да, удалить", "en": "Yes, delete"},
    "confirm_no": {"uz": "Bekor qilish", "ru": "Отмена", "en": "Cancel"},
    "account_deleted": {
        "uz": "Akkauntingiz o'chirildi. Xayr!",
        "ru": "Ваш аккаунт удалён. Прощайте!",
        "en": "Your account has been deleted. Goodbye!",
    },
    "level_native": {"uz": "Ona tili", "ru": "Родной", "en": "Native"},
    "gender_male": {"uz": "Erkak", "ru": "Мужской", "en": "Male"},
    "gender_female": {"uz": "Ayol", "ru": "Женский", "en": "Female"},
    "max_interests_reached": {
        "uz": "Siz allaqachon 5 ta qiziqish tanladingiz.",
        "ru": "Вы уже выбрали 5 интересов.",
        "en": "You've already selected 5 interests.",
    },
    "already_in_queue": {
        "uz": "Siz allaqachon navbatdasiz.",
        "ru": "Вы уже в очереди.",
        "en": "You're already in the queue.",
    },
    "already_in_chat": {
        "uz": "Siz hozir suhbatdasiz. Avval uni tugating.",
        "ru": "Вы сейчас в чате. Сначала завершите его.",
        "en": "You're currently in a chat. End it first.",
    },
    "complete_onboarding_first": {
        "uz": "Iltimos, avval profilni to'ldiring.",
        "ru": "Пожалуйста, сначала заполните профиль.",
        "en": "Please complete your profile first.",
    },
    "premium_only_feature": {
        "uz": "Bu funksiya faqat Premium foydalanuvchilar uchun.",
        "ru": "Эта функция доступна только для Премиум пользователей.",
        "en": "This feature is only available for Premium users.",
    },
}

# Languages users can pick as native/learning language (not the UI language)
LANGUAGE_OPTIONS = ["uz", "ru", "en", "tr"]
LANGUAGE_NAMES = {
    "uz": {"uz": "O'zbekcha", "ru": "Узбекский", "en": "Uzbek"},
    "ru": {"uz": "Ruscha", "ru": "Русский", "en": "Russian"},
    "en": {"uz": "Inglizcha", "ru": "Английский", "en": "English"},
    "tr": {"uz": "Turkcha", "ru": "Турецкий", "en": "Turkish"},
}

LEVEL_OPTIONS = ["A1", "A2", "B1", "B2", "C1", "C2", "native"]

INTEREST_NAMES = {
    "programming": {"uz": "Dasturlash", "ru": "Программирование", "en": "Programming"},
    "movies": {"uz": "Filmlar", "ru": "Фильмы", "en": "Movies"},
    "football": {"uz": "Futbol", "ru": "Футбол", "en": "Football"},
    "chess": {"uz": "Shaxmat", "ru": "Шахматы", "en": "Chess"},
    "music": {"uz": "Musiqa", "ru": "Музыка", "en": "Music"},
    "travel": {"uz": "Sayohat", "ru": "Путешествия", "en": "Travel"},
    "business": {"uz": "Biznes", "ru": "Бизнес", "en": "Business"},
    "reading": {"uz": "Kitob o'qish", "ru": "Чтение", "en": "Reading"},
    "anime": {"uz": "Anime", "ru": "Аниме", "en": "Anime"},
    "cooking": {"uz": "Pazandachilik", "ru": "Кулинария", "en": "Cooking"},
    "technology": {"uz": "Texnologiya", "ru": "Технологии", "en": "Technology"},
    "startups": {"uz": "Startaplar", "ru": "Стартапы", "en": "Startups"},
}


def t(key: str, lang: str = "en", **kwargs) -> str:
    """Fetch a translated string and format it with kwargs if provided."""
    entry = TRANSLATIONS.get(key)
    if entry is None:
        return key
    text = entry.get(lang) or entry.get("en") or key
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, IndexError):
            return text
    return text


def language_name(code: str, lang: str = "en") -> str:
    return LANGUAGE_NAMES.get(code, {}).get(lang, code)


def interest_name(code: str, lang: str = "en") -> str:
    return INTEREST_NAMES.get(code, {}).get(lang, code)
