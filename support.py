from aiogram import Router, F
from aiogram.types import CallbackQuery

from database import Database
from config import TEXTS
from keyboards.inline import back_to_main_kb

router = Router()


@router.callback_query(F.data == "support")
async def support_handler(callback: CallbackQuery, db: Database):
    tg_id = callback.from_user.id
    lang = await db.get_language(tg_id)
    support_username = await db.get_setting("support_username")

    text = TEXTS[lang]["support_text"].format(support=support_username)
    try:
        await callback.message.edit_text(text, reply_markup=back_to_main_kb(lang))
    except Exception:
        await callback.message.answer(text, reply_markup=back_to_main_kb(lang))
    await callback.answer()
