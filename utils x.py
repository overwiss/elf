import re
from aiogram import Bot
from config import LOG_GROUP_ID

TOPIC_KEYS = {
    "users": "topic_users",
    "deals": "topic_deals",
    "topups": "topic_topups",
    "withdrawals": "topic_withdrawals",
    "requisites": "topic_requisites",
    "admin": "topic_admin",
    "general": "topic_general",
}


def is_valid_gift_link(link: str) -> bool:
    link = link.strip()
    patterns = [
        r"^https://t\.me/nft/.+",
        r"^t\.me/nft/.+",
        r"^https://t\.me/.+",
        r"^t\.me/.+",
        r"^https://.+",
    ]
    return any(re.match(p, link) for p in patterns)


def validate_gift_links(text: str) -> tuple[bool, list[str]]:
    lines = [l.strip() for l in text.strip().splitlines() if l.strip()]
    if not lines:
        return False, []
    for line in lines:
        if not is_valid_gift_link(line):
            return False, []
    return True, lines


def is_valid_card(card: str) -> bool:
    return bool(re.match(r"^\d{16}$", card.replace(" ", "")))


def is_valid_ton_wallet(wallet: str) -> bool:
    return bool(re.match(r"^[A-Za-z0-9_\-]{48}$", wallet))


async def send_log(bot: Bot, text: str, topic: str = "general", db=None):
    if not LOG_GROUP_ID:
        return
    thread_id = None
    if db is not None:
        key = TOPIC_KEYS.get(topic)
        if key:
            raw = await db.get_setting(key)
            if raw and raw.isdigit():
                thread_id = int(raw)
    try:
        await bot.send_message(
            LOG_GROUP_ID,
            text,
            parse_mode="HTML",
            message_thread_id=thread_id,
        )
    except Exception:
        pass


def fmt_username(username: str | None, tg_id: int) -> str:
    if username:
        return f"@{username}"
    return f"ID:{tg_id}"
