from aiogram import Router, Bot, F
from aiogram.types import CallbackQuery

from database import Database
from config import TEXTS
from keyboards.inline import language_kb, back_to_main_kb
from utils import send_log, fmt_username

router = Router()


@router.callback_query(F.data == "language")
async def language_menu(callback: CallbackQuery, db: Database):
    tg_id = callback.from_user.id
    if await db.is_banned(tg_id):
        lang = await db.get_language(tg_id)
        await callback.answer(TEXTS[lang]["banned"], show_alert=True)
        return
    lang = await db.get_language(tg_id)
    try:
        await callback.message.edit_text(
            TEXTS[lang]["language_menu"],
            reply_markup=language_kb()
        )
    except Exception:
        await callback.message.answer(
            TEXTS[lang]["language_menu"],
            reply_markup=language_kb()
        )
    await callback.answer()


@router.callback_query(F.data.startswith("set_lang_"))
async def set_language(callback: CallbackQuery, db: Database, bot: Bot):
    tg_id = callback.from_user.id
    new_lang = callback.data[9:]
    if new_lang not in ("ru", "en"):
        await callback.answer("❌ Неизвестный язык.", show_alert=True)
        return

    await db.set_language(tg_id, new_lang)

    try:
        await callback.message.edit_text(
            TEXTS[new_lang]["language_set"],
            reply_markup=back_to_main_kb(new_lang)
        )
    except Exception:
        await callback.message.answer(
            TEXTS[new_lang]["language_set"],
            reply_markup=back_to_main_kb(new_lang)
        )

    lang_name = "Русский 🇷🇺" if new_lang == "ru" else "English 🇺🇸"
    username = callback.from_user.username
    await send_log(
        bot,
        f"🌍 <b>Смена языка</b>\n"
        f"👤 {fmt_username(username, tg_id)}\n"
        f"🆔 ID: <code>{tg_id}</code>\n"
        f"🌍 Язык: {lang_name}",
        topic="general",
        db=db,
    )
    await callback.answer()
