"""
All bot-facing UI strings live here, keyed by short identifiers.
Supported UI languages: 'uz' (Uzbek), 'ru' (Russian), 'en' (English).

Usage:
    from bot.translations import t
    t("welcome", lang="uz")
"""

TRANSLATIONS = {
    "choose_ui_language": {
        "uz": "👋 Assalomu alaykum!\nBotdan foydalanish uchun tilni tanlang:",
        "ru": "👋 Здравствуйте!\nВыберите язык, на котором вам удобно пользоваться ботом:",
        "en": "👋 Hey there!\nPick the language you'd like to use the bot in:",
    },
    "welcome": {
        "uz": "🎉 Xush kelibsiz, LingoMatch oilasiga!\n\Biz siz uchun mukammal til partnerini topamiz 🤝\nBir necha oddiy savollarga javob bering ⏱",
        "ru": "🎉 Добро пожаловать в LingoMatch!\n\nДавайте подберём для вас идеального языкового партнёра 🤝\nОтветьте на пару простых вопросов — это займёт всего минуту ⏱",
        "en": "🎉 Welcome to LingoMatch!\n\nLet's find you the perfect language exchange partner 🤝\nJust answer a few quick questions — it'll take about a minute ⏱",
    },
    "ask_native_language": {
        "uz": "🗣 1-qadam: Sizning ona tilingiz qaysi?\n\nBu bizga sizni to'g'ri partner bilan bog'lashga yordam beradi.",
        "ru": "🗣 Шаг 1: Какой язык для вас родной?\n\nЭто поможет нам подобрать вам подходящего собеседника.",
        "en": "🗣 Step 1: What's your native language?\n\nThis helps us match you with the right partner.",
    },
    "ask_learning_language": {
        "uz": "📚 2-qadam: Qaysi tilni o'rganmoqchisiz?\n\nShu tilda gaplashadigan partner topamiz 🌍",
        "ru": "📚 Шаг 2: Какой язык вы хотите изучать?\n\nМы найдём вам собеседника, говорящего на этом языке 🌍",
        "en": "📚 Step 2: Which language do you want to learn?\n\nWe'll find you a partner who speaks it 🌍",
    },
    "ask_level": {
        "uz": "📈 3-qadam: Til darajangiz qanday?\n\nBu partneringiz bilan qulay muloqot qilishga yordam beradi.",
        "ru": "📈 Шаг 3: Какой у вас уровень языка?\n\nЭто поможет вам комфортно общаться с партнёром.",
        "en": "📈 Step 3: What's your language level?\n\nThis helps make conversations comfortable for both of you.",
    },
    "ask_gender": {
        "uz": "🧑‍🤝‍🧑 4-qadam: Jinsingizni tanlang.\n\nBu ma'lumot faqat moslashtirish uchun ishlatiladi.",
        "ru": "🧑‍🤝‍🧑 Шаг 4: Укажите ваш пол.\n\nЭта информация используется только для подбора партнёра.",
        "en": "🧑‍🤝‍🧑 Step 4: What's your gender?\n\nThis is only used to help with matching.",
    },
    "ask_interests": {
        "uz": "🎯 5-qadam: Qiziqishlaringizni tanlang (maksimum 5 ta).\n\nUmumiy qiziqishlar suhbatni yanada qiziqarli qiladi! ✨",
        "ru": "🎯 Шаг 5: Выберите ваши интересы (максимум 5).\n\nОбщие интересы делают беседу интереснее! ✨",
        "en": "🎯 Step 5: Pick your interests (up to 5).\n\nShared interests make conversations way more fun! ✨",
    },
    "interests_saved": {
        "uz": "✅ Ajoyib! Profilingiz muvaffaqiyatli saqlandi.\n\nEndi partner topishni boshlashingiz mumkin 🚀",
        "ru": "✅ Отлично! Ваш профиль успешно сохранён.\n\nТеперь вы можете начать искать партнёра 🚀",
        "en": "✅ Awesome! Your profile has been saved.\n\nYou're all set to start finding a partner 🚀",
    },
    "done_button": {
        "uz": "✅ Tayyor",
        "ru": "✅ Готово",
        "en": "✅ Done",
    },
    "main_menu": {
        "uz": "🏠 Asosiy menyu\n\nQuyidagilardan birini tanlang:",
        "ru": "🏠 Главное меню\n\nВыберите один из пунктов:",
        "en": "🏠 Main menu\n\nChoose an option below:",
    },
    "menu_find_partner": {
        "uz": "🔍 Partner topish",
        "ru": "🔍 Найти партнёра",
        "en": "🔍 Find Partner",
    },
    "menu_profile": {
        "uz": "👤 Mening profilim",
        "ru": "👤 Мой профиль",
        "en": "👤 My Profile",
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
        "uz": "🔎 partner qidirilmoqda...\n\n⏱ O'rtacha kutish vaqti: ~30 soniya\n🔔 Topilgan zahoti avtomatik ulanasiz.\n\nBiroz sabr qiling 🙂",
        "ru": "🔎 Ищем для вас партнёра...\n\n⏱ Среднее время ожидания: ~30 секунд\n🔔 Как только найдём — подключим вас автоматически.\n\nЧуть-чуть терпения 🙂",
        "en": "🔎 Looking for a partner...\n\n⏱ Average wait time: ~30 seconds\n🔔 You'll be connected automatically the moment we find one.\n\nHang tight 🙂",
    },
    "search_cancelled": {
        "uz": "🚫 Qidiruv bekor qilindi.\n\nIstalgan vaqt yana urinib ko'rishingiz mumkin!",
        "ru": "🚫 Поиск отменён.\n\nВы можете попробовать снова в любой момент!",
        "en": "🚫 Search cancelled.\n\nFeel free to try again anytime!",
    },
    "cancel_search_button": {
        "uz": "❌ Qidiruvni bekor qilish",
        "ru": "❌ Отменить поиск",
        "en": "❌ Cancel search",
    },
    "partner_found": {
        "uz": "🎉 Speaking Partner topildi!\n\n📚 O'rganayotgan tili: {learning}\n📈 Daraja: {level}\n🎯 Qiziqishlari: {interests}\n\n👋 Salom bering va suhbatni boshlang!",
        "ru": "🎉 Партнёр найден!\n\n📚 Изучаемый язык: {learning}\n📈 Уровень: {level}\n🎯 Интересы: {interests}\n\n👋 Поздоровайтесь и начните беседу!",
        "en": "🎉 Partner Found!\n\n📚 Learning language: {learning}\n📈 Level: {level}\n🎯 Interests: {interests}\n\n👋 Say hello and start chatting!",
    },
    "chat_controls_hint": {
        "uz": "💬 Chat davomida quyidagi tugmalardan foydalaning:\n⏭ Keyingisi — boshqa partner bilan tanishish\n🚪 Tugatish — suhbatni yakunlash\n🚩 Shikoyat — muammo haqida xabar berish",
        "ru": "💬 Во время чата используйте кнопки:\n⏭ Следующий — найти другого партнёра\n🚪 Завершить — закончить чат\n🚩 Пожаловаться — сообщить о проблеме",
        "en": "💬 During the chat, use these buttons:\n⏭ Next — meet a different partner\n🚪 End — finish the chat\n🚩 Report — flag an issue",
    },
    "next_partner_button": {
        "uz": "⏭ Keyingi partner",
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
        "uz": "👋 Suhbat tugatildi.\n\nAsosiy menyuga qaytdingiz. Yangi partner topishni xohlaysizmi?",
        "ru": "👋 Чат завершён.\n\nВы вернулись в главное меню. Хотите найти нового партнёра?",
        "en": "👋 Chat ended.\n\nYou're back at the main menu. Want to find a new partner?",
    },
    "partner_left": {
        "uz": "😔 Partneringiz suhbatni tark etdi.\n\nXavotir olmang — yangi partner topish oson! Shunchaki pastdagi knopkadan foydalaning",
        "ru": "😔 Ваш партнёр покинул чат.\n\nНе расстраивайтесь — найти нового партнёра легко!",
        "en": "😔 Your partner left the chat.\n\nNo worries — finding a new one is easy!",
    },
    "searching_new_partner": {
        "uz": "🔎 Yangi speakingpartner qidirilmoqda...",
        "ru": "🔎 Ищем нового партнёра...",
        "en": "🔎 Searching for another partner...",
    },
    "not_in_chat": {
        "uz": "ℹ️ Suhbatingiz tugatildi.\n\n Yangi partner topish uchun quyidagi knopkadan foydalaning 🔍",
        "ru": "ℹ️ Вы сейчас не в чате.\n\nИспользуйте главное меню, чтобы найти партнёра 🔍",
        "en": "ℹ️ You're not in a chat right now.\n\nUse the main menu to find a partner 🔍",
    },
    "report_reason_prompt": {
        "uz": "🚩 Shikoyat sababini tanlang:",
        "ru": "🚩 Выберите причину жалобы:",
        "en": "🚩 Select a reason for your report:",
    },
    "report_reason_spam": {"uz": "📩 Spam", "ru": "📩 Спам", "en": "📩 Spam"},
    "report_reason_advertising": {"uz": "📢 Reklama", "ru": "📢 Реклама", "en": "📢 Advertising"},
    "report_reason_harassment": {"uz": "🚫 Tahqirlash", "ru": "🚫 Домогательства", "en": "🚫 Harassment"},
    "report_reason_inappropriate": {
        "uz": "🤬 Nomaqbul til",
        "ru": "🤬 Неприемлемый язык",
        "en": "🤬 Inappropriate language",
    },
    "report_reason_other": {"uz": "❓ Boshqa", "ru": "❓ Другое", "en": "❓ Other"},
    "report_submitted": {
        "uz": "✅ Shikoyatingiz qabul qilindi. E'tiboringiz uchun rahmat! 🙏\n\nJamoamiz tez orada ko'rib chiqadi.",
        "ru": "✅ Ваша жалоба принята. Спасибо за бдительность! 🙏\n\nНаша команда скоро её рассмотрит.",
        "en": "✅ Your report has been submitted. Thanks for looking out! 🙏\n\nOur team will review it shortly.",
    },
    "profile_header": {
        "uz": "👤 Sizning profilingiz",
        "ru": "👤 Ваш профиль",
        "en": "👤 Your Profile",
    },
    "profile_body": {
        "uz": "🗣 Ona tili: {native}\n📚 O'rganayotgan til: {learning}\n📈 Daraja: {level}\n🧑‍🤝‍🧑 Jins: {gender}\n🎯 Qiziqishlar: {interests}\n⭐ Premium: {premium}",
        "ru": "🗣 Родной язык: {native}\n📚 Изучаемый язык: {learning}\n📈 Уровень: {level}\n🧑‍🤝‍🧑 Пол: {gender}\n🎯 Интересы: {interests}\n⭐ Премиум: {premium}",
        "en": "🗣 Native language: {native}\n📚 Learning language: {learning}\n📈 Level: {level}\n🧑‍🤝‍🧑 Gender: {gender}\n🎯 Interests: {interests}\n⭐ Premium: {premium}",
    },
    "edit_profile_button": {
        "uz": "✏️ Profilni tahrirlash",
        "ru": "✏️ Редактировать профиль",
        "en": "✏️ Edit Profile",
    },
    "premium_header": {
        "uz": "⭐ LingoMatch Premium\n\nMuloqotni keyingi bosqichga olib chiqing!",
        "ru": "⭐ LingoMatch Премиум\n\nВыведите общение на новый уровень!",
        "en": "⭐ LingoMatch Premium\n\nTake your language exchange to the next level!",
    },
    "premium_features": {
        "uz": "💎 Imkoniyatlar:\n♾ Cheksiz partnerlar\n🧑‍🤝‍🧑 Jins bo'yicha filtr\n🎯 Qiziqish bo'yicha filtr\n⚡ Navbatda ustuvorlik",
        "ru": "💎 Возможности:\n♾ Неограниченные совпадения\n🧑‍🤝‍🧑 Фильтр по полу\n🎯 Фильтр по интересам\n⚡ Приоритет в очереди",
        "en": "💎 Features:\n♾ Unlimited matches\n🧑‍🤝‍🧑 Gender filter\n🎯 Interest filter\n⚡ Priority queue",
    },
    "pay_with_stars_button": {
        "uz": "⭐ Telegram Stars orqali to'lash",
        "ru": "⭐ Оплатить через Telegram Stars",
        "en": "⭐ Pay with Telegram Stars",
    },
    "pay_with_transfer_button": {
        "uz": "💳 Karta orqali o'tkazma",
        "ru": "💳 Перевод на карту",
        "en": "💳 Pay via Card Transfer",
    },
    "transfer_instructions": {
        "uz": "💳 Quyidagi kartaga {amount} so'm o'tkazing:\n\n🔢 Karta raqami: {card}\n👤 Karta egasi: {holder}\n\n📝 {note}\n\n📸 O'tkazma chekining skrinshotini shu yerga yuboring.",
        "ru": "💳 Переведите {amount} сум на карту:\n\n🔢 Номер карты: {card}\n👤 Владелец карты: {holder}\n\n📝 {note}\n\n📸 Отправьте скриншот чека сюда.",
        "en": "💳 Transfer {amount} UZS to the card below:\n\n🔢 Card number: {card}\n👤 Card holder: {holder}\n\n📝 {note}\n\n📸 Send a screenshot of the receipt here.",
    },
    "transfer_proof_received": {
        "uz": "📸 Skrinshot qabul qilindi!\n\n⏳ Admin tasdiqlagach, Premium avtomatik faollashadi.",
        "ru": "📸 Скриншот получен!\n\n⏳ Премиум активируется автоматически после подтверждения админом.",
        "en": "📸 Screenshot received!\n\n⏳ Premium will activate automatically once an admin confirms it.",
    },
    "premium_activated": {
        "uz": "🎉 Premium faollashtirildi!\n\nEndi barcha imkoniyatlardan foydalanishingiz mumkin ⭐",
        "ru": "🎉 Премиум активирован!\n\nТеперь вам доступны все возможности ⭐",
        "en": "🎉 Premium activated!\n\nAll the perks are now unlocked for you ⭐",
    },
    "stars_payment_success": {
        "uz": "✅ To'lov muvaffaqiyatli o'tdi!\n\n🎉 Premium faollashtirildi.",
        "ru": "✅ Оплата прошла успешно!\n\n🎉 Премиум активирован.",
        "en": "✅ Payment successful!\n\n🎉 Premium has been activated.",
    },
    "settings_header": {
        "uz": "⚙️ Sozlamalar",
        "ru": "⚙️ Настройки",
        "en": "⚙️ Settings",
    },
    "settings_change_ui_language": {
        "uz": "🌐 Interfeys tilini o'zgartirish",
        "ru": "🌐 Изменить язык интерфейса",
        "en": "🌐 Change Interface Language",
    },
    "settings_delete_account": {
        "uz": "🗑 Akkauntni o'chirish",
        "ru": "🗑 Удалить аккаунт",
        "en": "🗑 Delete Account",
    },
    "delete_confirm": {
        "uz": "⚠️ Rostdan ham akkauntingizni butunlay o'chirmoqchimisiz?\n\nBu amalni qaytarib bo'lmaydi — barcha ma'lumotlaringiz yo'qoladi.",
        "ru": "⚠️ Вы уверены, что хотите полностью удалить аккаунт?\n\nЭто действие необратимо — все ваши данные будут потеряны.",
        "en": "⚠️ Are you sure you want to permanently delete your account?\n\nThis can't be undone — all your data will be lost.",
    },
    "confirm_yes": {"uz": "✅ Ha, o'chirish", "ru": "✅ Да, удалить", "en": "✅ Yes, delete"},
    "confirm_no": {"uz": "❌ Bekor qilish", "ru": "❌ Отмена", "en": "❌ Cancel"},
    "account_deleted": {
        "uz": "🗑 Akkauntingiz o'chirildi.\n\nBiz bilan bo'lganingiz uchun rahmat — xayr! 👋",
        "ru": "🗑 Ваш аккаунт удалён.\n\nСпасибо, что были с нами — прощайте! 👋",
        "en": "🗑 Your account has been deleted.\n\nThanks for being with us — goodbye! 👋",
    },
    "level_native": {"uz": "🏅 Ona tili", "ru": "🏅 Родной", "en": "🏅 Native"},
    "gender_male": {"uz": "👨 Erkak", "ru": "👨 Мужской", "en": "👨 Male"},
    "gender_female": {"uz": "👩 Ayol", "ru": "👩 Женский", "en": "👩 Female"},
    "max_interests_reached": {
        "uz": "⚠️ Siz allaqachon 5 ta qiziqish tanladingiz.\n\nDavom etish uchun avval birini bekor qiling.",
        "ru": "⚠️ Вы уже выбрали 5 интересов.\n\nЧтобы продолжить, сначала уберите один из них.",
        "en": "⚠️ You've already picked 5 interests.\n\nRemove one to add another.",
    },
    "already_in_queue": {
        "uz": "⏳ Siz allaqachon navbatdasiz.\n\nBiroz kuting, tez orada partner topamiz!",
        "ru": "⏳ Вы уже в очереди.\n\nНемного подождите, мы скоро найдём вам партнёра!",
        "en": "⏳ You're already in the queue.\n\nHang tight, we'll find you a partner soon!",
    },
    "already_in_chat": {
        "uz": "💬 Siz hozir suhbatdasiz.\n\nYangisini boshlash uchun avval joriy suhbatni tugating.",
        "ru": "💬 Вы сейчас в чате.\n\nЧтобы начать новый, сначала завершите текущий.",
        "en": "💬 You're currently in a chat.\n\nEnd it first before starting a new one.",
    },
    "complete_onboarding_first": {
        "uz": "📝 Iltimos, avval profilingizni to'ldiring.\n\nBu bor-yo'g'i 1 daqiqa vaqt oladi!",
        "ru": "📝 Пожалуйста, сначала заполните профиль.\n\nЭто займёт всего минуту!",
        "en": "📝 Please complete your profile first.\n\nIt only takes a minute!",
    },
    "premium_only_feature": {
        "uz": "⭐ Bu funksiya faqat Premium foydalanuvchilar uchun.\n\nUpgrade qilish uchun Premium bo'limiga o'ting!",
        "ru": "⭐ Эта функция доступна только для Премиум пользователей.\n\nПерейдите в раздел Премиум, чтобы улучшить аккаунт!",
        "en": "⭐ This feature is only available for Premium users.\n\nCheck out the Premium section to upgrade!",
    },


"start_intro": {
    "uz": "🤝 LingoMatch — bu til o'rganish uchun speaking partneri topishga yordam beruvchi bot.\n\nBotdan foydalanish juda oson:\n1️⃣ Profilingizni to'ldirasiz\n2️⃣ \"🔍 Partner topish\" tugmasни bosasiz\n3️⃣ Sizga mos partner topilgach, suhbatни boshlaysiz!\n\nBoshladik 👇",
    "ru": "🤝 LingoMatch — бот, который помогает найти партнёра для языкового обмена.\n\nПользоваться очень просто:\n1️⃣ Заполните профиль\n2️⃣ Нажмите «🔍 Найти партнёра»\n3️⃣ Как только найдём подходящего собеседника — начинайте общение!\n\nНачнём 👇",
    "en": "🤝 LingoMatch is a bot that helps you find a language exchange partner to practice with.\n\nHere's how it works:\n1️⃣ Fill in your profile\n2️⃣ Tap \"🔍 Find Partner\"\n3️⃣ Once we match you, start chatting!\n\nLet's get started 👇",
},



"main_menu_header": {
    "uz": "👋 Xush kelibsiz, {name}!\n\nMana sizning profilingiz:",
    "ru": "👋 С возвращением, {name}!\n\nВот ваш профиль:",
    "en": "👋 Welcome back, {name}!\n\nHere's your profile:",
},


"main_menu_footer": {
    "uz": "\n👇 Speaking partner topish uchun pastdagi \"🔍 Partner topish\" tugmasini bosing.",
    "ru": "\n👇 Чтобы найти собеседника, нажмите кнопку \"🔍 Найти партнёра\" ниже.",
    "en": "\n👇 Tap the \"🔍 Find Partner\" button below to find a speaking partner.",
},


"filters_menu_button": {
    "uz": "🎛 Premium uchun moslashtirilgan filtrlar",
    "ru": "🎛 Персональные фильтры",
    "en": "🎛 Custom Filters",
},
"filters_header": {
    "uz": "🎛 Filtrlaringiz\n\nSizda Premium bor. Shuning uchun bu sozlamalar faqat siz uchun partner tanlashda ishlatiladi.",
    "ru": "🎛 Ваши фильтры\n\nЭти настройки используются только при подборе партнёра для вас.",
    "en": "🎛 Your Filters\n\nThese settings are only used when finding a partner for you.",
},
"filters_gender_prompt": {
    "uz": "🧑‍🤝‍🧑 Speaking Partner jinsini tanlang:",
    "ru": "🧑‍🤝‍🧑 Выберите пол партнёра:",
    "en": "🧑‍🤝‍🧑 Choose partner gender:",
},
"filter_gender_any": {"uz": "🌍 Farqi yo'q", "ru": "🌍 Не важно", "en": "🌍 Any"},
"filters_interests_prompt": {
    "uz": "🎯 Umumiy bo'lishi kerak bo'lgan qiziqishlarni tanlang (ixtiyoriy):",
    "ru": "🎯 Выберите общие интересы (необязательно):",
    "en": "🎯 Pick interests your partner should share (optional):",
},
"filters_saved": {
    "uz": "✅ Filtrlaringiz saqlandi!",
    "ru": "✅ Ваши фильтры сохранены!",
    "en": "✅ Your filters have been saved!",
},


"other_button": {"uz": "🌐 Boshqa", "ru": "🌐 Другой", "en": "🌐 Other"},


}

# ─────────────────────────────────────────────────────────────
# Languages users can pick as native/learning language
# (not the UI language — UI is only uz/ru/en)
# ─────────────────────────────────────────────────────────────
LANGUAGE_OPTIONS = [
    "uz", "ru", "en", "tr", "ar", "es", "fr",
    "de", "it", "pt", "zh", "ja", "ko", "hi",
    "kk", "ky", "tg", "fa",
]

# Flag emoji shown next to each language name in keyboards
LANGUAGE_FLAGS = {
    "uz": "🇺🇿",
    "ru": "🇷🇺",
    "en": "🇬🇧",
    "tr": "🇹🇷",
    "ar": "🇸🇦",
    "es": "🇪🇸",
    "fr": "🇫🇷",
    "de": "🇩🇪",
    "it": "🇮🇹",
    "pt": "🇵🇹",
    "zh": "🇨🇳",
    "ja": "🇯🇵",
    "ko": "🇰🇷",
    "hi": "🇮🇳",
    "kk": "🇰🇿",
    "ky": "🇰🇬",
    "tg": "🇹🇯",
    "fa": "🇮🇷",
}

LANGUAGE_NAMES = {
    "uz": {"uz": "O'zbekcha", "ru": "Узбекский", "en": "Uzbek"},
    "ru": {"uz": "Ruscha", "ru": "Русский", "en": "Russian"},
    "en": {"uz": "Inglizcha", "ru": "Английский", "en": "English"},
    "tr": {"uz": "Turkcha", "ru": "Турецкий", "en": "Turkish"},
    "ar": {"uz": "Arabcha", "ru": "Арабский", "en": "Arabic"},
    "es": {"uz": "Ispancha", "ru": "Испанский", "en": "Spanish"},
    "fr": {"uz": "Fransuzcha", "ru": "Французский", "en": "French"},
    "de": {"uz": "Nemischa", "ru": "Немецкий", "en": "German"},
    "it": {"uz": "Italyancha", "ru": "Итальянский", "en": "Italian"},
    "pt": {"uz": "Portugalcha", "ru": "Португальский", "en": "Portuguese"},
    "zh": {"uz": "Xitoycha", "ru": "Китайский", "en": "Chinese"},
    "ja": {"uz": "Yaponcha", "ru": "Японский", "en": "Japanese"},
    "ko": {"uz": "Koreyscha", "ru": "Корейский", "en": "Korean"},
    "hi": {"uz": "Hindcha", "ru": "Хинди", "en": "Hindi"},
    "kk": {"uz": "Qozoqcha", "ru": "Казахский", "en": "Kazakh"},
    "ky": {"uz": "Qirg'izcha", "ru": "Киргизский", "en": "Kyrgyz"},
    "tg": {"uz": "Tojikcha", "ru": "Таджикский", "en": "Tajik"},
    "fa": {"uz": "Forscha", "ru": "Персидский", "en": "Persian"},
}

LEVEL_OPTIONS = ["A1", "A2", "B1", "B2", "C1", "C2", "native"]

INTEREST_NAMES = {
    "programming": {"uz": "💻 Dasturlash", "ru": "💻 Программирование", "en": "💻 Programming"},
    "movies": {"uz": "🎬 Filmlar", "ru": "🎬 Фильмы", "en": "🎬 Movies"},
    "football": {"uz": "⚽ Futbol", "ru": "⚽ Футбол", "en": "⚽ Football"},
    "chess": {"uz": "♟ Shaxmat", "ru": "♟ Шахматы", "en": "♟ Chess"},
    "music": {"uz": "🎵 Musiqa", "ru": "🎵 Музыка", "en": "🎵 Music"},
    "travel": {"uz": "✈️ Sayohat", "ru": "✈️ Путешествия", "en": "✈️ Travel"},
    "business": {"uz": "💼 Biznes", "ru": "💼 Бизнес", "en": "💼 Business"},
    "reading": {"uz": "📖 Kitob o'qish", "ru": "📖 Чтение", "en": "📖 Reading"},
    "anime": {"uz": "🎌 Anime", "ru": "🎌 Аниме", "en": "🎌 Anime"},
    "cooking": {"uz": "🍳 Pazandachilik", "ru": "🍳 Кулинария", "en": "🍳 Cooking"},
    "technology": {"uz": "🖥 Texnologiya", "ru": "🖥 Технологии", "en": "🖥 Technology"},
    "startups": {"uz": "🚀 Startaplar", "ru": "🚀 Стартапы", "en": "🚀 Startups"},
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
    """Plain language name, no flag (used in profile text etc.)."""
    return LANGUAGE_NAMES.get(code, {}).get(lang, code)


def language_label(code: str, lang: str = "en") -> str:
    """Flag + language name, for buttons."""
    flag = LANGUAGE_FLAGS.get(code, "")
    name = language_name(code, lang)
    return f"{flag} {name}".strip()


def interest_name(code: str, lang: str = "en") -> str:
    return INTEREST_NAMES.get(code, {}).get(lang, code)