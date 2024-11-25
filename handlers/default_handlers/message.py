import datetime
from aiogram import Router, F
from aiogram.enums import ContentType
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from loger.logger_helper import get_logger
from keyboards.inline.inline_config import kb_url, choice_filter_done
from states.states_bot import Form, Builder
from handlers.default_handlers.adm_handlers import load_from_json, save_to_json
from config_data.config import CHAT_ID
from utils.utils_custom import choice_from_json

chat_id = CHAT_ID
log = get_logger(__name__)
router = Router()


def is_img_message(message: Message):
    return message.content_type == ContentType.PHOTO



@router.callback_query(F.data == "msg")
async def set_text(callback: CallbackQuery, state: FSMContext):
    log.info("Пользователь выбрал 'msg'.")
    kb = await choice_filter_done()
    await callback.message.answer("Выберете элементы", reply_markup=kb)
    await state.set_state(Form.msg)


@router.callback_query(F.data, Form.msg)
async def get_msg_elm(callback: CallbackQuery, state: FSMContext):
    log.info(f"Пользователь выбрал элемент: {callback.data}.")
    if callback.data == "text":
        await callback.message.answer("Введите текст")
        await state.set_state(Builder.get_text)
    elif callback.data == "img":
        await callback.message.answer("Загрузите картинку")
        await state.set_state(Builder.get_img)
    elif callback.data == "url":
        kb = await kb_url()
        await callback.message.answer("Загрузите ссылку и ее название", reply_markup=kb)
        await state.set_state(Builder.get_url)
    elif callback.data == "time_out":
        await callback.message.answer("Введите время и дату публикации (в формате ГГГГ-ММ-ДД ЧЧ:ММ)")
        await state.set_state(Builder.get_time_start)
    elif callback.data == "time_del":
        await callback.message.answer("Введите время и дату удаления (в формате ГГГГ-ММ-ДД ЧЧ:ММ)")
        await state.set_state(Builder.get_time_del)
    elif callback.data == "choice_topic_add":
        await state.set_state(Builder.choice_topic)
        topics = await load_from_json("topic.json")
        if not topics:
            await callback.message.answer("Темы не найдены.")
            return

        builder = InlineKeyboardBuilder()
        for topic in topics.keys():
            builder.button(text=topic, callback_data=f"choice_add_{topic}")
            builder.adjust(1)
        await callback.message.answer("Выберете тему:", reply_markup=builder.as_markup())
    elif callback.data == "done":
        await state.set_state(Builder.done)
        log.debug("Пользователь завершил ввод сообщения.")
        data = await state.get_data()
        data_time = data.get("time_start")
        await save_to_json(data, "message.json")
        await callback.message.answer(f"Сообщение с датой публикации {data_time} принято")
        data.clear()

    await callback.message.delete()



@router.message(Builder.get_text)
async def process_get_text(message: Message, state: FSMContext):
    log.info("Пользователь ввел текст.")
    await state.update_data(text=message.text)
    kb_done = await choice_filter_done()
    await message.reply("Что-то еще? Если нет, нажмите 'Готово'", reply_markup=kb_done)
    await state.set_state(Form.msg)


@router.message(Builder.get_img, is_img_message)
async def process_get_img(message: Message, state: FSMContext):
    log.info("Пользователь загрузил изображение.")
    await state.update_data(img=message.photo[-1].file_id)
    kb_done = await choice_filter_done()
    await message.reply("Что-то еще? Если нет, нажмите 'Готово'", reply_markup=kb_done)
    await state.set_state(Form.msg)


@router.message(Builder.get_url)
async def process_get_url(message: Message, state: FSMContext):
    data = await state.get_data()
    if 'link_text' not in data:
        log.info("Пользователь ввел текст кнопки для ссылки.")
        await state.update_data(link_text=message.text)
        await message.reply("Теперь введите URL:")
    else:
        log.info("Пользователь ввел URL для кнопки.")
        await state.update_data(link_url=message.text)
        data = await state.get_data()
        link_text = data.get("link_text")
        link_url = data.get("link_url")
        log.debug(f"Переданы следующие параметры: link_text:  {link_text}, link_url: {link_url}")
        await message.answer(f"Параметры приняты.\nНазвание кнопки:  {link_text}\nСсылка: {link_url}")
        kb_done = await choice_filter_done()
        await message.reply("Что-то еще? Если нет, нажмите 'Готово'", reply_markup=kb_done)
        await state.set_state(Form.msg)


@router.callback_query(Builder.get_url)
async def get_name_url(callback: CallbackQuery, state: FSMContext):
    log.info("Пользователь выбрал 'get_url'.")
    await callback.message.reply("Введите название кнопки")
    await state.set_state(Builder.get_url)


@router.callback_query(Builder.get_time_start)
async def get_time_del(callback: CallbackQuery, state: FSMContext):
    log.info("Пользователь выбрал 'get_time_start'.")
    await callback.message.answer("Введите время и дату публикации (в формате ГГГГ-ММ-ДД ЧЧ:ММ):")
    await state.set_state(Builder.get_time_start)


@router.message(Builder.get_time_start)
async def process_get_time_start(message: Message, state: FSMContext):
    log.info("Пользователь ввел время и дату публикации.")
    try:
        time_start = datetime.datetime.strptime(message.text, "%Y-%m-%d %H:%M")
        await state.update_data(time_start=time_start)
        await message.answer("Время принято")
        kb_done = await choice_filter_done()
        await message.reply("Что-то еще? Если нет, нажмите 'Готово'", reply_markup=kb_done)
        await state.set_state(Form.msg)
    except ValueError:
        log.error("Неправильный формат времени для публикации.")
        await message.reply("Неправильный формат времени. Попробуйте еще раз.")
        await state.set_state(Builder.get_time_start)


@router.callback_query(Builder.get_time_del)
async def get_time_del(callback: CallbackQuery, state: FSMContext):
    log.info("Пользователь выбрал 'get_time_del'.")
    await callback.message.answer("Введите время и дату удаления (в формате ГГГГ-ММ-ДД ЧЧ:ММ):")
    await state.set_state(Builder.get_time_del)


@router.message(Builder.get_time_del)
async def process_get_time_del(message: Message, state: FSMContext):
    log.info("Пользователь ввел время и дату удаления.")
    try:
        time_del = datetime.datetime.strptime(message.text, "%Y-%m-%d %H:%M")
        await state.update_data(time_del=time_del)
        await message.reply("Время принято")
        kb_done = await choice_filter_done()
        await message.reply("Что-то еще? Если нет, нажмите 'Готово'", reply_markup=kb_done)
        await state.set_state(Form.msg)
    except ValueError:
        log.error("Неправильный формат времени для удаления.")
        await message.reply("Неправильный формат времени. Попробуйте еще раз.")
        await state.set_state(Builder.get_time_del)


@router.callback_query(F.data.startswith("choice_add_"))
async def confirm_delete_topic(callback: CallbackQuery, state: FSMContext):
    topic = callback.data[len("choice_add_"):]
    success = await choice_from_json(topic, "topic.json")
    if success:
        await callback.message.reply(f"Тема успешно выбрана.")
        log.debug(f"Выбрана тема с ссылкой {topic}")
        id_topic = topic.split('/')[-1]
        await state.update_data(id_topic=id_topic)
        kb_done = await choice_filter_done()
        await callback.message.answer("Что-то еще? Если нет, нажмите 'Готово'", reply_markup=kb_done)
        await state.set_state(Form.msg)
    else:
        await callback.message.answer(f"Не удалось выбрать тему '{topic}'. Возможно, она не существует.")
