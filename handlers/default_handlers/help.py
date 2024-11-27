from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from config_data.config import DEFAULT_COMMANDS


router = Router()
text = [f"/{command} - {desk}" for command, desk in DEFAULT_COMMANDS]


@router.message(Command("help"))
async def get_help(message: Message, state: FSMContext) -> None:
    """
    Обрабатывает команду /help и отправляет пользователю список доступных команд.

    При получении команды /help, функция:
    - Очищает состояние пользователя.
    - Сбрасывает параметры поиска.
    - Записывает информацию о команде в лог.
    - Отправляет пользователю сообщение со списком доступных команд.

    Args:
        message (Message): Сообщение от пользователя, содержащие команду /help.
        state (FSMContext): Контекст состояния, который позволяет управлять состоянием пользователя.

    Returns:
        None: Функция не возвращает значения, но отправляет сообщение пользователю.
    """
    await state.clear()
    await message.answer("\n".join(text))