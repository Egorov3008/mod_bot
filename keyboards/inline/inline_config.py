from aiogram.types import Message
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


async def choice() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с выбором действий.

    :return: Объект InlineKeyboardMarkup с кнопками.
    """
    buttons = [[InlineKeyboardButton(text="Создать сообщение", callback_data="msg")],
               [InlineKeyboardButton(text="Темы чата", callback_data="topic")],
               [InlineKeyboardButton(text="Настроить архивацию", callback_data="set_archiving")]]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


async def choice_filter_done() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с выбором действий.

    :return: Объект InlineKeyboardMarkup с кнопками.
    """
    buttons = [
        [InlineKeyboardButton(text="Изменить текст", callback_data="text"),
         InlineKeyboardButton(text="Медиа+", callback_data="img")],
        [InlineKeyboardButton(text="Ссылка", callback_data="url"),
         InlineKeyboardButton(text="Время отправки", callback_data="time_out")],
        [InlineKeyboardButton(text="Время удаления", callback_data="time_del")],
        [InlineKeyboardButton(text="Выбор темы", callback_data="confirm")],
        [InlineKeyboardButton(text="Готово", callback_data="done")],
        [InlineKeyboardButton(text="Основное меню", callback_data="cancel")],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


async def kb_url() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с выбором действий.

    :return: Объект InlineKeyboardMarkup с кнопками.
    """
    buttons = [
        [InlineKeyboardButton(text="Ссылка", callback_data="URL"),
         InlineKeyboardButton(text="Название ссылки", callback_data="name_url")],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


async def url_kb_config(message: Message, url: str) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с кнопкой для url.

    :return: Объект InlineKeyboardMarkup с кнопкой для url.
    """
    buttons = [
        [InlineKeyboardButton(text=message.text, callback_data=url)],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


async def topic_chice() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с выбором действий.

    :return: Объект InlineKeyboardMarkup с кнопками.
    """
    buttons = [[InlineKeyboardButton(text="Добавить тему", callback_data="get_topic")],
               [InlineKeyboardButton(text="Удалить", callback_data="deleted_topic")],
               [InlineKeyboardButton(text="Выбрать", callback_data="confirm")],
               [InlineKeyboardButton(text="Основное меню", callback_data="cancel")]]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard
