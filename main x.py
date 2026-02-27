import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from database import Database
from handlers import start, deals, profile, requisites, language, support, admin


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


async def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN не указан сука в .env файле!")

    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    db = Database()
    await db.init()

    dp["db"] = db

    dp.include_router(admin.router)
    dp.include_router(start.router)
    dp.include_router(deals.router)
    dp.include_router(profile.router)
    dp.include_router(requisites.router)
    dp.include_router(language.router)
    dp.include_router(support.router)

    logging.info("Бот запущен!")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
