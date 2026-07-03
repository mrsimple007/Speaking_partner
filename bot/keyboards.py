from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.translations import (
    t,
    LANGUAGE_OPTIONS,
    LEVEL_OPTIONS,
    language_label,
    INTEREST_NAMES,
    interest_name,
)
COMMON_LANGUAGES = ["en", "ru", "uz", "tr", "ar"]

def language_keyboard(lang: str, field: str, show_all: bool = False) -> InlineKeyboardMarkup:
    codes = LANGUAGE_OPTIONS if show_all else COMMON_LANGUAGES
    buttons = [
        InlineKeyboardButton(language_label(c, lang), callback_data=f"{field}:{c}")
        for c in codes
    ]
    rows = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
    if not show_all:
        rows.append([InlineKeyboardButton(t("other_button", lang), callback_data=f"{field}_more")])
    return InlineKeyboardMarkup(rows)

def ui_language_keyboard() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="ui_lang:uz")],
        [InlineKeyboardButton("🇷🇺 Русский", callback_data="ui_lang:ru")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="ui_lang:en")],
    ]
    return InlineKeyboardMarkup(rows)


def language_keyboard(lang: str, prefix: str) -> InlineKeyboardMarkup:
    """
    Two languages per row with flag + name, e.g. '🇬🇧 English'.
    Signature unchanged (lang, prefix) so existing call sites keep working.
    """
    rows = []
    row = []
    for code in LANGUAGE_OPTIONS:
        row.append(InlineKeyboardButton(language_label(code, lang), callback_data=f"{prefix}:{code}"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    return InlineKeyboardMarkup(rows)


def level_keyboard(lang: str, prefix: str = "level") -> InlineKeyboardMarkup:
    rows = []
    row = []
    for level in LEVEL_OPTIONS:
        label = t("level_native", lang) if level == "native" else f"📊 {level}"
        row.append(InlineKeyboardButton(label, callback_data=f"{prefix}:{level}"))
        if len(row) == 3:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    return InlineKeyboardMarkup(rows)


def gender_keyboard(lang: str, prefix: str = "gender") -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(t("gender_male", lang), callback_data=f"{prefix}:male"),
            InlineKeyboardButton(t("gender_female", lang), callback_data=f"{prefix}:female"),
        ]
    ]
    return InlineKeyboardMarkup(rows)


def interests_keyboard(lang: str, selected: set, prefix: str = "interest") -> InlineKeyboardMarkup:
    rows = []
    row = []
    for code in INTEREST_NAMES.keys():
        label = interest_name(code, lang)
        if code in selected:
            label = "✅ " + label
        row.append(InlineKeyboardButton(label, callback_data=f"{prefix}:{code}"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton(t("done_button", lang), callback_data=f"{prefix}_done")])
    return InlineKeyboardMarkup(rows)


def main_menu_keyboard(lang: str) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(t("menu_find_partner", lang), callback_data="menu:find")],
        [InlineKeyboardButton(t("menu_profile", lang), callback_data="menu:profile")],
        [InlineKeyboardButton(t("menu_premium", lang), callback_data="menu:premium")],
        [InlineKeyboardButton(t("menu_settings", lang), callback_data="menu:settings")],
    ]
    return InlineKeyboardMarkup(rows)

def find_and_settings_keyboard(lang: str) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(t("menu_find_partner", lang), callback_data="menu:find")],
        [InlineKeyboardButton(t("menu_premium", lang), callback_data="menu:premium")],
        [InlineKeyboardButton(t("menu_settings", lang), callback_data="menu:settings")],
    ]
    return InlineKeyboardMarkup(rows)


def cancel_search_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(t("cancel_search_button", lang), callback_data="search:cancel")]]
    )


def chat_controls_keyboard(lang: str) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(t("next_partner_button", lang), callback_data="chat:next"),
            InlineKeyboardButton(t("end_chat_button", lang), callback_data="chat:end"),
        ],
        [InlineKeyboardButton(t("report_button", lang), callback_data="chat:report")],
    ]
    return InlineKeyboardMarkup(rows)


def report_reasons_keyboard(lang: str) -> InlineKeyboardMarkup:
    reasons = [
        ("spam", "report_reason_spam"),
        ("advertising", "report_reason_advertising"),
        ("harassment", "report_reason_harassment"),
        ("inappropriate_language", "report_reason_inappropriate"),
        ("other", "report_reason_other"),
    ]
    rows = [
        [InlineKeyboardButton(t(label_key, lang), callback_data=f"report_reason:{code}")]
        for code, label_key in reasons
    ]
    return InlineKeyboardMarkup(rows)


def premium_keyboard(lang: str) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(t("pay_with_stars_button", lang), callback_data="premium:stars")],
        [InlineKeyboardButton(t("pay_with_transfer_button", lang), callback_data="premium:transfer")],
    ]
    return InlineKeyboardMarkup(rows)


def settings_keyboard(lang: str, premium: bool = False) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(t("edit_profile_button", lang), callback_data="settings:edit_profile")],
        [InlineKeyboardButton(t("settings_change_ui_language", lang), callback_data="settings:ui_lang")],
    ]
    if premium:
        rows.append(
            [InlineKeyboardButton(t("filters_menu_button", lang), callback_data="settings:filters")]
        )
    return InlineKeyboardMarkup(rows)


def filters_gender_keyboard(lang: str, current: str = None) -> InlineKeyboardMarkup:
    def label(key, text_key):
        prefix = "✅ " if current == key else ""
        return prefix + t(text_key, lang)

    rows = [
        [InlineKeyboardButton(label(None, "filter_gender_any"), callback_data="filter_gender:any")],
        [
            InlineKeyboardButton(label("male", "gender_male"), callback_data="filter_gender:male"),
            InlineKeyboardButton(label("female", "gender_female"), callback_data="filter_gender:female"),
        ],
    ]
    return InlineKeyboardMarkup(rows)


def filters_interests_keyboard(lang: str, selected: set) -> InlineKeyboardMarkup:
    rows = []
    row = []
    for code in INTEREST_NAMES.keys():
        label = interest_name(code, lang)
        if code in selected:
            label = "✅ " + label
        row.append(InlineKeyboardButton(label, callback_data=f"filter_interest:{code}"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton(t("done_button", lang), callback_data="filter_interest_done")])
    return InlineKeyboardMarkup(rows)