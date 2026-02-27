import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
import uuid
import logging
import os

# ---------- Настройка логгера ----------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ---------- Конфигурация ----------
BOT_TOKEN = "8646127356:AAEENwQwJyu5Ynbs9SlHvVvdu5sLtPYUXw4"  # замените на свой токен
ADMIN_ID = 8418705574
VALUTE = "TON"  # валюта по умолчанию

# ---------- Словарь сообщений (встроенный, чтобы не зависеть от messages.py) ----------
MESSAGES = {
    'ru': {
        'start_message': 'Добро пожаловать в OTC бот!',
        'admin_panel_message': 'Панель администратора\n\nВыберите действие:',
        'add_wallet_button': '➕ Добавить кошелек',
        'create_deal_button': '📝 Создать сделку',
        'referral_button': '👥 Реферальная ссылка',
        'change_lang_button': '🌐 Сменить язык',
        'support_button': '🆘 Поддержка',
        'menu_button': '🔙 В меню',
        'pay_from_balance_button': '💳 Оплатить с баланса',
        'wallet_message': 'Ваш кошелек: {wallet}',
        'create_deal_message': 'Введите сумму сделки в {valute} (только число):',
        'referral_message': 'Ваша реферальная ссылка: {referral_link}\n\nЗа каждого приглашённого вы получите бонус!',
        'change_lang_message': 'Выберите язык:',
        'english_lang_button': '🇬🇧 English',
        'russian_lang_button': '🇷🇺 Русский',
        'lang_set_message': 'Язык успешно изменён!',
        'awaiting_description_message': 'Введите описание товара/услуги:',
        'deal_created_message': '✅ Сделка создана!\nСумма: {amount} {valute}\nОписание: {description}\nСсылка для покупателя: {deal_link}',
        'wallet_updated_message': '✅ Кошелёк обновлён: {wallet}',
        'insufficient_balance_message': '❌ Недостаточно средств на балансе.',
        'payment_confirmed_message': '✅ Оплата по сделке {deal_id} подтверждена!\nСумма: {amount} {valute}\nОписание: {description}',
        'payment_confirmed_seller_message': '✅ Покупатель @{buyer_username} оплатил сделку {deal_id}.\nОписание: {description}',
        'deal_info_message': 'Сделка {deal_id}\nПродавец: @{seller_username} (успешных сделок: {successful_deals})\nОписание: {description}\nКошелёк продавца: {wallet}\nСумма: {amount} {valute}',
        'seller_notification_message': 'Покупатель @{buyer_username} перешёл по ссылке на сделку {deal_id}. Ожидайте оплаты.',
        'admin_view_deals_button': '📋 Просмотр сделок',
        'admin_change_balance_button': '💰 Изменить баланс',
        'admin_change_successful_deals_button': '📊 Изменить успешные сделки',
        'admin_change_valute_button': '💱 Изменить валюту',
        'admin_view_deals_message': 'Активные сделки:\n{deals_list}',
        'admin_change_balance_message': 'Введите ID пользователя и новый баланс через пробел:',
        'admin_change_successful_deals_message': 'Введите ID пользователя и новое количество успешных сделок через пробел:',
        'admin_change_valute_message': 'Введите новое название валюты:',
        # Новые сообщения для админ-панели
        'admin_ban_button': '🚫 Забанить пользователя',
        'admin_unban_button': '✅ Разбанить пользователя',
        'admin_send_money_button': '💸 Отправить деньги',
        'admin_set_successful_deals_button': '📈 Установить успешные сделки',
        'admin_set_deals_count_button': '🔢 Установить кол-во сделок',
        'admin_set_turnover_button': '💰 Установить оборот',
        'admin_settings_button': '⚙️ Настройки бота',
        'admin_complete_deal_button': '🏁 Завершить сделку',
        'admin_all_users_button': '👥 Все пользователи',
        'admin_mailing_button': '📨 Рассылка',
        'admin_back_button': '🔙 Назад',
        'admin_enter_user_id': 'Введите ID пользователя:',
        'admin_enter_amount': 'Введите сумму:',
        'admin_enter_new_value': 'Введите новое значение:',
        'admin_user_not_found': 'Пользователь с ID {user_id} не найден.',
        'admin_action_done': '✅ Готово.',
        'admin_enter_deal_id': 'Введите ID сделки:',
        'admin_deal_not_found': 'Сделка с ID {deal_id} не найдена.',
        'admin_deal_completed': 'Сделка {deal_id} завершена администратором.',
        'admin_deal_completed_notify_seller': 'Ваша сделка {deal_id} была завершена администратором.',
        'admin_deal_completed_notify_buyer': 'Сделка {deal_id}, в которой вы участвовали, завершена администратором.',
        'admin_all_users_header': 'Список пользователей (страница {page}):\n',
        'admin_user_line': 'ID: {user_id} | Баланс: {balance} {valute} | Усп.сделок: {successful_deals} | Оборот: {turnover} | Язык: {lang} | Кошелёк: {wallet}\n',
        'admin_next_page': '▶️ След.',
        'admin_prev_page': '◀️ Пред.',
        'admin_mailing_prompt': 'Отправьте текст для рассылки (можно с фото).',
        'admin_mailing_started': 'Рассылка началась...',
        'admin_mailing_completed': 'Рассылка завершена. Отправлено {sent} пользователям.',
        'admin_settings_title': 'Настройки бота\nВыберите параметр для изменения:',
        'admin_settings_support': '🆘 Поддержка (юз)',
        'admin_settings_site': '🌐 Сайт',
        'admin_settings_channel': '📢 Канал',
        'admin_settings_card_number': '💳 Номер карты',
        'admin_settings_card_name': '👤 Имя на карте',
        'admin_settings_card_bank': '🏦 Банк карты',
        'admin_settings_ton_wallet': '💎 TON кошелёк',
        'admin_settings_terms': '📜 Ссылка на условия',
        'admin_settings_photo': '🖼 Фото (file_id)',
        'admin_settings_gift_account': '🎁 Аккаунт для подарков',
        'admin_settings_log_topics': '🗂 Топики логов',
        'admin_setting_updated': 'Параметр {key} обновлён на {value}.',
        'admin_enter_new_value_for': 'Введите новое значение для {key}:',
        'bot_blocked': 'Бот заблокирован пользователем {user_id}',
        'user_banned': 'Вы забанены. Доступ запрещён.',
    },
    'en': {
        # Аналогично для английского (можно заполнить позже)
        'start_message': 'Welcome to OTC bot!',
        # ... остальные ключи
    }
}

def get_text(lang, key, **kwargs):
    """Возвращает локализованный текст с подстановкой переменных."""
    text = MESSAGES.get(lang, MESSAGES['ru']).get(key, key)
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError:
            pass
    return text

# ---------- База данных ----------
DB_NAME = 'bot_data.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Таблица пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            wallet TEXT,
            balance REAL DEFAULT 0,
            successful_deals INTEGER DEFAULT 0,
            turnover REAL DEFAULT 0,
            lang TEXT DEFAULT 'ru'
        )
    ''')
    # Проверяем наличие колонки turnover
    cursor.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'turnover' not in columns:
        cursor.execute('ALTER TABLE users ADD COLUMN turnover REAL DEFAULT 0')

    # Таблица сделок
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS deals (
            deal_id TEXT PRIMARY KEY,
            amount REAL,
            description TEXT,
            seller_id INTEGER,
            buyer_id INTEGER
        )
    ''')
    # Таблица забаненных
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS banned_users (
            user_id INTEGER PRIMARY KEY
        )
    ''')
    # Таблица настроек
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    conn.commit()
    conn.close()

def load_data():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Загрузка пользователей
    cursor.execute('SELECT user_id, wallet, balance, successful_deals, turnover, lang FROM users')
    for row in cursor.fetchall():
        user_id, wallet, balance, successful_deals, turnover, lang = row
        user_data[user_id] = {
            'wallet': wallet or '',
            'balance': balance,
            'successful_deals': successful_deals,
            'turnover': turnover,
            'lang': lang or 'ru'
        }
    # Загрузка сделок
    cursor.execute('SELECT deal_id, amount, description, seller_id, buyer_id FROM deals')
    for row in cursor.fetchall():
        deal_id, amount, description, seller_id, buyer_id = row
        deals[deal_id] = {
            'amount': amount,
            'description': description,
            'seller_id': seller_id,
            'buyer_id': buyer_id
        }
    # Загрузка настроек
    cursor.execute('SELECT key, value FROM settings')
    for key, value in cursor.fetchall():
        settings[key] = value
    conn.close()

def save_user_data(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    user = user_data.get(user_id, {})
    cursor.execute('''
        INSERT OR REPLACE INTO users (user_id, wallet, balance, successful_deals, turnover, lang)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, user.get('wallet', ''), user.get('balance', 0.0),
          user.get('successful_deals', 0), user.get('turnover', 0.0), user.get('lang', 'ru')))
    conn.commit()
    conn.close()

def save_deal(deal_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    deal = deals.get(deal_id, {})
    cursor.execute('''
        INSERT OR REPLACE INTO deals (deal_id, amount, description, seller_id, buyer_id)
        VALUES (?, ?, ?, ?, ?)
    ''', (deal_id, deal.get('amount', 0.0), deal.get('description', ''),
          deal.get('seller_id'), deal.get('buyer_id')))
    conn.commit()
    conn.close()

def delete_deal(deal_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM deals WHERE deal_id = ?', (deal_id,))
    conn.commit()
    conn.close()
    if deal_id in deals:
        del deals[deal_id]

def save_setting(key, value):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', (key, str(value)))
    conn.commit()
    conn.close()
    settings[key] = value

def is_banned(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM banned_users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone() is not None
    conn.close()
    return result

def ban_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO banned_users (user_id) VALUES (?)', (user_id,))
    conn.commit()
    conn.close()

def unban_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM banned_users WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM users')
    users = [row[0] for row in cursor.fetchall()]
    conn.close()
    return users

# ---------- Глобальные переменные ----------
user_data = {}
deals = {}
admin_commands = {}   # {user_id: 'command'}
settings = {}         # настройки бота
# Значения по умолчанию для настроек
DEFAULT_SETTINGS = {
    'support_username': '',
    'site_url': '',
    'channel_url': '',
    'card_number': '',
    'card_name': '',
    'card_bank': '',
    'ton_wallet': '',
    'terms_link': '',
    'photo_file_id': '',
    'gift_account': '',
    'log_topic_users': '',
    'log_topic_deals': '',
    'log_topic_deposits': '',
    'log_topic_withdrawals': '',
    'log_topic_requisites': '',
    'log_topic_admin': '',
    'log_topic_general': '',
}

# ---------- Вспомогательные функции ----------
def ensure_user_exists(user_id):
    if user_id not in user_data:
        user_data[user_id] = {
            'wallet': '',
            'balance': 0.0,
            'successful_deals': 0,
            'turnover': 0.0,
            'lang': 'ru'
        }
        save_user_data(user_id)

async def log_event(event_type: str, text: str, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет лог в соответствующий топик (если указан) или в общий чат."""
    topic_key = f'log_topic_{event_type}'
    topic_id = settings.get(topic_key)
    chat_id = ADMIN_ID  # логи отправляются админу
    if topic_id and topic_id.isdigit():
        await context.bot.send_message(chat_id=int(chat_id), text=text, message_thread_id=int(topic_id))
    else:
        await context.bot.send_message(chat_id=int(chat_id), text=text)

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, chat_id: int):
    """Показывает главное меню для пользователя или админа."""
    lang = user_data.get(user_id, {}).get('lang', 'ru')
    if user_id == ADMIN_ID:
        keyboard = [
            [InlineKeyboardButton(get_text(lang, "admin_view_deals_button"), callback_data='admin_view_deals')],
            [InlineKeyboardButton(get_text(lang, "admin_change_balance_button"), callback_data='admin_change_balance')],
            [InlineKeyboardButton(get_text(lang, "admin_change_successful_deals_button"), callback_data='admin_change_successful_deals')],
            [InlineKeyboardButton(get_text(lang, "admin_change_valute_button"), callback_data='admin_change_valute')],
            [InlineKeyboardButton(get_text(lang, "admin_ban_button"), callback_data='admin_ban')],
            [InlineKeyboardButton(get_text(lang, "admin_unban_button"), callback_data='admin_unban')],
            [InlineKeyboardButton(get_text(lang, "admin_send_money_button"), callback_data='admin_send_money')],
            [InlineKeyboardButton(get_text(lang, "admin_set_turnover_button"), callback_data='admin_set_turnover')],
            [InlineKeyboardButton(get_text(lang, "admin_settings_button"), callback_data='admin_settings')],
            [InlineKeyboardButton(get_text(lang, "admin_complete_deal_button"), callback_data='admin_complete_deal')],
            [InlineKeyboardButton(get_text(lang, "admin_all_users_button"), callback_data='admin_all_users')],
            [InlineKeyboardButton(get_text(lang, "admin_mailing_button"), callback_data='admin_mailing')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(chat_id, get_text(lang, "admin_panel_message"), reply_markup=reply_markup)
    else:
        keyboard = [
            [InlineKeyboardButton(get_text(lang, "add_wallet_button"), callback_data='wallet')],
            [InlineKeyboardButton(get_text(lang, "create_deal_button"), callback_data='create_deal')],
            [InlineKeyboardButton(get_text(lang, "referral_button"), callback_data='referral')],
            [InlineKeyboardButton(get_text(lang, "change_lang_button"), callback_data='change_lang')],
            [InlineKeyboardButton(get_text(lang, "support_button"), url='https://t.me/otcgifttg/113382/113404')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_photo(
            chat_id,
            photo="https://postimg.cc/8sHq27HV",
            caption=get_text(lang, "start_message"),
            reply_markup=reply_markup
        )

# ---------- Обработчики ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.message:
            user_id = update.message.from_user.id
            chat_id = update.message.chat_id
            args = context.args
        elif update.callback_query:
            user_id = update.callback_query.from_user.id
            chat_id = update.callback_query.message.chat_id
            args = []
        else:
            return

        # Проверка бана
        if is_banned(user_id):
            await context.bot.send_message(chat_id, get_text('ru', 'user_banned'))
            return

        lang = user_data.get(user_id, {}).get('lang', 'ru')

        # Если передан deal_id
        if args and args[0] in deals:
            deal_id = args[0]
            deal = deals[deal_id]
            seller_id = deal['seller_id']
            try:
                seller_username = (await context.bot.get_chat(seller_id)).username or str(seller_id)
            except:
                seller_username = str(seller_id)

            # Добавляем покупателя
            deals[deal_id]['buyer_id'] = user_id
            save_deal(deal_id)

            await context.bot.send_message(
                chat_id,
                get_text(lang, "deal_info_message",
                         deal_id=deal_id,
                         seller_username=seller_username,
                         successful_deals=user_data.get(seller_id, {}).get('successful_deals', 0),
                         description=deal['description'],
                         wallet=user_data.get(seller_id, {}).get('wallet', 'Не указан'),
                         amount=deal['amount'],
                         valute=VALUTE),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(get_text(lang, "pay_from_balance_button"), callback_data=f'pay_from_balance_{deal_id}')],
                    [InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]
                ])
            )

            try:
                buyer_username = (await context.bot.get_chat(user_id)).username or str(user_id)
            except:
                buyer_username = str(user_id)
            await context.bot.send_message(
                seller_id,
                get_text(lang, "seller_notification_message",
                         buyer_username=buyer_username,
                         deal_id=deal_id,
                         successful_deals=user_data.get(seller_id, {}).get('successful_deals', 0))
            )
            return

        # Показываем меню
        await show_main_menu(update, context, user_id, chat_id)

    except Exception as e:
        logger.error(f"Ошибка в start: {e}")
        await context.bot.send_message(chat_id, "Произошла ошибка. Попробуйте позже.")

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /admin"""
    user_id = update.message.from_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("У вас нет прав администратора.")
        return
    await show_main_menu(update, context, user_id, update.message.chat_id)

async def fastbuy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Фейк-оплата сделки: /fastbuy <deal_id>"""
    user_id = update.message.from_user.id
    if user_id != ADMIN_ID:
        return
    args = context.args
    if not args:
        await update.message.reply_text("Укажите ID сделки: /fastbuy <deal_id>")
        return
    deal_id = args[0]
    if deal_id not in deals:
        await update.message.reply_text("Сделка не найдена.")
        return
    deal = deals[deal_id]
    seller_id = deal['seller_id']
    ensure_user_exists(seller_id)
    # Увеличиваем успешные сделки и оборот продавца
    user_data[seller_id]['successful_deals'] += 1
    user_data[seller_id]['turnover'] += deal['amount']
    save_user_data(seller_id)
    # Уведомляем продавца
    try:
        await context.bot.send_message(seller_id, f"✅ Ваша сделка {deal_id} помечена как выполненная (фейк-оплата).")
    except:
        pass
    # Удаляем сделку
    delete_deal(deal_id)
    await update.message.reply_text(f"Сделка {deal_id} завершена (фейк).")
    await log_event('admin', f"Админ выполнил фейк-оплату сделки {deal_id}", context)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()
        data = query.data
        user_id = query.from_user.id
        chat_id = query.message.chat_id
        lang = user_data.get(user_id, {}).get('lang', 'ru')

        # Проверка бана (кроме самого админа)
        if user_id != ADMIN_ID and is_banned(user_id):
            await query.edit_message_text(get_text(lang, 'user_banned'))
            return

        # ---------- Смена языка ----------
        if data.startswith('lang_'):
            new_lang = data.split('_')[1]
            ensure_user_exists(user_id)
            user_data[user_id]['lang'] = new_lang
            save_user_data(user_id)
            await query.edit_message_text(get_text(new_lang, "lang_set_message"))
            await show_main_menu(update, context, user_id, chat_id)
            return

        # ---------- Главное меню ----------
        if data == 'menu':
            await show_main_menu(update, context, user_id, chat_id)
            return

        # ---------- Кошелёк ----------
        if data == 'wallet':
            wallet = user_data.get(user_id, {}).get('wallet', '')
            if wallet:
                text = get_text(lang, "wallet_message", wallet=wallet)
            else:
                text = get_text(lang, "wallet_message", wallet="Не указан")
            await context.bot.send_message(
                chat_id, text,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
            )
            context.user_data['awaiting_wallet'] = True
            return

        # ---------- Создание сделки ----------
        if data == 'create_deal':
            await context.bot.send_photo(
                chat_id,
                photo="https://postimg.cc/8sHq27HV",
                caption=get_text(lang, "create_deal_message", valute=VALUTE),
                parse_mode="MarkdownV2",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
            )
            context.user_data['awaiting_amount'] = True
            return

        # ---------- Реферальная ссылка ----------
        if data == 'referral':
            referral_link = f"https://t.me/ElfDealRobot?start={user_id}"
            await context.bot.send_message(
                chat_id,
                get_text(lang, "referral_message", referral_link=referral_link, valute=VALUTE),
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
            )
            return

        # ---------- Смена языка (кнопка) ----------
        if data == 'change_lang':
            await context.bot.send_message(
                chat_id,
                get_text(lang, "change_lang_message"),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(get_text(lang, "english_lang_button"), callback_data='lang_en')],
                    [InlineKeyboardButton(get_text(lang, "russian_lang_button"), callback_data='lang_ru')]
                ])
            )
            return

        # ---------- Админские кнопки ----------
        if user_id != ADMIN_ID:
            return

        # Просмотр сделок
        if data == 'admin_view_deals':
            if not deals:
                await context.bot.send_message(chat_id, "Нет активных сделок.")
            else:
                deals_list = "\n".join([f"Сделка {deal_id}: {deal['amount']} {VALUTE}, Продавец: {deal['seller_id']}" for deal_id, deal in deals.items()])
                await context.bot.send_message(chat_id, get_text(lang, "admin_view_deals_message", deals_list=deals_list))
            return

        # Изменить баланс
        if data == 'admin_change_balance':
            await query.edit_message_text(get_text(lang, "admin_change_balance_message"))
            admin_commands[user_id] = 'change_balance'
            return

        # Изменить успешные сделки
        if data == 'admin_change_successful_deals':
            await query.edit_message_text(get_text(lang, "admin_change_successful_deals_message"))
            admin_commands[user_id] = 'change_successful_deals'
            return

        # Изменить валюту
        if data == 'admin_change_valute':
            await query.edit_message_text(get_text(lang, "admin_change_valute_message"))
            admin_commands[user_id] = 'change_valute'
            return

        # Забанить
        if data == 'admin_ban':
            await query.edit_message_text("Введите ID пользователя для бана:")
            admin_commands[user_id] = 'ban'
            return

        # Разбанить
        if data == 'admin_unban':
            await query.edit_message_text("Введите ID пользователя для разбана:")
            admin_commands[user_id] = 'unban'
            return

        # Отправить деньги
        if data == 'admin_send_money':
            await query.edit_message_text("Введите ID пользователя и сумму через пробел:")
            admin_commands[user_id] = 'send_money'
            return

        # Установить оборот
        if data == 'admin_set_turnover':
            await query.edit_message_text("Введите ID пользователя и новый оборот через пробел:")
            admin_commands[user_id] = 'set_turnover'
            return

        # Настройки бота
        if data == 'admin_settings':
            keyboard = [
                [InlineKeyboardButton(get_text(lang, "admin_settings_support"), callback_data='set_support')],
                [InlineKeyboardButton(get_text(lang, "admin_settings_site"), callback_data='set_site')],
                [InlineKeyboardButton(get_text(lang, "admin_settings_channel"), callback_data='set_channel')],
                [InlineKeyboardButton(get_text(lang, "admin_settings_card_number"), callback_data='set_card_number')],
                [InlineKeyboardButton(get_text(lang, "admin_settings_card_name"), callback_data='set_card_name')],
                [InlineKeyboardButton(get_text(lang, "admin_settings_card_bank"), callback_data='set_card_bank')],
                [InlineKeyboardButton(get_text(lang, "admin_settings_ton_wallet"), callback_data='set_ton_wallet')],
                [InlineKeyboardButton(get_text(lang, "admin_settings_terms"), callback_data='set_terms')],
                [InlineKeyboardButton(get_text(lang, "admin_settings_photo"), callback_data='set_photo')],
                [InlineKeyboardButton(get_text(lang, "admin_settings_gift_account"), callback_data='set_gift')],
                [InlineKeyboardButton(get_text(lang, "admin_settings_log_topics"), callback_data='set_log_topics')],
                [InlineKeyboardButton(get_text(lang, "admin_back_button"), callback_data='menu')],
            ]
            await query.edit_message_text(
                get_text(lang, "admin_settings_title"),
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return

        # Завершить сделку
        if data == 'admin_complete_deal':
            await query.edit_message_text("Введите ID сделки:")
            admin_commands[user_id] = 'complete_deal'
            return

        # Все пользователи (с пагинацией)
        if data == 'admin_all_users':
            page = 1
            await show_users_page(update, context, page)
            return

        if data.startswith('users_page_'):
            page = int(data.split('_')[2])
            await show_users_page(update, context, page)
            return

        # Рассылка
        if data == 'admin_mailing':
            await query.edit_message_text(get_text(lang, "admin_mailing_prompt"))
            admin_commands[user_id] = 'mailing'
            return

        # Обработка настроек (подменю)
        if data.startswith('set_'):
            key_map = {
                'set_support': 'support_username',
                'set_site': 'site_url',
                'set_channel': 'channel_url',
                'set_card_number': 'card_number',
                'set_card_name': 'card_name',
                'set_card_bank': 'card_bank',
                'set_ton_wallet': 'ton_wallet',
                'set_terms': 'terms_link',
                'set_photo': 'photo_file_id',
                'set_gift': 'gift_account',
                'set_log_topics': 'log_topics'
            }
            key = key_map.get(data)
            if key:
                admin_commands[user_id] = f'set_{key}'
                await query.edit_message_text(get_text(lang, "admin_enter_new_value_for", key=key))
            return

        # Оплата с баланса
        if data.startswith('pay_from_balance_'):
            deal_id = data.split('_')[-1]
            deal = deals.get(deal_id)
            if not deal:
                await context.bot.send_message(chat_id, "Сделка не найдена.")
                return
            buyer_id = user_id
            seller_id = deal['seller_id']
            amount = deal['amount']

            ensure_user_exists(buyer_id)
            ensure_user_exists(seller_id)

            if user_data[buyer_id]['balance'] >= amount:
                # Списание
                user_data[buyer_id]['balance'] -= amount
                save_user_data(buyer_id)
                # Зачисление
                user_data[seller_id]['balance'] += amount
                user_data[seller_id]['turnover'] += amount
                save_user_data(seller_id)

                await context.bot.send_message(
                    chat_id,
                    get_text(lang, "payment_confirmed_message",
                             deal_id=deal_id, amount=amount, valute=VALUTE, description=deal['description']),
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
                )
                # Уведомление продавцу
                try:
                    buyer_username = (await context.bot.get_chat(buyer_id)).username or str(buyer_id)
                except:
                    buyer_username = str(buyer_id)
                await context.bot.send_message(
                    seller_id,
                    get_text(lang, "payment_confirmed_seller_message",
                             deal_id=deal_id, description=deal['description'], buyer_username=buyer_username)
                )
                # Увеличиваем успешные сделки
                user_data[seller_id]['successful_deals'] += 1
                save_user_data(seller_id)
                # Удаляем сделку
                delete_deal(deal_id)
            else:
                await context.bot.send_message(
                    chat_id,
                    get_text(lang, "insufficient_balance_message"),
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
                )
            return

    except Exception as e:
        logger.error(f"Ошибка в button: {e}")
        await context.bot.send_message(chat_id, "Произошла ошибка.")

async def show_users_page(update: Update, context: ContextTypes.DEFAULT_TYPE, page: int):
    """Показывает список пользователей с пагинацией (по 10 на странице)."""
    query = update.callback_query
    user_id = query.from_user.id
    lang = user_data.get(user_id, {}).get('lang', 'ru')
    all_users = list(user_data.keys())
    per_page = 10
    total_pages = (len(all_users) + per_page - 1) // per_page
    page = max(1, min(page, total_pages))
    start = (page - 1) * per_page
    end = start + per_page
    users_on_page = all_users[start:end]

    text = get_text(lang, "admin_all_users_header", page=page)
    for uid in users_on_page:
        u = user_data[uid]
        text += get_text(lang, "admin_user_line",
                         user_id=uid,
                         balance=u.get('balance', 0),
                         valute=VALUTE,
                         successful_deals=u.get('successful_deals', 0),
                         turnover=u.get('turnover', 0),
                         lang=u.get('lang', 'ru'),
                         wallet=u.get('wallet', '-'))

    keyboard = []
    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton(get_text(lang, "admin_prev_page"), callback_data=f'users_page_{page-1}'))
    if page < total_pages:
        nav_buttons.append(InlineKeyboardButton(get_text(lang, "admin_next_page"), callback_data=f'users_page_{page+1}'))
    if nav_buttons:
        keyboard.append(nav_buttons)
    keyboard.append([InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')])

    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        global VALUTE
        user_id = update.message.from_user.id
        text = update.message.text
        lang = user_data.get(user_id, {}).get('lang', 'ru')

        # Проверка бана
        if user_id != ADMIN_ID and is_banned(user_id):
            await update.message.reply_text(get_text(lang, 'user_banned'))
            return

        # ---------- Админские команды (ожидание ввода) ----------
        if user_id == ADMIN_ID and user_id in admin_commands:
            cmd = admin_commands[user_id]
            admin_commands[user_id] = None  # сброс после обработки

            # Изменение баланса
            if cmd == 'change_balance':
                try:
                    target_id, new_balance = text.split()
                    target_id = int(target_id)
                    new_balance = float(new_balance)
                    ensure_user_exists(target_id)
                    user_data[target_id]['balance'] = new_balance
                    save_user_data(target_id)
                    await update.message.reply_text(f"Баланс пользователя {target_id} изменён на {new_balance} {VALUTE}.")
                except:
                    await update.message.reply_text("Неверный формат. Введите ID и сумму через пробел.")
                return

            # Изменение успешных сделок
            if cmd == 'change_successful_deals':
                try:
                    target_id, new_val = text.split()
                    target_id = int(target_id)
                    new_val = int(new_val)
                    ensure_user_exists(target_id)
                    user_data[target_id]['successful_deals'] = new_val
                    save_user_data(target_id)
                    await update.message.reply_text(f"Успешные сделки пользователя {target_id} изменены на {new_val}.")
                except:
                    await update.message.reply_text("Неверный формат. Введите ID и количество через пробел.")
                return

            # Изменение валюты
            if cmd == 'change_valute':
                VALUTE = text.strip().upper()
                await update.message.reply_text(f"Валюта изменена на {VALUTE}.")
                return

            # Бан
            if cmd == 'ban':
                try:
                    target_id = int(text.strip())
                    ban_user(target_id)
                    await update.message.reply_text(f"Пользователь {target_id} забанен.")
                except:
                    await update.message.reply_text("Введите корректный ID.")
                return

            # Разбан
            if cmd == 'unban':
                try:
                    target_id = int(text.strip())
                    unban_user(target_id)
                    await update.message.reply_text(f"Пользователь {target_id} разбанен.")
                except:
                    await update.message.reply_text("Введите корректный ID.")
                return

            # Отправить деньги
            if cmd == 'send_money':
                try:
                    target_id, amount = text.split()
                    target_id = int(target_id)
                    amount = float(amount)
                    ensure_user_exists(target_id)
                    user_data[target_id]['balance'] += amount
                    save_user_data(target_id)
                    await update.message.reply_text(f"Пользователю {target_id} зачислено {amount} {VALUTE}.")
                except:
                    await update.message.reply_text("Неверный формат. Введите ID и сумму через пробел.")
                return

            # Установить оборот
            if cmd == 'set_turnover':
                try:
                    target_id, turnover = text.split()
                    target_id = int(target_id)
                    turnover = float(turnover)
                    ensure_user_exists(target_id)
                    user_data[target_id]['turnover'] = turnover
                    save_user_data(target_id)
                    await update.message.reply_text(f"Оборот пользователя {target_id} установлен на {turnover}.")
                except:
                    await update.message.reply_text("Неверный формат. Введите ID и оборот через пробел.")
                return

            # Завершить сделку
            if cmd == 'complete_deal':
                deal_id = text.strip()
                if deal_id in deals:
                    deal = deals[deal_id]
                    seller_id = deal['seller_id']
                    buyer_id = deal.get('buyer_id')
                    # Уведомления
                    try:
                        await context.bot.send_message(seller_id, get_text(lang, "admin_deal_completed_notify_seller", deal_id=deal_id))
                    except:
                        pass
                    if buyer_id:
                        try:
                            await context.bot.send_message(buyer_id, get_text(lang, "admin_deal_completed_notify_buyer", deal_id=deal_id))
                        except:
                            pass
                    delete_deal(deal_id)
                    await update.message.reply_text(get_text(lang, "admin_deal_completed", deal_id=deal_id))
                else:
                    await update.message.reply_text(get_text(lang, "admin_deal_not_found", deal_id=deal_id))
                return

            # Рассылка
            if cmd == 'mailing':
                # Сохраняем текст рассылки и начинаем отправку
                mailing_text = text
                # Если есть фото, можно обработать (упрощённо)
                photo = None
                if update.message.photo:
                    photo = update.message.photo[-1].file_id
                sent = 0
                all_users = get_all_users()
                for uid in all_users:
                    if uid == ADMIN_ID or is_banned(uid):
                        continue
                    try:
                        if photo:
                            await context.bot.send_photo(uid, photo=photo, caption=mailing_text)
                        else:
                            await context.bot.send_message(uid, mailing_text)
                        sent += 1
                    except Exception as e:
                        logger.warning(f"Не удалось отправить рассылку пользователю {uid}: {e}")
                await update.message.reply_text(get_text(lang, "admin_mailing_completed", sent=sent))
                return

            # Настройки (set_...)
            if cmd.startswith('set_'):
                key = cmd[4:]  # убираем 'set_'
                new_value = text.strip()
                save_setting(key, new_value)
                await update.message.reply_text(get_text(lang, "admin_setting_updated", key=key, value=new_value))
                return

        # ---------- Обычные пользовательские сообщения ----------
        # Ожидание суммы сделки
        if context.user_data.get('awaiting_amount', False):
            try:
                context.user_data['amount'] = float(text)
                context.user_data['awaiting_amount'] = False
                context.user_data['awaiting_description'] = True
                await update.message.reply_text(
                    get_text(lang, "awaiting_description_message"),
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
                )
            except ValueError:
                await update.message.reply_text("Неверный формат. Введите число.")
            return

        # Ожидание описания сделки
        if context.user_data.get('awaiting_description', False):
            deal_id = str(uuid.uuid4())
            deals[deal_id] = {
                'amount': context.user_data['amount'],
                'description': text,
                'seller_id': user_id,
                'buyer_id': None
            }
            save_deal(deal_id)
            context.user_data.clear()

            await update.message.reply_text(
                get_text(lang, "deal_created_message",
                         amount=deals[deal_id]['amount'],
                         valute=VALUTE,
                         description=deals[deal_id]['description'],
                         deal_link=f"https://t.me/ElfDealRobot?start={deal_id}"),
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
            )
            # Лог админу
            await log_event('deals',
                f"Новая сделка:\nID: {deal_id}\nСумма: {deals[deal_id]['amount']} {VALUTE}\nПродавец: {user_id}",
                context)
            return

        # Ожидание кошелька
        if context.user_data.get('awaiting_wallet', False):
            ensure_user_exists(user_id)
            user_data[user_id]['wallet'] = text
            save_user_data(user_id)
            context.user_data.pop('awaiting_wallet', None)
            await update.message.reply_text(
                get_text(lang, "wallet_updated_message", wallet=text),
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(lang, "menu_button"), callback_data='menu')]])
            )
            return

        # Если ничего не ожидаем – игнорируем
    except Exception as e:
        logger.error(f"Ошибка в handle_message: {e}")
        await update.message.reply_text("Произошла ошибка. Попробуйте позже.")

# ---------- Запуск бота ----------
def main():
    init_db()
    load_data()
    # Устанавливаем настройки по умолчанию, если их нет
    for key, default in DEFAULT_SETTINGS.items():
        if key not in settings:
            save_setting(key, default)

    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin_command))
    application.add_handler(CommandHandler("fastbuy", fastbuy))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_message))  # для фото в рассылке

    logger.info("Бот запущен")
    application.run_polling()

if __name__ == "__main__":
    main()