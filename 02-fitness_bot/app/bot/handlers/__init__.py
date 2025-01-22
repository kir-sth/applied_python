from aiogram import Dispatcher
from app.bot.handlers.common import router as common_router
from app.bot.handlers.profile import router as profile_router
from app.bot.handlers.water import router as water_router
from app.bot.handlers.food import router as food_router
from app.bot.handlers.workout import router as workout_router
from app.bot.handlers.progress import router as progress_router


def register_handlers(dp: Dispatcher):
    hadnlers = [
        progress_router,
        food_router,
        water_router,
        workout_router,
        profile_router,
        common_router,
    ]

    for handler in hadnlers:
        dp.include_router(handler)
