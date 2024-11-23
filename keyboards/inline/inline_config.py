from datetime import datetime, timedelta
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime, timedelta
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


# def format_date(option: str) -> str:
#     """
#     Форматирует дату в зависимости от переданного параметра.
#
#     :param option: Строка, указывающая, какую дату нужно сформатировать.
#                    Возможные значения: 'сегодня', 'вчера', 'неделя', 'месяц'.
#     :return: Строка с диапазоном дат в формате 'YYYY-MM-DD - YYYY-MM-DD'.
#     """
#     global data
#     today = datetime.now()
#
#     if option.lower() == 'сегодня':
#         data = f"{today.strftime('%Y-%m-%d')} - {today.strftime('%Y-%m-%d')}"
#     elif option.lower() == 'вчера':
#         yesterday = today - timedelta(days=1)
#         data = f"{yesterday.strftime('%Y-%m-%d')} - {yesterday.strftime('%Y-%m-%d')}"
#     elif option.lower() == 'неделя':
#         start_of_week = today - timedelta(days=7)
#         end_of_week = today
#         data = f"{start_of_week.strftime('%Y-%m-%d')} - {end_of_week.strftime('%Y-%m-%d')}"
#     elif option.lower() == 'месяц':
#         start_of_month = today - timedelta(days=30)
#         end_of_month = today
#         data = f"{start_of_month.strftime('%Y-%m-%d')} - {end_of_month.strftime('%Y-%m-%d')}"
#
#     return data


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


async def choice_filter() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с выбором действий.

    :return: Объект InlineKeyboardMarkup с кнопками.
    """
    buttons = [
        [InlineKeyboardButton(text="Изменить текст", callback_data="text"),
         InlineKeyboardButton(text="Медиа+", callback_data="img")],
        [InlineKeyboardButton(text="Ссылка", callback_data="url"),
         InlineKeyboardButton(text="Время отправки", callback_data="time_out")],
        [InlineKeyboardButton(text="Время удаления", callback_data="time_del"),
         InlineKeyboardButton(text="Выбор темы", callback_data="choice_topic_add")]
    ]
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
        [InlineKeyboardButton(text="Выбор темы", callback_data="choice_topic_add")],
        [InlineKeyboardButton(text="Готово", callback_data="done")],
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


async def topic_kb() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с выбором действий.

    :return: Объект InlineKeyboardMarkup с кнопками.
    """
    buttons = [[InlineKeyboardButton(text="Добавить тему", callback_data="get_topic")],
               [InlineKeyboardButton(text="Просмотр тем", callback_data="view_topics")],
               [InlineKeyboardButton(text="Выбор темы", callback_data="choice_topic")]]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

