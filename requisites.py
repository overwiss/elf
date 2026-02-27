from aiogram import Router, Bot, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import Database
from config import TEXTS
from keyboards.inline import requisites_menu_kb, back_to_requisites_kb
from utils import send_log, is_valid_card, is_valid_ton_wallet, fmt_username

router = Router()


class RequisiteStates(StatesGroup):
    waiting_card = State()
    waiting_ton = State()


@router.callback_query(F.data == "requisites")
async def requisites(callback: CallbackQuery, db: Database, state: FSMContext):
    tg_id = callback.from_user.id
    if await db.is_banned(tg_id):
        lang = await db.get_language(tg_id)
        await callback.answer(TEXTS[lang]["banned"], show_alert=True)
        return
    await state.clear()
    lang = await db.get_language(tg_id)
    try:
        await callback.message.edit_text(
            TEXTS[lang]["requisites_menu"],
            reply_markup=requisites_menu_kb(lang)
        )
    except Exception:
        await callback.message.answer(
            TEXTS[lang]["requisites_menu"],
            reply_markup=requisites_menu_kb(lang)
        )
    await callback.answer()


@router.callback_query(F.data == "req_add_card")
async def req_add_card(callback: CallbackQuery, db: Database, state: FSMContext):
    tg_id = callback.from_user.id
    lang = await db.get_language(tg_id)
    await state.set_state(RequisiteStates.waiting_card)
    try:
        await callback.message.edit_text(
            TEXTS[lang]["enter_card"],
            reply_markup=back_to_requisites_kb(lang)
        )
    except Exception:
        await callback.message.answer(
            TEXTS[lang]["enter_card"],
            reply_markup=back_to_requisites_kb(lang)
        )
    await callback.answer()


@router.callback_query(F.data == "req_add_ton")
async def req_add_ton(callback: CallbackQuery, db: Database, state: FSMContext):
    tg_id = callback.from_user.id
    lang = await db.get_language(tg_id)
    await state.set_state(RequisiteStates.waiting_ton)
    try:
        await callback.message.edit_text(
            TEXTS[lang]["enter_ton_wallet"],
            reply_markup=back_to_requisites_kb(lang)
        )
    except Exception:
        await callback.message.answer(
            TEXTS[lang]["enter_ton_wallet"],
            reply_markup=back_to_requisites_kb(lang)
        )
    await callback.answer()


@router.message(RequisiteStates.waiting_card)
async def process_card(message: Message, db: Database, state: FSMContext, bot: Bot):
    tg_id = message.from_user.id
    lang = await db.get_language(tg_id)
    card = (message.text or "").replace(" ", "")

    if not is_valid_card(card):
        await message.answer(
            TEXTS[lang]["req_invalid_card"],
            reply_markup=back_to_requisites_kb(lang)
        )
        return

    await db.add_requisite(tg_id, "card", card)
    await state.clear()
    await message.answer(
        TEXTS[lang]["req_saved"],
        reply_markup=requisites_menu_kb(lang)
    )

    username = message.from_user.username
    await send_log(
        bot,
        f"💳 <b>Добавлена карта</b>\n"
        f"👤 {fmt_username(username, tg_id)}\n"
        f"🆔 ID: <code>{tg_id}</code>\n"
        f"💳 Карта: <code>{card[:4]}****{card[-4:]}</code>",
        topic="requisites",
        db=db,
    )


@router.message(RequisiteStates.waiting_ton)
async def process_ton(message: Message, db: Database, state: FSMContext, bot: Bot):
    tg_id = message.from_user.id
    lang = await db.get_language(tg_id)
    wallet = (message.text or "").strip()

    if not is_valid_ton_wallet(wallet):
        await message.answer(
            TEXTS[lang]["req_invalid_ton"],
            reply_markup=back_to_requisites_kb(lang)
        )
        return

    await db.add_requisite(tg_id, "ton", wallet)
    await state.clear()
    await message.answer(
        TEXTS[lang]["req_saved"],
        reply_markup=requisites_menu_kb(lang)
    )

    username = message.from_user.username
    await send_log(
        bot,
        f"💎 <b>Добавлен TON кошелёк</b>\n"
        f"👤 {fmt_username(username, tg_id)}\n"
        f"🆔 ID: <code>{tg_id}</code>\n"
        f"💎 Кошелёк: <code>{wallet[:10]}...{wallet[-6:]}</code>",
        topic="requisites",
        db=db,
    )


@router.callback_query(F.data == "req_view")
async def req_view(callback: CallbackQuery, db: Database):
    tg_id = callback.from_user.id
    lang = await db.get_language(tg_id)
    reqs = await db.get_requisites(tg_id)

    if not reqs:
        try:
            await callback.message.edit_text(
                TEXTS[lang]["no_requisites"],
                reply_markup=back_to_requisites_kb(lang)
            )
        except Exception:
            await callback.message.answer(
                TEXTS[lang]["no_requisites"],
                reply_markup=back_to_requisites_kb(lang)
            )
        await callback.answer()
        return

    items = []
    for r in reqs:
        if r["type"] == "card":
            val = r["value"]
            items.append(f"💳 Карта: {val[:4]}****{val[-4:]}")
        elif r["type"] == "ton":
            val = r["value"]
            items.append(f"💎 TON: {val[:10]}...{val[-6:]}")

    text = TEXTS[lang]["your_requisites"].format(items="\n".join(items))
    try:
        await callback.message.edit_text(text, reply_markup=back_to_requisites_kb(lang))
    except Exception:
        await callback.message.answer(text, reply_markup=back_to_requisites_kb(lang))
    await callback.answer()
