from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.services.profile_service import ProfileService
from app.utils.validators import (
    validate_weight,
    validate_height,
    validate_age,
    validate_activity_level
)


router = Router()


class ProfileStates(StatesGroup):
    waiting_for_weight = State()
    waiting_for_height = State()
    waiting_for_age = State()
    waiting_for_activity = State()
    waiting_for_city = State()


@router.message(Command("set_profile"))
async def start_profile_setup(message: Message, state: FSMContext):
    await message.answer(
        "Давайте настроим ваш профиль!\n"
        "Введите ваш вес в килограммах (например: 70)"
    )
    await state.set_state(ProfileStates.waiting_for_weight)


@router.message(ProfileStates.waiting_for_weight)
async def process_weight(message: Message, state: FSMContext):
    """Обработка введенного веса"""
    try:
        weight = float(message.text)
        if not validate_weight(weight):
            raise ValueError("Недопустимое значение веса")

        await state.update_data(weight=weight)
        await message.answer(
            "Отлично! Теперь введите ваш рост в сантиметрах (например: 175)"
        )
        await state.set_state(ProfileStates.waiting_for_height)

    except ValueError:
        await message.answer(
            "Пожалуйста, введите корректное значение веса (от 30 до 300 кг)"
        )


@router.message(ProfileStates.waiting_for_height)
async def process_height(message: Message, state: FSMContext):
    """Обработка введенного роста"""
    try:
        height = float(message.text)
        if not validate_height(height):
            raise ValueError("Недопустимое значение роста")

        await state.update_data(height=height)
        await message.answer("Введите ваш возраст")
        await state.set_state(ProfileStates.waiting_for_age)

    except ValueError:
        await message.answer(
            "Пожалуйста, введите корректное значение роста (от 100 до 250 см)"
        )


@router.message(ProfileStates.waiting_for_age)
async def process_age(message: Message, state: FSMContext):
    """Обработка введенного возраста"""
    try:
        age = int(message.text)
        if not validate_age(age):
            raise ValueError("Недопустимое значение возраста")

        await state.update_data(age=age)
        await message.answer(
            "Выберите уровень физической активности:\n"
            "1 - Сидячий образ жизни\n"
            "2 - Умеренная активность\n"
            "3 - Высокая активность\n"
            "4 - Очень высокая активность"
        )
        await state.set_state(ProfileStates.waiting_for_activity)

    except ValueError:
        await message.answer(
            "Пожалуйста, введите корректный возраст (от 14 до 100 лет)"
        )


@router.message(ProfileStates.waiting_for_activity)
async def process_activity(message: Message, state: FSMContext):
    """Обработка уровня активности"""
    try:
        activity_level = int(message.text)
        if not validate_activity_level(activity_level):
            raise ValueError("Недопустимый уровень активности")

        await state.update_data(activity_level=activity_level)
        await message.answer("Введите название вашего города")
        await state.set_state(ProfileStates.waiting_for_city)

    except ValueError:
        await message.answer(
            "Пожалуйста, выберите уровень активности от 1 до 4"
        )


@router.message(ProfileStates.waiting_for_city)
async def process_city(message: Message, state: FSMContext):
    """Завершение настройки профиля"""
    try:
        # Получаем данные из состояния
        user_data = await state.get_data()
        user_data['city'] = message.text
        user_data['user_id'] = message.from_user.id

        # Создаем сервис и сохраняем профиль
        profile_service = ProfileService()
        await profile_service.create_or_update_profile(user_data)

        # Получаем профиль пользователя с рассчитанными целями
        profile = await profile_service.get_profile(message.from_user.id)

        if profile:
            await message.answer(
                "Профиль успешно настроен!\n"
                f"Ваша дневная норма калорий: {profile.calorie_goal} ккал\n"
                f"Рекомендуемое потребление воды: {profile.water_goal} мл\n\n"
                "Теперь вы можете использовать команды:\n"
                "/log_water - записать потребление воды\n"
                "/log_food - записать приём пищи\n"
                "/log_workout - записать тренировку\n"
                "/check_progress - посмотреть прогресс за день"
            )
        else:
            await message.answer(
                "Произошла ошибка при создании профиля. "
                "Пожалуйста, попробуйте позже."
            )

    except Exception:
        await message.answer(
            "Произошла ошибка при сохранении профиля. "
            "Пожалуйста, попробуйте позже."
        )

    finally:
        await state.clear()


@router.message(Command("profile"))
async def show_profile(message: Message):
    """Показать текущий профиль пользователя"""
    try:
        profile_service = ProfileService()
        user_profile = await profile_service.get_profile(message.from_user.id)

        if not user_profile:
            await message.answer(
                "Профиль не найден. Используйте /set_profile для настройки."
            )
            return

        calories = profile_service.calculate_daily_calories(user_profile)
        water = profile_service.calculate_daily_water(user_profile)

        await message.answer(
            f"Ваш профиль:\n"
            f"Вес: {user_profile.weight} кг\n"
            f"Рост: {user_profile.height} см\n"
            f"Возраст: {user_profile.age} лет\n"
            f"Город: {user_profile.city}\n"
            f"Уровень активности: {user_profile.activity_level}\n"
            f"Дневная норма калорий: {calories} ккал\n"
            f"Дневная норма воды: {water} мл"
        )

    except Exception as e:
        await message.answer(
            "Произошла ошибка при получении профиля. "
            "Пожалуйста, попробуйте позже."
        )
        print(f"Error fetching profile: {e}")
