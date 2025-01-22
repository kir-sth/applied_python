from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.db.database import async_session_maker
from app.services.workout_service import WorkoutService
from app.schemas.workout import WorkoutCreate

router = Router()

WORKOUT_TYPES = {
    "1": "Бег",
    "2": "Ходьба",
    "3": "Велосипед",
    "4": "Плавание",
    "5": "Силовая тренировка",
    "6": "Йога",
    "7": "Другое"
}

INTENSITY_LEVELS = {
    "1": "low",
    "2": "medium",
    "3": "high"
}


class WorkoutStates(StatesGroup):
    waiting_for_type = State()
    waiting_for_duration = State()
    waiting_for_intensity = State()


@router.message(Command("log_workout"))
async def cmd_log_workout(message: Message, state: FSMContext):
    """Начало логирования тренировки"""
    workout_types = "\n".join([f"{k}. {v}" for k, v in WORKOUT_TYPES.items()])
    await message.answer(
        "🏃‍♂️ Выберите тип тренировки (введите номер):\n\n"
        f"{workout_types}\n\n"
        "Для отмены введите /cancel"
    )
    await state.set_state(WorkoutStates.waiting_for_type)


@router.message(WorkoutStates.waiting_for_type)
async def process_workout_type(message: Message, state: FSMContext):
    """Обработка типа тренировки"""
    if message.text.startswith('/'):
        await state.clear()
        await message.answer("Запись тренировки отменена")
        return

    if message.text not in WORKOUT_TYPES:
        await message.answer(
            "⚠️ Пожалуйста, выберите номер из списка (1-7):"
        )
        return

    workout_type = WORKOUT_TYPES[message.text]
    await state.update_data(workout_type=workout_type)

    await message.answer(
        "⏱ Введите продолжительность тренировки в минутах (1-300):"
    )
    await state.set_state(WorkoutStates.waiting_for_duration)


@router.message(WorkoutStates.waiting_for_duration)
async def process_duration(message: Message, state: FSMContext):
    """Обработка продолжительности тренировки"""
    try:
        if message.text.startswith('/'):
            await state.clear()
            await message.answer("Запись тренировки отменена")
            return

        try:
            duration = int(message.text)
            if duration < 1 or duration > 300:
                await message.answer(
                    "⚠️ Продолжительность должна быть от 1 до 300 минут.\n"
                    "Пожалуйста, введите корректное значение:"
                )
                return
        except ValueError:
            await message.answer(
                "⚠️ Пожалуйста, введите целое число.\n"
                "Например: 30"
            )
            return

        await state.update_data(duration=duration)
        await message.answer(
            "💪 Выберите интенсивность тренировки:\n"
            "1. Низкая\n"
            "2. Средняя\n"
            "3. Высокая"
        )
        await state.set_state(WorkoutStates.waiting_for_intensity)

    except Exception:
        await message.answer("❌ Произошла ошибка. Попробуйте позже.")
        await state.clear()


@router.message(WorkoutStates.waiting_for_intensity)
async def process_intensity(message: Message, state: FSMContext):
    """Обработка интенсивности тренировки"""
    try:
        if message.text.startswith('/'):
            await state.clear()
            await message.answer("Запись тренировки отменена")
            return

        if message.text not in INTENSITY_LEVELS:
            await message.answer(
                "⚠️ Пожалуйста, выберите интенсивность (1-3):"
            )
            return

        intensity = INTENSITY_LEVELS[message.text]
        user_data = await state.get_data()

        async with async_session_maker() as session:
            workout_service = WorkoutService(session)
            calories_burned = workout_service.calculate_calories_burned(
                user_data['workout_type'],
                user_data['duration'],
                intensity
            )

            workout_data = WorkoutCreate(
                user_id=message.from_user.id,
                workout_type=user_data['workout_type'],
                duration=user_data['duration'],
                intensity=intensity,
                calories_burned=calories_burned
            )

            await workout_service.log_workout(workout_data)
            daily_stats = await workout_service.get_daily_stats(
                message.from_user.id
            )

            await message.answer(
                f"✅ Тренировка записана!\n\n"
                f"📊 Статистика за сегодня:\n"
                f"🏃‍♂️ Тренировка: {user_data['workout_type']}\n"
                f"⏱ Длительность: {user_data['duration']} мин\n"
                f"🔥 Сожжено калорий: {calories_burned} ккал\n\n"
                f"Всего за день:\n"
                f"⚡️ Сожжено: {daily_stats.total_burned} ккал\n"
                f"🎯 Съедено: {daily_stats.calories_consumed} ккал\n"
                f"⭐️ Баланс: {daily_stats.calories_remaining} ккал\n"
                f"🏋️‍♂️ Тренировок: {daily_stats.workout_count}"
            )

            await state.clear()

    except Exception:
        await message.answer(
            "❌ Произошла ошибка при сохранении тренировки.\n"
            "Пожалуйста, попробуйте позже."
        )
        await state.clear()
