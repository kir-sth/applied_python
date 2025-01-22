from app.db.database import async_session_maker
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.services.food_service import FoodService


class FoodStates(StatesGroup):
    waiting_for_food = State()
    waiting_for_portion = State()


router = Router()


@router.message(Command("log_food"))
async def cmd_food(message: Message, state: FSMContext):
    """Начало логирования приема пищи"""
    await message.answer(
        "🔍 Введите название продукта или блюда.\n"
        "Например: яблоко, овсянка, йогурт\n\n"
        "Для отмены введите /cancel"
    )
    await state.set_state(FoodStates.waiting_for_food)


@router.message(FoodStates.waiting_for_food)
async def process_food_name(message: Message, state: FSMContext):
    """Обработка названия продукта"""
    try:
        if message.text.startswith('/'):
            await state.clear()
            await message.answer("Поиск продукта отменен")
            return

        async with async_session_maker() as session:
            food_service = FoodService(session=session)
            food_items = await food_service.search_food(message.text)

            if not food_items:
                await message.answer(
                    "❌ Продукт не найден. Попробуйте ввести другое название.\n"
                    "Например: молоко, хлеб, банан"
                )
                return

            await state.update_data(
                food_items=food_items,
                selected_food=food_items[0]
            )

            food = food_items[0]
            nutritional_info = (
                f"📋 Найден продукт: {food['name']}\n"
                f"🔸 Калорийность: {food['calories']:.1f} ккал/100г\n"
                f"🔸 Белки: {food.get('proteins', 0):.1f} г\n"
                f"🔸 Жиры: {food.get('fats', 0):.1f} г\n"
                f"🔸 Углеводы: {food.get('carbs', 0):.1f} г\n\n"
                "⚖️ Введите размер порции в граммах (1-2000):"
            )

            await message.answer(nutritional_info)
            await state.set_state(FoodStates.waiting_for_portion)

    except Exception:
        await message.answer(
            "❌ Произошла ошибка при поиске продукта.\n"
            "Пожалуйста, попробуйте позже."
        )
        await state.clear()


@router.message(FoodStates.waiting_for_portion)
async def process_portion(message: Message, state: FSMContext):
    """Обработка размера порции"""
    try:
        if message.text.startswith('/'):
            await state.clear()
            await message.answer("Запись продукта отменена")
            return

        try:
            portion = float(message.text)
            if portion <= 0 or portion > 2000:
                await message.answer(
                    "⚠️ Размер порции должен быть от 1 до 2000 грамм.\n"
                    "Пожалуйста, введите корректное значение:"
                )
                return
        except ValueError:
            await message.answer(
                "⚠️ Пожалуйста, введите число.\n"
                "Например: 100"
            )
            return

        user_data = await state.get_data()
        selected_food = user_data['selected_food']
        calories = (selected_food['calories'] * portion) / 100

        async with async_session_maker() as session:
            food_service = FoodService(session=session)
            await food_service.log_food(
                user_id=message.from_user.id,
                food_name=selected_food['name'],
                portion=portion,
                calories=calories
            )

            consumed, target = await food_service.get_daily_progress(message.from_user.id)  # noqa: E501

            remaining = max(0, target - consumed)
            progress_percentage = min(100, (consumed / target) * 100)

            await message.answer(
                f"✅ Продукт записан!\n\n"
                f"📊 Ваш прогресс на сегодня:\n"
                f"Съедено: {consumed:.0f} ккал\n"
                f"Осталось: {remaining:.0f} ккал\n"
                f"Прогресс: {progress_percentage:.1f}%"
            )
            await state.clear()

    except Exception:
        await message.answer(
            "❌ Произошла ошибка при сохранении данных.\n"
            "Пожалуйста, попробуйте позже."
        )
        await state.clear()
