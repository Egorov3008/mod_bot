import traceback
from pydoc_data.topics import topics

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from loader import bot
from config_data.config import CHAT_ID
from handlers.default_handlers.adm_handlers import get_group_admins
from loger.logger_helper import get_logger
from keyboards.inline.inline_config import topic_kb
from states.states_bot import Topic
from utils.utils_custom import delete_from_json, load_from_json, save_to_json

router = Router()
log = get_logger(__name__)
chat_id = CHAT_ID


@router.callback_query(F.data == "topic")
async def topic_menu(callback: CallbackQuery, state: FSMContext):
    """
    Обрабатывает нажатие кнопки "Темы чата" в меню.

    Отправляет пользователю клавиатуру с действиями, связанными с темами,
    и устанавливает состояние машины состояний в Topic.menu.

    Args:
        callback (CallbackQuery): Объект обратного вызова, содержащий информацию о нажатой кнопке.
        state (FSMContext): Контекст состояния для управления состояниями пользователя.
    """
    kb = await topic_kb()
    await callback.message.answer("Выберите действие", reply_markup=kb)
    await state.set_state(Topic.menu)


@router.callback_query(F.data == "get_topic")
async def set_topic(callback: CallbackQuery, state: FSMContext):
    """
    Обрабатывает нажатие кнопки "Добавить тему".

    Запрашивает у пользователя ввод информации о новой теме в формате
    'название темы'|'ссылка на тему' и устанавливает состояние машины состояний
    в Topic.menu.

    Args:
        callback (CallbackQuery): Объект обратного вызова, содержащий информацию о нажатой кнопке.
        state (FSMContext): Контекст состояния для управления состояниями пользователя.
    """
    log.info("Пользователь выбрал 'get_topic'.")
    await callback.message.answer("Введите: 'название темы'|'ссылка на тему'")
    await state.set_state(Topic.menu)


@router.message(Topic.menu)
async def get_topic(message: Message, state: FSMContext):
    """
    ОБНАВЛЕНО
    Обрабатывает сообщение пользователя с информацией о теме.

    Проверяет формат введенного текста, разбивает его на название темы
    и ссылку, сохраняет информацию о теме в JSON-файл и уведомляет
    администраторов о создании новой темы.

    Args:
        message (Message): Сообщение от пользователя, содержащее информацию о теме.
        state (FSMContext): Контекст состояния для управления состояниями пользователя.
    """
    text = message.text
    lst = text.split('|')
    if len(lst) != 2:
        await message.answer("Неправильный формат. Попробуйте еще раз ввести 'название темы'|'ссылка на тему'")
        return

    try:
        topic_name, topic_url = lst
        data = {topic_name: {"url": topic_url}}
        chat_info = await load_from_json("info_chats.json")
        if "Темы чата" not in chat_info:
            chat_info["Темы чата"] = data
            await save_to_json(chat_info, "info_chats.json")
        else:
            data_topic = chat_info.get("Темы чата")
            data_topic.update(data)
            await save_to_json(chat_info, "info_chats.json")
            log.debug(f"Чата с текущем ID: {topic_name} не существует")
        await message.answer(f"Тема: {topic_name} принята")

    except Exception as e:
        log.error(f"Возникла ошибка: {e}\nТрассировка:\n{traceback.format_exc()}")
        await state.set_state(Topic.menu)
    await state.set_state(Topic.menu)


@router.callback_query(F.data == "view_topics")
async def view_topics(callback: CallbackQuery):
    """
    Обрабатывает нажатие кнопки "Просмотр тем".

    Загружает список тем из JSON-файла и отправляет его пользователю.
    Если темы не найдены, уведомляет об этом.

    Args:
        callback (CallbackQuery): Объект обратного вызова, содержащий информацию о нажатой кнопке.
    """

    try:
        data = await load_from_json("info_chats.json")
        if data.get("Темы чата") is None:
            await callback.message.answer("Темы не найдены.")
            return
        topics_info = data.get("Темы чата")
        log.debug(f"Для просмотра тем получены данные: {topics_info}")
        response = "Список тем:\n"
        for topic, info in topics_info.items():
            log.debug(f"сообщение {info}")
            response += f"{topics}: {info['url']}\n"
        await callback.message.answer(response)
    except Exception as e:
        log.error(f"Возникла ошибка: {e}\nТрассировка:\n{traceback.format_exc()}")




@router.callback_query(F.data == "delete_topic")
async def choose_topic_for_deletion(callback: CallbackQuery):
    """
    Обрабатывает нажатие кнопки "delete_topic".

    Загружает список тем из JSON-файла и предлагает пользователю выбрать
    тему для удаления. Если темы не найдены, уведомляет об этом.

    Args:
        callback (CallbackQuery): Объект обратного вызова, содержащий информацию о нажатой кнопке.
    """
    log.info("Пользователь выбрал 'delete_topic'.")
    topics = await load_from_json("topic.json")
    if not topics:
        await callback.message.answer("Темы не найдены.")
        return

    builder = InlineKeyboardBuilder()
    for topic in topics.keys():
        builder.button(text=topic, callback_data=f"confirm_delete_{topic}")
    builder.adjust(1)

    await callback.message.answer("Выберите тему:", reply_markup=builder.as_markup())


@router.callback_query(F.data.startswith("confirm_delete_"))
async def confirm_delete_topic(callback: CallbackQuery):
    """
    Подтверждает удаление темы.

    Извлекает название темы из данных обратного вызова и пытается удалить
    её из JSON-файла. Уведомляет пользователя об успешности операции.

    Args:
        callback (CallbackQuery): Объект обратного вызова, содержащий информацию о нажатой кнопке.
    """
    topic = callback.data[len("confirm_delete_"):]
    success = await delete_from_json(topic, "topic.json")
    if success:
        await callback.message.answer(f"Тема '{topic}' успешно удалена.")
    else:
        await callback.message.answer(f"Не удалось удалить тему '{topic}'. Возможно, она не существует.")
