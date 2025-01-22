from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.services.water_service import WaterService
from app.utils.exceptions import ValidationError
import logging


class WaterStates(StatesGroup):
    waiting_for_amount = State()


router = Router()
logger = logging.getLogger(__name__)


@router.message(Command("log_water"))
async def cmd_water(message: Message, state: FSMContext):
    """Обработка команды /water"""
    await message.answer(
        "Введите количество выпитой воды в миллилитрах (мл).\n"
        "Например: 250"
    )
    await state.set_state(WaterStates.waiting_for_amount)


@router.message(WaterStates.waiting_for_amount)
async def process_water_amount(message: Message, state: FSMContext):
    """Обработка введенного количества воды"""
    try:
        # Пробуем преобразовать введенное значение в число
        try:
            amount = int(message.text)
        except ValueError:
            await message.answer(
                "Пожалуйста, введите число.\n"
                "Например: 250"
            )
            return

        # Создаем сервис и логируем воду
        water_service = WaterService()
        await water_service.log_water(message.from_user.id, amount)

        # Получаем прогресс за день
        consumed, target = await water_service.get_daily_progress(
            message.from_user.id
        )

        # Формируем ответ
        remaining = max(0, target - consumed)
        progress_message = (
            f"✅ Записано: {amount} мл\n\n"
            f"Прогресс за сегодня:\n"
            f"🚰 Выпито воды: {consumed} из {target} мл\n"
            f"💧 Осталось выпить: {remaining} мл"
        )

        await message.answer(progress_message)
        logger.info(
            f"Water logged for user {message.from_user.id}: {amount} ml"
        )

    except ValidationError as e:
        await message.answer(str(e))
        logger.warning(
            f"Validation error for user {message.from_user.id}: {str(e)}"
        )

    except Exception as e:
        await message.answer(
            "Произошла ошибка при записи воды. "
            "Пожалуйста, попробуйте позже."
        )
        logger.error(
            f"Error processing water for user {
                message.from_user.id}: {str(e)}",
            exc_info=True
        )

    finally:
        await state.clear()
