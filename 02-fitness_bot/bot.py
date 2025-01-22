import asyncio
import logging
from aiogram import Bot, Dispatcher

from config import settings
from app.bot.handlers import register_handlers
from app.bot.middlewares import setup_middlewares
from app.db.database import init_db


logging.basicConfig(level=logging.INFO)


async def main():
    await init_db()
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()
    setup_middlewares(dp)
    register_handlers(dp)
    await bot.delete_webhook()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
