import aiosqlite
import random
import string
from datetime import datetime


DB_PATH = "playerok.db"


def generate_id(length: int = 10) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


def generate_memo(length: int = 7) -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


class Database:
    def __init__(self):
        self.db_path = DB_PATH

    async def init(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tg_id INTEGER UNIQUE NOT NULL,
                    username TEXT,
                    language TEXT DEFAULT 'ru',
                    balance_rub REAL DEFAULT 0,
                    balance_crypto REAL DEFAULT 0,
                    total_deals INTEGER DEFAULT 0,
                    successful_deals INTEGER DEFAULT 0,
                    turnover REAL DEFAULT 0,
                    is_verified INTEGER DEFAULT 0,
                    is_banned INTEGER DEFAULT 0,
                    agreed_terms INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS deals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    deal_id TEXT UNIQUE NOT NULL,
                    creator_id INTEGER NOT NULL,
                    buyer_id INTEGER,
                    buyer_username TEXT,
                    gift_links TEXT NOT NULL,
                    currency TEXT NOT NULL,
                    amount REAL NOT NULL,
                    status TEXT DEFAULT 'pending',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS requisites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    type TEXT NOT NULL,
                    value TEXT NOT NULL,
                    label TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)
            await db.execute("""
                INSERT OR IGNORE INTO settings (key, value) VALUES
                ('support_username', '@PlayerokOTCsupport'),
                ('website_url', 'https://playerok.com'),
                ('channel_url', 'https://t.me/playerok'),
                ('card_number', '+79275173373'),
                ('card_name', 'Ярослав'),
                ('card_bank', 'Сбербанк'),
                ('ton_wallet', 'UQC8XYKyH-u5NPNGJEU_WFlqamxCqsai63_e9SuCLOH2m8_E'),
                ('terms_url', 'https://telegra.ph/Ispolzuya-Nash-servis-Vy-soglashaetes-s-01-02-2'),
                ('photo_file_id', ''),
                ('topic_users', ''),
                ('topic_deals', ''),
                ('topic_topups', ''),
                ('topic_withdrawals', ''),
                ('topic_requisites', ''),
                ('topic_admin', ''),
                ('topic_general', ''),
                ('gift_account', '@PlayerokOTC')
            """)
            await db.commit()

    async def get_setting(self, key: str) -> str:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT value FROM settings WHERE key = ?", (key,)) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else ""

    async def set_setting(self, key: str, value: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                (key, value)
            )
            await db.commit()

    async def get_user(self, tg_id: int) -> dict | None:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM users WHERE tg_id = ?", (tg_id,)) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None

    async def create_user(self, tg_id: int, username: str | None):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR IGNORE INTO users (tg_id, username) VALUES (?, ?)",
                (tg_id, username or "")
            )
            await db.commit()

    async def update_user_username(self, tg_id: int, username: str | None):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE users SET username = ? WHERE tg_id = ?",
                (username or "", tg_id)
            )
            await db.commit()

    async def set_agreed_terms(self, tg_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE users SET agreed_terms = 1 WHERE tg_id = ?",
                (tg_id,)
            )
            await db.commit()

    async def set_language(self, tg_id: int, lang: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE users SET language = ? WHERE tg_id = ?",
                (lang, tg_id)
            )
            await db.commit()

    async def get_language(self, tg_id: int) -> str:
        user = await self.get_user(tg_id)
        return user["language"] if user else "ru"

    async def ban_user(self, tg_id: int, is_banned: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE users SET is_banned = ? WHERE tg_id = ?",
                (is_banned, tg_id)
            )
            await db.commit()

    async def is_banned(self, tg_id: int) -> bool:
        user = await self.get_user(tg_id)
        return bool(user and user["is_banned"])

    async def deduct_balance(self, tg_id: int, amount: float, currency: str) -> bool:
        crypto_currencies = ("USDT", "TON", "Stars")
        field = "balance_crypto" if currency in crypto_currencies else "balance_rub"
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                f"SELECT {field} FROM users WHERE tg_id = ?", (tg_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if not row or row[0] < amount:
                    return False
            await db.execute(
                f"UPDATE users SET {field} = {field} - ? WHERE tg_id = ?",
                (amount, tg_id)
            )
            await db.commit()
        return True

    async def get_balance(self, tg_id: int, currency: str) -> float:
        crypto_currencies = ("USDT", "TON", "Stars")
        field = "balance_crypto" if currency in crypto_currencies else "balance_rub"
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                f"SELECT {field} FROM users WHERE tg_id = ?", (tg_id,)
            ) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0.0

    async def add_balance(self, tg_id: int, amount: float):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE users SET balance_rub = balance_rub + ? WHERE tg_id = ?",
                (amount, tg_id)
            )
            await db.commit()

    async def set_successful_deals(self, tg_id: int, count: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE users SET successful_deals = ? WHERE tg_id = ?",
                (count, tg_id)
            )
            await db.commit()

    async def set_total_deals(self, tg_id: int, count: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE users SET total_deals = ? WHERE tg_id = ?",
                (count, tg_id)
            )
            await db.commit()

    async def set_turnover(self, tg_id: int, amount: float):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE users SET turnover = ? WHERE tg_id = ?",
                (amount, tg_id)
            )
            await db.commit()

    async def create_deal(self, creator_id: int, gift_links: str, currency: str, amount: float) -> str:
        deal_id = generate_id(10)
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """INSERT INTO deals (deal_id, creator_id, gift_links, currency, amount)
                   VALUES (?, ?, ?, ?, ?)""",
                (deal_id, creator_id, gift_links, currency, amount)
            )
            await db.execute(
                "UPDATE users SET total_deals = total_deals + 1 WHERE tg_id = ?",
                (creator_id,)
            )
            await db.commit()
        return deal_id

    async def get_deal(self, deal_id: str) -> dict | None:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM deals WHERE deal_id = ?", (deal_id,)) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None

    async def set_deal_buyer(self, deal_id: str, buyer_id: int, buyer_username: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE deals SET buyer_id = ?, buyer_username = ? WHERE deal_id = ?",
                (buyer_id, buyer_username, deal_id)
            )
            await db.commit()

    async def set_deal_status(self, deal_id: str, status: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE deals SET status = ? WHERE deal_id = ?",
                (status, deal_id)
            )
            await db.commit()

    async def cancel_deal(self, deal_id: str):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT creator_id FROM deals WHERE deal_id = ?", (deal_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    await db.execute(
                        "UPDATE users SET total_deals = MAX(0, total_deals - 1) WHERE tg_id = ?",
                        (row[0],)
                    )
            await db.execute(
                "UPDATE deals SET status = 'cancelled' WHERE deal_id = ?",
                (deal_id,)
            )
            await db.commit()

    async def complete_deal(self, deal_id: str, buyer_id: int, buyer_username: str):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT creator_id, amount FROM deals WHERE deal_id = ?", (deal_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    creator_id, amount = row
                    await db.execute(
                        """UPDATE users SET
                           successful_deals = successful_deals + 1,
                           turnover = turnover + ?
                           WHERE tg_id = ?""",
                        (amount, creator_id)
                    )
            await db.execute(
                """UPDATE deals SET status = 'completed', buyer_id = ?, buyer_username = ?
                   WHERE deal_id = ?""",
                (buyer_id, buyer_username, deal_id)
            )
            await db.commit()

    async def add_requisite(self, user_id: int, req_type: str, value: str, label: str = ""):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO requisites (user_id, type, value, label) VALUES (?, ?, ?, ?)",
                (user_id, req_type, value, label)
            )
            await db.commit()

    async def get_requisites(self, user_id: int) -> list:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM requisites WHERE user_id = ?", (user_id,)
            ) as cursor:
                rows = await cursor.fetchall()
                return [dict(r) for r in rows]

    async def get_all_users(self) -> list:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM users") as cursor:
                rows = await cursor.fetchall()
                return [dict(r) for r in rows]

    async def get_all_settings(self) -> dict:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT key, value FROM settings") as cursor:
                rows = await cursor.fetchall()
                return {r[0]: r[1] for r in rows}
