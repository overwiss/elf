from aiogram import Router, Bot, F
from aiogram.types import CallbackQuery

from database import Database, generate_memo
from config import TEXTS
from keyboards.inline import (
    profile_kb, topup_info_kb, topup_choose_kb,
    topup_payment_kb, back_to_main_kb
)
from utils import send_log, fmt_username

router = Router()


@router.callback_query(F.data == "profile")
async def profile(callback: CallbackQuery, db: Database):
    tg_id = callback.from_user.id
    if await db.is_banned(tg_id):
        lang = await db.get_language(tg_id)
        await callback.answer(TEXTS[lang]["banned"], show_alert=True)
        return
    lang = await db.get_language(tg_id)
    user = await db.get_user(tg_id)

    verified = "✅ Пройдена" if user["is_verified"] else "❌ Не пройдена"
    username = user.get("username") or str(tg_id)

    text = TEXTS[lang]["profile_text"].format(
        username=username,
        balance_rub=round(user["balance_rub"], 2),
        balance_crypto=round(user["balance_crypto"], 2),
        total_deals=user["total_deals"],
        successful_deals=user["successful_deals"],
        turnover=round(user["turnover"], 2),
        verified=verified
    )

    try:
        await callback.message.edit_text(text, reply_markup=profile_kb(lang))
    except Exception:
        await callback.message.answer(text, reply_markup=profile_kb(lang))
    await callback.answer()


@router.callback_query(F.data == "topup_info")
async def topup_info(callback: CallbackQuery, db: Database):
    tg_id = callback.from_user.id
    lang = await db.get_language(tg_id)
    try:
        await callback.message.edit_text(
            TEXTS[lang]["topup_info"],
            reply_markup=topup_info_kb(lang)
        )
    except Exception:
        await callback.message.answer(
            TEXTS[lang]["topup_info"],
            reply_markup=topup_info_kb(lang)
        )
    await callback.answer()


@router.callback_query(F.data == "topup_choose")
async def topup_choose(callback: CallbackQuery, db: Database):
    tg_id = callback.from_user.id
    lang = await db.get_language(tg_id)
    try:
        await callback.message.edit_text(
            TEXTS[lang]["topup_choose"],
            reply_markup=topup_choose_kb(lang)
        )
    except Exception:
        await callback.message.answer(
            TEXTS[lang]["topup_choose"],
            reply_markup=topup_choose_kb(lang)
        )
    await callback.answer()


@router.callback_query(F.data == "topup_card")
async def topup_card(callback: CallbackQuery, db: Database, bot: Bot):
    tg_id = callback.from_user.id
    lang = await db.get_language(tg_id)

    card_number = await db.get_setting("card_number")
    card_name = await db.get_setting("card_name")
    card_bank = await db.get_setting("card_bank")
    memo = generate_memo()

    text = TEXTS[lang]["topup_card"].format(
        card_number=card_number,
        card_name=card_name,
        card_bank=card_bank,
        memo=memo
    )

    try:
        await callback.message.edit_text(
            text,
            reply_markup=topup_payment_kb(lang),
            parse_mode="HTML"
        )
    except Exception:
        await callback.message.answer(
            text,
            reply_markup=topup_payment_kb(lang),
            parse_mode="HTML"
        )

    username = callback.from_user.username
    await send_log(
        bot,
        f"💳 <b>Запрос пополнения (карта)</b>\n"
        f"👤 {fmt_username(username, tg_id)}\n"
        f"🆔 ID: <code>{tg_id}</code>\n"
        f"🔑 Мемо: <code>{memo}</code>",
        topic="topups",
        db=db,
    )
    await callback.answer()


@router.callback_query(F.data == "topup_ton")
async def topup_ton(callback: CallbackQuery, db: Database, bot: Bot):
    tg_id = callback.from_user.id
    lang = await db.get_language(tg_id)

    ton_wallet = await db.get_setting("ton_wallet")
    memo = generate_memo()

    text = TEXTS[lang]["topup_ton"].format(
        ton_wallet=ton_wallet,
        memo=memo
    )

    try:
        await callback.message.edit_text(
            text,
            reply_markup=topup_payment_kb(lang),
            parse_mode="HTML"
        )
    except Exception:
        await callback.message.answer(
            text,
            reply_markup=topup_payment_kb(lang),
            parse_mode="HTML"
        )

    username = callback.from_user.username
    await send_log(
        bot,
        f"💎 <b>Запрос пополнения (TON)</b>\n"
        f"👤 {fmt_username(username, tg_id)}\n"
        f"🆔 ID: <code>{tg_id}</code>\n"
        f"🔑 Мемо: <code>{memo}</code>",
        topic="topups",
        db=db,
    )
    await callback.answer()


@router.callback_query(F.data == "withdraw")
async def withdraw(callback: CallbackQuery, db: Database, bot: Bot):
    tg_id = callback.from_user.id
    lang = await db.get_language(tg_id)
    support = await db.get_setting("support_username")

    text = TEXTS[lang]["withdraw_text"].format(support=support)
    try:
        await callback.message.edit_text(text, reply_markup=back_to_main_kb(lang))
    except Exception:
        await callback.message.answer(text, reply_markup=back_to_main_kb(lang))

    username = callback.from_user.username
    await send_log(
        bot,
        f"💸 <b>Запрос вывода средств</b>\n"
        f"👤 {fmt_username(username, tg_id)}\n"
        f"🆔 ID: <code>{tg_id}</code>",
        topic="withdrawals",
        db=db,
    )
    await callback.answer()
