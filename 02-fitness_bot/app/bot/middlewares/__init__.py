from aiogram import Dispatcher

from app.bot.middlewares.common_middleware import LoggingMiddleware


def setup_middlewares(dp: Dispatcher) -> None:
    dp.message.middleware(LoggingMiddleware())
