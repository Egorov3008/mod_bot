import sqlite3
import traceback
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config_data.config import CHAT_ID
from loger.logger_helper import get_logger
from keyboards.inline.inline_config import topic_choice
from states.states_bot import Topic, Form, Builder

from config_data.config import FILE_TOPIC, FILE_INFO
from aiogram.filters import Command
from database.data_db import TopicsChat, insert_topic

file_info = FILE_INFO
file_topic = FILE_TOPIC
router = Router()
log = get_logger(__name__)
chat_id = CHAT_ID

text = "Выберете действие"
conn = sqlite3.connect('bot_data.db')


async def topic_set(message: Message, state: FSMContext):
    kb_done = await topic_choice()
    await message.answer(text, reply_markup=kb_done)
    await get_state(state)
    await message.delete()


async def get_state(state: FSMContext):
    current_state = await state.get_state()
    log.debug(f"Статус {current_state}")


@router.callback_query(F.data == "topic")
async def menu_topic(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Topic.menu)
    await topic_set(callback.message, state)


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
    await state.set_state(Topic.add)
    await get_state(state)
    log.info("Пользователь выбрал 'get_topic'.")
    await callback.message.answer("Введите: 'название темы'|'ссылка на тему'\n"
                                  "Для возвращения в меню темы введите 'Готово'")


@router.message(Topic.add)
async def get_topic(message: Message, state: FSMContext):
    text = message.text
    log.debug(f"Получено сообщение {text}")
    if text.lower() == "готово":
        await state.set_state(Topic.menu)
        await topic_set(message, state)
        log.debug("Установленно состояние Topic.menu")
        return
    else:
        lst = text.split('|')
        if len(lst) != 2:
            await message.answer("Неправильный формат. Попробуйте еще раз ввести 'название темы'|'ссылка на тему'")
            return

        try:
            topic_name, topic_url = lst
            exists = TopicsChat.get_or_none(TopicsChat.name_topic == topic_name)

            if exists:
                await message.reply(f"Тема: {topic_name} уже существует")
                await topic_set(message, state)
                return
            insert_topic(topic_name, int(topic_url[-1]), chat_id)
            await message.answer(f"Тема: {topic_name} принята\n"
                                 f"Введите 'ГОТОВО', если закончили ввод")
            await state.set_state(Topic.add)
            await get_state(state)

        except Exception as e:
            log.error(f"Возникла ошибка: {e}\nТрассировка:\n{traceback.format_exc()}")
            await message.answer("Произошла ошибка при обработке вашей темы.")
            await state.set_state(Topic.menu)
            await topic_set(message, state)


@router.callback_query(F.data == "view_topics", Topic.menu)
async def view_topics(callback: CallbackQuery, state: FSMContext):
    """
    Обрабатывает нажатие кнопки "Просмотр тем".

    Загружает список тем из JSON-файла и отправляет его пользователю.
    Если темы не найдены, уведомляет об этом.

    Args:
        callback (CallbackQuery): Объект обратного вызова, содержащий информацию о нажатой кнопке.
    """

    try:
        await state.set_state(Topic.view_topics)
        await get_state(state)
        topicsChat = TopicsChat.select()
        if topicsChat is None:
            await callback.message.answer("Темы не найдены.")
            return
        log.debug(f"Для просмотра тем данные получены")
        response = "Список тем:\n"
        for topic in topicsChat:
            log.debug(f"сообщение {topic.name_topic}")
            response += f"{topic.name_topic}\n"
        await callback.message.answer(response)
        await state.set_state(Topic.menu)
        await topic_set(callback.message, state)
    except Exception as e:
        log.error(f"Возникла ошибка: {e}\nТрассировка:\n{traceback.format_exc()}")
        await topic_set(callback.message, state)


@router.callback_query(F.data == "confirm", Builder.menu)
@router.callback_query(F.data == "deleted_topic", Topic.menu)
async def choose_topic_for_deletion(callback: CallbackQuery, state: FSMContext):
    """
    Обрабатывает нажатие кнопки "delete_topic".

    Загружает список тем из JSON-файла и предлагает пользователю выбрать
    тему для удаления. Если темы не найдены, уведомляет об этом.

    Args:
        callback (CallbackQuery): Объект обратного вызова, содержащий информацию о нажатой кнопке.
    """
    log.info(f"Пользователь выбрал {callback.data}.")
    topics = TopicsChat.select()
    if topics is None:
        await callback.message.answer("Темы не найдены.")
        return

    builder = InlineKeyboardBuilder()
    for line in topics:

        if callback.data == "deleted_topic":
            builder.button(text=line.name_topic, callback_data=f"confirm_delete_{line.name_topic}")
            await state.set_state(Topic.delete)
            await get_state(state)

        elif callback.data == f"confirm":
            builder.button(text=line.name_topic, callback_data=f"confirm_topic_{line.name_topic}")
            await state.set_state(Builder.choice_topic)
            await get_state(state)
    builder.adjust(1)

    await callback.message.answer("Выберите тему:", reply_markup=builder.as_markup())


@router.callback_query(F.data.startswith("confirm_"))
async def confirm_delete_topic(callback: CallbackQuery, state: FSMContext):
    """
    Подтверждает удаление темы.

    Извлекает название темы из данных обратного вызова и пытается удалить
    её из JSON-файла. Уведомляет пользователя об успешности операции.

    Args:
        callback (CallbackQuery): Объект обратного вызова, содержащий информацию о нажатой кнопке.
    """
    try:
        if callback.data.startswith("confirm_delete_"):
            topic = callback.data[len("confirm_delete_"):]
            log.debug(f"Удаление темы: {topic}")
            query = TopicsChat.delete().where(TopicsChat.name_topic == topic)
            query.execute()  # Выполнение запроса на удаление
            log.info(f"Тема {topic} удалена.")
            await callback.message.answer(f"Тема '{topic}' успешно удалена.")
            await state.set_state(Topic.menu)
            await topic_set(callback.message, state)
        else:
            topic = callback.data[len("confirm_topic_"):]
            topics_db = TopicsChat.get(TopicsChat.name_topic == topic)
            value = topics_db.topic_id
            if value:
                log.debug(f"Данные получены")
                await state.update_data(id_topic=value)
                await callback.message.answer(f"Тема {topic} выбрана")
                await state.set_state(Builder.menu)
                await get_state(state)
            else:
                log.debug("Что-то пошло не так")

        await callback.message.delete()
    except Exception as e:
        log.error(f"Возникла ошибка: {e}\nТрассировка:\n{traceback.format_exc()}")
        await callback.message.answer("Не удалось выполнить действие")
        await topic_set(callback.message, state)
