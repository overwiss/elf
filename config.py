import os
from dotenv import load_dotenv

load_dotenv()
#pierrot_dev
BOT_TOKEN: str = os.getenv("BOT_TOKEN", "8646127356:AAEENwQwJyu5Ynbs9SlHvVvdu5sLtPYUXw4")
ADMIN_IDS: list[int] = [
    int(i.strip()) for i in os.getenv("ADMIN_IDS", "8418705574").split(",") if i.strip().isdigit()
]
LOG_GROUP_ID: int = int(os.getenv("LOG_GROUP_ID", "3622507815"))

TEXTS = {
    "ru": {
        "banned": "🚫 Вы заблокированы в этом боте.",
        "terms_text": (
            "Вы подтверждаете, что ознакомились и согласны с "
            "<<Условиями предоставления услуг Гарант сервиса?>>"
        ),
        "terms_btn": "✅ Полностью согласен",
        "welcome": (
            "Добро пожаловать в Playerok — сервис, обеспечивающий "
            "безопасность и удобство проведения сделок.\n\n"
            "Наш канал — {t.me/FunPayComNews}\n"
            "Поддержка — {t.me/FunPayManeger}"
        ),
        "continue_btn": "Продолжить",
        "main_menu_text": (
            "Playerok Bot | OTC\n"
            "Безопасный и удобный сервис для сделок!\n\n"
            "Наши преимущества:\n"
            "• Автоматические сделки\n"
            "• Вывод в любой валюте\n"
            "• Поддержка 24/7\n"
            "• Удобный интерфейс\n\n"
            "Выберите нужный раздел ниже:"
        ),
        "btn_deal": "🛡️ Создать сделку",
        "btn_profile": "👤 Профиль",
        "btn_requisites": "💳 Реквизиты",
        "btn_language": "🌍 Сменить язык",
        "btn_support": "📞 Поддержка",
        "btn_site": "🌐 Наш сайт",
        "btn_back": "🔙 Назад",
        "choose_deal_type": "Создать сделку\n\nВыберите тип сделки:",
        "btn_gift": "🎁 Подарок",
        "enter_gift_links": (
            "🛡 Создание сделки\n\n"
            "🎁 Введите ссылку(-и) на подарок(-и) в одном из форматов:\n"
            "https://... или t.me/...\n\n"
            "Например:\nt.me/nft/DurovsCap-1\n\n"
            "Если у вас несколько подарков, указывайте каждую ссылку с новой строки, например:\n"
            "t.me/nft/DurovsCap-1\n"
            "t.me/nft/PlushPepe-2\n"
            "t.me/nft/EternalRose-3"
        ),
        "choose_currency": "🛡 Создание сделки\n\nВыберите валюту:",
        "enter_amount": "🛡 Создание сделки\n\nВведите сумму сделки в {currency}",
        "deal_created": (
            "✅ Сделка успешно создана!\n\n"
            "💰 Сумма: {amount} {currency}\n"
            "📜 Описание: {links}\n"
            "🔗 Ссылка для покупателя: {link}\n"
            "🔑 ID сделки: <code>{deal_id}</code>"
        ),
        "btn_cancel_deal": "❌ Отменить сделку",
        "cancel_deal_confirm": (
            "❌ Вы уверены, что хотите отменить сделку?\n\n"
            "Это действие нельзя будет отменить."
        ),
        "btn_yes_cancel": "✅ Да, отменить",
        "btn_no": "❌ Нет",
        "deal_cancelled": "✅ Сделка успешно отменена.",
        "deal_not_found": "❌ Сделка не найдена.",
        "deal_already_done": "❌ Сделка уже завершена или отменена.",
        "invalid_link": "❌ Некорректная ссылка. Используйте формат https://... или t.me/...",
        "invalid_amount": "❌ Некорректная сумма. Введите число больше 0.",
        "profile_text": (
            "👤 Профиль пользователя\n\n"
            "Имя пользователя: @{username}\n"
            "Общий баланс: {balance_rub} RUB\n"
            "Общий баланс крипто валюты: {balance_crypto} RUB\n"
            "Всего сделок: {total_deals}\n"
            "Успешных сделок: {successful_deals}\n"
            "Суммарный оборот: {turnover} RUB\n"
            "Верификация: {verified}"
        ),
        "btn_topup": "💳 Пополнить баланс",
        "topup_info": (
            "❓ Как работают кнопки выбора валюты?\n\n"
            "Когда вы выбираете, например, На карту → RUB → вводите сумму, "
            "бот автоматически считает, сколько нужно пополнить в TON или USDT (сеть TON), "
            "чтобы после пополнения у вас хватило средств для оплаты сделки(-ок) "
            "на введённую вами сумму.\n\n"
            "💡 Пример: если вы выбираете «На карту → RUB» и вводите 1000, "
            "бот подскажет, сколько нужно пополнить для того чтобы вы смогли "
            "оплатить сделку на 1000 RUB\n\n"
            "Таким образом, вы всегда пополняете нужную вам сумму для оплаты "
            "сделок на любые валюты в валюте TON или USDT"
        ),
        "btn_understood": "✅ Я прочитал(-а)",
        "topup_choose": (
            "💳 Пополнение баланса\n\n"
            "Выберите способ — бот автоматически рассчитает, "
            "сколько TON или же USDT нужно для пополнения."
        ),
        "btn_card": "💳 Банковская карта",
        "btn_ton": "💎 TON",
        "btn_withdraw": "💸 Вывод средств",
        "topup_card": (
            "{card_number} — {card_name}, {card_bank}\n\n"
            "Переводите точную сумму и не забывайте мемо комментарий\n"
            "Мемо: <code>{memo}</code>"
        ),
        "topup_ton": (
            "Адрес кошелька:\n<code>{ton_wallet}</code>\n\n"
            "Не забудьте указать точную сумму и мемо комментарий\n"
            "Мемо: <code>{memo}</code>"
        ),
        "requisites_menu": "💳 Управление реквизитами\n\nВыберите одну из предложенных ниже опций:",
        "btn_add_card": "💳 Добавить карту",
        "btn_add_ton": "💎 Добавить TON кошелек",
        "btn_view_reqs": "👀 Посмотреть реквизиты",
        "enter_card": "Введите номер банковской карты (16 цифр):",
        "enter_ton_wallet": "Введите адрес TON кошелька:",
        "req_saved": "✅ Реквизит успешно сохранён!",
        "req_invalid_card": "❌ Некорректный номер карты. Введите 16 цифр без пробелов.",
        "req_invalid_ton": "❌ Некорректный TON адрес.",
        "no_requisites": "У вас пока нет сохранённых реквизитов.",
        "your_requisites": "📋 Ваши реквизиты:\n\n{items}",
        "language_menu": (
            "🌍 Изменить язык\n\nВыберите предпочитаемый язык:"
        ),
        "btn_ru": "🇷🇺 Русский",
        "btn_en": "🇺🇸 English",
        "btn_back_menu": "🔙 Обратно в меню",
        "language_set": "✅ Язык успешно изменён!",
        "support_text": "📞 Поддержка\n\nОбратитесь к нашему оператору: {support}",
        "withdraw_text": (
            "💸 Для вывода средств обратитесь в поддержку: {support}\n\n"
            "Укажите:\n• Сумму вывода\n• Ваши реквизиты из профиля"
        ),
    },
    "en": {
        "banned": "🚫 You are banned in this bot.",
        "terms_text": (
            "Do you confirm that you have read and agree with "
            "<<Terms of Service of the Guarantee Service?>>"
        ),
        "terms_btn": "✅ I fully agree",
        "welcome": (
            "Welcome to Playerok — a service ensuring safety and convenience of deals.\n\n"
            "Our channel — {channel}\n"
            "Support — {support}"
        ),
        "continue_btn": "Continue",
        "main_menu_text": (
            "Playerok Bot | OTC\n"
            "Safe and convenient service for deals!\n\n"
            "Our advantages:\n"
            "• Automatic deals\n"
            "• Withdrawal in any currency\n"
            "• 24/7 support\n"
            "• User-friendly interface\n\n"
            "Select a section below:"
        ),
        "btn_deal": "🛡️ Create Deal",
        "btn_profile": "👤 Profile",
        "btn_requisites": "💳 Requisites",
        "btn_language": "🌍 Change Language",
        "btn_support": "📞 Support",
        "btn_site": "🌐 Our Website",
        "btn_back": "🔙 Back",
        "choose_deal_type": "Create Deal\n\nChoose deal type:",
        "btn_gift": "🎁 Gift",
        "enter_gift_links": (
            "🛡 Creating Deal\n\n"
            "🎁 Enter gift link(s) in one of the formats:\n"
            "https://... or t.me/...\n\n"
            "Example:\nt.me/nft/DurovsCap-1\n\n"
            "For multiple gifts, put each link on a new line:\n"
            "t.me/nft/DurovsCap-1\n"
            "t.me/nft/PlushPepe-2\n"
            "t.me/nft/EternalRose-3"
        ),
        "choose_currency": "🛡 Creating Deal\n\nChoose currency:",
        "enter_amount": "🛡 Creating Deal\n\nEnter deal amount in {currency}",
        "deal_created": (
            "✅ Deal successfully created!\n\n"
            "💰 Amount: {amount} {currency}\n"
            "📜 Description: {links}\n"
            "🔗 Buyer link: {link}\n"
            "🔑 Deal ID: <code>{deal_id}</code>"
        ),
        "btn_cancel_deal": "❌ Cancel Deal",
        "cancel_deal_confirm": (
            "❌ Are you sure you want to cancel the deal?\n\n"
            "This action cannot be undone."
        ),
        "btn_yes_cancel": "✅ Yes, cancel",
        "btn_no": "❌ No",
        "deal_cancelled": "✅ Deal successfully cancelled.",
        "deal_not_found": "❌ Deal not found.",
        "deal_already_done": "❌ Deal already completed or cancelled.",
        "invalid_link": "❌ Invalid link. Use format https://... or t.me/...",
        "invalid_amount": "❌ Invalid amount. Enter a number greater than 0.",
        "profile_text": (
            "👤 User Profile\n\n"
            "Username: @{username}\n"
            "Total balance: {balance_rub} RUB\n"
            "Crypto balance: {balance_crypto} RUB\n"
            "Total deals: {total_deals}\n"
            "Successful deals: {successful_deals}\n"
            "Total turnover: {turnover} RUB\n"
            "Verification: {verified}"
        ),
        "btn_topup": "💳 Top Up Balance",
        "topup_info": (
            "❓ How do currency selection buttons work?\n\n"
            "When you choose, for example, Card → RUB → enter amount, "
            "the bot automatically calculates how much TON or USDT (TON network) "
            "you need to top up to have enough for your deal.\n\n"
            "💡 Example: if you choose «Card → RUB» and enter 1000, "
            "the bot will tell you how much to top up to pay for a 1000 RUB deal.\n\n"
            "You always top up the required amount in TON or USDT."
        ),
        "btn_understood": "✅ I've read it",
        "topup_choose": (
            "💳 Top Up Balance\n\n"
            "Choose method — bot will automatically calculate "
            "how much TON or USDT is needed."
        ),
        "btn_card": "💳 Bank Card",
        "btn_ton": "💎 TON",
        "btn_withdraw": "💸 Withdraw",
        "topup_card": (
            "{card_number} — {card_name}, {card_bank}\n\n"
            "Send the exact amount and don't forget the memo comment\n"
            "Memo: <code>{memo}</code>"
        ),
        "topup_ton": (
            "Wallet address:\n<code>{ton_wallet}</code>\n\n"
            "Don't forget to specify exact amount and memo comment\n"
            "Memo: <code>{memo}</code>"
        ),
        "requisites_menu": "💳 Manage Requisites\n\nChoose one of the options below:",
        "btn_add_card": "💳 Add Card",
        "btn_add_ton": "💎 Add TON Wallet",
        "btn_view_reqs": "👀 View Requisites",
        "enter_card": "Enter bank card number (16 digits):",
        "enter_ton_wallet": "Enter TON wallet address:",
        "req_saved": "✅ Requisite successfully saved!",
        "req_invalid_card": "❌ Invalid card number. Enter 16 digits without spaces.",
        "req_invalid_ton": "❌ Invalid TON address.",
        "no_requisites": "You have no saved requisites yet.",
        "your_requisites": "📋 Your requisites:\n\n{items}",
        "language_menu": "🌍 Change Language\n\nChoose your preferred language:",
        "btn_ru": "🇷🇺 Russian",
        "btn_en": "🇺🇸 English",
        "btn_back_menu": "🔙 Back to Menu",
        "language_set": "✅ Language successfully changed!",
        "support_text": "📞 Support\n\nContact our operator: {support}",
        "withdraw_text": (
            "💸 To withdraw funds, contact support: {support}\n\n"
            "Specify:\n• Withdrawal amount\n• Your requisites from profile"
        ),
    }
}
