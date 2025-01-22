from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from app.db.database import async_session_maker
from app.services.progress_service import ProgressService

router = Router()


@router.message(Command("check_progress"))
async def cmd_check_progress(message: Message):
    """Отображение прогресса за день"""
    try:
        async with async_session_maker() as session:
            progress_service = ProgressService(session)
            progress = await progress_service.get_daily_progress(
                message.from_user.id
            )

            # Создаем индикаторы прогресса
            water_percentage = min(100, int(
                progress.water_consumed / progress.water_target * 100)) if progress.water_target else 0  # noqa: E501
            water_progress = "🌊" * (water_percentage // 20) + \
                "⚪️" * (5 - water_percentage // 20)

            calories_percentage = min(100, int(
                progress.calories_consumed / progress.calories_target * 100)) if progress.calories_target else 0  # noqa: E501
            calories_progress = "🔴" * \
                (calories_percentage // 20) + "⚪️" * \
                (5 - calories_percentage // 20)

            await message.answer(
                f"📊 Ваш прогресс за сегодня:\n\n"
                f"💧 Вода: {
                    progress.water_consumed}/{progress.water_target} мл\n"
                f"{water_progress}\n\n"
                f"🍎 Калории: {progress.calories_consumed}/{progress.calories_target} ккал\n"  # noqa: E501
                f"{calories_progress}\n\n"
                f"🏃‍♂️ Сожжено: {progress.calories_burned} ккал\n"
                f"⚖️ Баланс: {progress.calories_remaining} ккал\n"
                f"🏋️‍♂️ Тренировок: {progress.workout_count}\n\n"
                f"{'✅ Отличная работа!' if progress.calories_remaining >=
                    0 else '⚠️ Превышение калорий'}"
            )

    except ValueError:
        await message.answer(
            "❌ Ошибка: Пожалуйста, сначала настройте свой профиль с помощью /set_profile"  # noqa: E501
        )
    except Exception:
        await message.answer(
            "❌ Произошла ошибка при получении прогресса.\n"
            "Пожалуйста, попробуйте позже."
        )
