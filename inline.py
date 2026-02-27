from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import TEXTS


def t(lang: str, key: str) -> str:
    return TEXTS.get(lang, TEXTS["ru"]).get(key, key)


def terms_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "terms_btn"), callback_data="agree_terms")
    return builder.as_markup()


def welcome_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "continue_btn"), callback_data="go_main")
    return builder.as_markup()


def main_menu_kb(lang: str = "ru", site_url: str = "") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_deal"), callback_data="create_deal")
    builder.button(text=t(lang, "btn_profile"), callback_data="profile")
    builder.button(text=t(lang, "btn_requisites"), callback_data="requisites")
    builder.button(text=t(lang, "btn_language"), callback_data="language")
    builder.button(text=t(lang, "btn_support"), callback_data="support")
    builder.button(text=t(lang, "btn_site"), url=site_url or "https://playerok.com")
    builder.adjust(1)
    return builder.as_markup()


def deal_type_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_gift"), callback_data="deal_type_gift")
    builder.button(text=t(lang, "btn_back"), callback_data="go_main")
    builder.adjust(1)
    return builder.as_markup()


def currency_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    currencies = [
        ("🇷🇺 RUB", "cur_RUB"), ("🇪🇺 EUR", "cur_EUR"), ("🇺🇿 UZS", "cur_UZS"),
        ("🇰🇬 KGS", "cur_KGS"), ("🇰🇿 KZT", "cur_KZT"), ("🌟 Stars", "cur_Stars"),
        ("🇺🇦 UAH", "cur_UAH"), ("🇧🇾 BYN", "cur_BYN"),
        ("💰 USDT", "cur_USDT"), ("💎 TON", "cur_TON"),
    ]
    for text, data in currencies:
        builder.button(text=text, callback_data=data)
    builder.button(text=t(lang, "btn_back"), callback_data="create_deal")
    builder.adjust(2)
    return builder.as_markup()


def back_to_deal_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_back"), callback_data="create_deal")
    return builder.as_markup()


def deal_created_kb(lang: str, deal_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cancel_deal"), callback_data=f"cancel_deal_{deal_id}")
    return builder.as_markup()


def cancel_deal_confirm_kb(lang: str, deal_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_yes_cancel"), callback_data=f"confirm_cancel_{deal_id}")
    builder.button(text=t(lang, "btn_no"), callback_data=f"view_deal_{deal_id}")
    builder.adjust(2)
    return builder.as_markup()


def profile_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_topup"), callback_data="topup_info")
    builder.button(text=t(lang, "btn_back"), callback_data="go_main")
    builder.adjust(1)
    return builder.as_markup()


def topup_info_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_understood"), callback_data="topup_choose")
    return builder.as_markup()


def topup_choose_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_card"), callback_data="topup_card")
    builder.button(text=t(lang, "btn_ton"), callback_data="topup_ton")
    builder.button(text=t(lang, "btn_back"), callback_data="profile")
    builder.adjust(2)
    return builder.as_markup()


def topup_payment_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_withdraw"), callback_data="withdraw")
    builder.button(text=t(lang, "btn_back"), callback_data="topup_choose")
    builder.adjust(1)
    return builder.as_markup()


def requisites_menu_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_add_card"), callback_data="req_add_card")
    builder.button(text=t(lang, "btn_add_ton"), callback_data="req_add_ton")
    builder.button(text=t(lang, "btn_view_reqs"), callback_data="req_view")
    builder.button(text=t(lang, "btn_back"), callback_data="go_main")
    builder.adjust(1)
    return builder.as_markup()


def back_to_requisites_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_back"), callback_data="requisites")
    return builder.as_markup()


def language_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🇷🇺 Русский", callback_data="set_lang_ru")
    builder.button(text="🇺🇸 English", callback_data="set_lang_en")
    builder.button(text="🔙 Обратно в меню", callback_data="go_main")
    builder.adjust(2)
    return builder.as_markup()


def back_to_main_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_back"), callback_data="go_main")
    return builder.as_markup()


def buyer_deal_kb(deal_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="💳 Я оплатил", callback_data=f"buyer_paid_{deal_id}")
    builder.adjust(1)
    return builder.as_markup()


def seller_confirm_payment_kb(deal_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Подарок передан боту", callback_data=f"seller_sent_{deal_id}")
    builder.button(text="❌ Оплата не поступила", callback_data=f"seller_not_paid_{deal_id}")
    builder.adjust(1)
    return builder.as_markup()


def buyer_confirm_receipt_kb(deal_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Подарок получен", callback_data=f"buyer_got_{deal_id}")
    builder.button(text="⚠️ Подарок не пришёл", callback_data=f"buyer_dispute_{deal_id}")
    builder.adjust(1)
    return builder.as_markup()
