from aiogram.types import Message
from aiogram.filters import Command
from aiogram import Router

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Привет! Я бот для трекинга воды и калорий.\n"
        "Используйте /help для просмотра доступных команд."
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    help_text = """
    Доступные команды:
    /set_profile - Настройка профиля
    /log_water <мл> - Записать потребление воды
    /log_food <продукт> - Записать приём пищи
    /log_workout <тип> <минуты> - Записать тренировку
    /check_progress - Посмотреть прогресс за день
    /help - Показать это сообщение
    """
    await message.answer(help_text)
