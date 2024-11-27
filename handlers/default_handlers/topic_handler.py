import traceback
from pydoc_data.topics import topics
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config_data.config import CHAT_ID
from loger.logger_helper import get_logger
from keyboards.inline.inline_config import topic_chice
from states.states_bot import Topic, Form, Builder
from utils.utils_custom import delete_from_json, load_from_json, save_to_json
from config_data.config import FILE_TOPIC, FILE_INFO
from aiogram.filters import Command


file_info = FILE_INFO
file_topic = FILE_TOPIC
router = Router()
log = get_logger(__name__)
chat_id = CHAT_ID

text = "Выберете действие"
async def topic_set(message: Message):
    kb_done = await topic_chice()
    await message.answer(text, reply_markup=kb_done)
    await message.delete()




@router.callback_query(Command("topic_menu"), Form.admin_true)
@router.callback_query(F.data == "topic")
async def menu_topic(callback: CallbackQuery, state: FSMContext):
    await topic_set(callback.message)
    await state.set_state(Topic.menu)


@router.callback_query(F.data == "get_topic")
@router.message(Command("topics"), Form.admin_true)
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
    await callback.message.answer("Введите: 'название темы'|'ссылка на тему'\n"
                                  "Для возвращения в меню темы введите 'Готово'")
    await state.set_state(Topic.menu)
    await callback.message.delete()


@router.message(Topic.menu, Topic.choice)
async def get_topic(message: Message, state: FSMContext):
    text = message.text
    if text.lower() == "готово":
        await topic_set(message)
        await state.set_state(Topic.menu)
    else:
        lst = text.split('|')
        if len(lst) != 2:
            await message.answer("Неправильный формат. Попробуйте еще раз ввести 'название темы'|'ссылка на тему'")
            return

        try:
            topic_name, topic_url = lst

            data = {topic_name: {"url": topic_url}}
            big_data = await load_from_json("topic.json")
            if big_data.get(topic_name):
                await message.reply(f"Тема: {topic_name} уже существует")
                return
            big_data.update(data)
            await save_to_json(big_data, "topic.json")
            await message.answer(f"Тема: {topic_name} принята")
            await state.set_state(Topic.menu)

        except Exception as e:
            log.error(f"Возникла ошибка: {e}\nТрассировка:\n{traceback.format_exc()}")
            await message.answer("Произошла ошибка при обработке вашей темы.")


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
        data = await load_from_json("topic.json")
        if data is None:
            await callback.message.answer("Темы не найдены.")
            return
        log.debug(f"Для просмотра тем получены данные: {data}")
        response = "Список тем:\n"
        for topic in data:
            log.debug(f"сообщение {topic}")
            response += f"{topics}| url\n"
            await callback.message.answer(response)
    except Exception as e:
        log.error(f"Возникла ошибка: {e}\nТрассировка:\n{traceback.format_exc()}")


@router.callback_query(Topic.menu)
@router.callback_query(F.data == "confirm")
async def choose_topic_for_deletion(callback: CallbackQuery, state: FSMContext):
    """
    Обрабатывает нажатие кнопки "delete_topic".

    Загружает список тем из JSON-файла и предлагает пользователю выбрать
    тему для удаления. Если темы не найдены, уведомляет об этом.

    Args:
        callback (CallbackQuery): Объект обратного вызова, содержащий информацию о нажатой кнопке.
    """
    log.info("Пользователь выбрал 'viewing_topic'.")
    topics = await load_from_json("topic.json")
    if not topics:
        await callback.message.answer("Темы не найдены.")
        return

    builder = InlineKeyboardBuilder()
    for topic in topics.keys():
        msg = ''
        if callback.data == "deleted_topic":
            msg = f"confirm_delete_{topic}"

        elif callback.data == f"confirm":
            msg = f"confirm_topic_{topic}"

        builder.button(text=topic, callback_data=msg)
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
            success = await delete_from_json(topic, "topic.json")
            if success:
                await callback.message.answer(f"Тема '{topic}' успешно удалена.")
                await topic_set(callback.message)
        else:
            topic = callback.data[len("confirm_topic_"):]
            success = await load_from_json(topic, "topic.json")
            id_topic = success.split('/')[-1]
            await state.update_data(id_topic=id_topic)

            await callback.message.answer(f"Тема {topic} выбрана")
            await state.set_state(Builder.menu)
        await callback.message.delete()
    except Exception as e:
        log.error(f"Возникла ошибка: {e}\nТрассировка:\n{traceback.format_exc()}")
        await callback.message.answer("Не удалось выполнить действие")


