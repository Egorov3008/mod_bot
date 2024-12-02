import datetime
import traceback
from aiogram.filters import Command
from aiogram import Router, F
from aiogram.enums import ContentType
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from loger.logger_helper import get_logger
from keyboards.inline.inline_config import choice_filter_done, msg_choice, choice
from states.states_bot import Form, Builder
from config_data.config import CHAT_ID
from database.data_db import insert_message

chat_id = CHAT_ID
log = get_logger(__name__)
router = Router()
text = "Если сообщение сформировано, нажми ПРЕДПРОСМОТР СООБЩЕНИЯ"


async def get_state(state: FSMContext):
    current_state = await state.get_state()
    log.debug(f"Статус {current_state}")


async def gone_set(message: Message, state: FSMContext):
    kb_done = await choice_filter_done()
    await message.answer(text, reply_markup=kb_done)
    await get_state(state)


def is_img_message(message: Message):
    return message.content_type == ContentType.PHOTO


@router.message(Command("schedule_message"), Form.admin_true)
@router.callback_query(F.data == "msg", Form.admin_true)
async def set_text(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    log.info("Пользователь выбрал 'schedule_message'.")
    kb = await choice_filter_done()
    await callback.message.answer("Выберете элементы", reply_markup=kb)
    await state.set_state(Builder.menu)
    await get_state(state)


@router.callback_query(F.data, Builder.menu)
async def get_msg_elm(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    log.info(f"Пользователь выбрал элемент: {callback.data}.")
    if callback.data == "text":
        await callback.message.answer("Введите текст")
        await state.set_state(Builder.get_text)
    elif callback.data == "img":
        await callback.message.answer("Загрузите картинку")
        await state.set_state(Builder.get_img)
    elif callback.data == "url":
        await callback.message.answer("Введите: 'название кнопки'|'ссылка для кнопки'\n")
        await state.set_state(Builder.get_url)
    elif callback.data == "time_out":
        await callback.message.answer("Введите время и дату публикации (в формате ГГГГ-ММ-ДД ЧЧ:ММ)")
        await state.set_state(Builder.get_time_start)
    elif callback.data == "time_del":
        await callback.message.answer("Введите время и дату удаления (в формате ГГГГ-ММ-ДД ЧЧ:ММ)")
        await state.set_state(Builder.get_time_del)
    elif callback.data == "message_preview":
        await preview(callback.message, state)
    elif callback.data == "done":
        try:
            data = await state.get_data()

            insert_message(text=data.get("text"), img=data.get("img"),
                           link_text=data.get("link_text"), link_url=data.get("link_url"),
                           time_start=data.get("time_start"), time_del=data.get("time_del"), topic_id=data.get("id_topic"),
                           chat_id=chat_id)

            await callback.message.answer("Сообщение сформировано")
            await state.set_state(Builder.menu)
        except Exception as e:
            log.error(f"Возникла ошибка: {e}\nТрассировка:\n{traceback.format_exc()}")
            await callback.message.answer(f"Что-то пошло не так((( {e}")
    elif callback.data == "deleted_data":
        await state.clear()
        kb = await choice()
        await callback.message.answer("Сообщение удалено.\nВыберете пункт", reply_markup=kb)
    await get_state(state)


async def preview(message: Message, state: FSMContext):
    data = await state.get_data()
    data_msg = {
        "Время публикации": data.get("time_start"),
        "Время удаления": data.get("time_del"),
        "Текст": data.get("text"),
        "Картинка": data.get("img"),
        "Название кнопки": data.get("link_text"),
        "Ссылка": data.get("link_url"),
        "Id_topic": data.get("id_topic")
    }
    msg = "Приняты следующие данные:\n"

    log.debug(f"Добавляем информацию о данных в сообщение {data}")
    for key, value in data_msg.items():
        if key != "Картинка":
            msg += f"{key}: {value}\n"

    log.debug(f"Проверяем наличие картинки и отправляем соответствующее сообщение ")
    if data_msg.get("Картинка"):
        log.debug("Есть id картинки, отправляем изображение")
        file_id = data_msg.get("Картинка")
        await message.answer_photo(photo=file_id, caption=msg)
    else:
        # Отправляем сообщение без изображения
        await message.answer(msg)

    kb = await msg_choice()
    await message.answer("Выберете действие:", reply_markup=kb)


@router.message(Builder.get_text)
async def process_get_text(message: Message, state: FSMContext):
    log.info("Пользователь ввел текст.")
    await state.update_data(text=message.text)
    await message.reply("Сообщение принято")

    await state.set_state(Builder.menu)
    await gone_set(message, state)


@router.message(Builder.get_img, is_img_message)
async def process_get_img(message: Message, state: FSMContext):
    log.info("Пользователь загрузил изображение.")
    await state.update_data(img=message.photo[-1].file_id)
    await message.reply("Картинка принята")
    await state.set_state(Builder.menu)
    await gone_set(message, state)


@router.message(Builder.get_url)
async def get_topic(message: Message, state: FSMContext):
    text = message.text
    log.debug(f"Получено сообщение {text}")
    lst = text.split('|')
    if len(lst) != 2:
        await message.answer("Неправильный формат. Попробуйте еще раз ввести 'название темы'|'ссылка на тему'")
        return
    try:
        name_kb, kb_url = lst
        await state.update_data(link_text=name_kb)
        await state.update_data(link_url=kb_url)
        await message.answer(f"Название кнопки: {name_kb}\n"
                             f"Ссылка кнопки: {kb_url}. Приняты!"
                             )
        await state.set_state(Builder.menu)
        await gone_set(message, state)
    except Exception as e:
        log.error(f"Возникла ошибка: {e}\nТрассировка:\n{traceback.format_exc()}")
        await message.answer("Что-то пошло не так!")
        await state.set_state(Builder.menu)
        await get_state(state)


@router.callback_query(Builder.get_url)
async def get_name_url(callback: CallbackQuery, state: FSMContext):
    log.info("Пользователь выбрал 'get_url'.")
    await callback.message.reply("Введите название кнопки")
    await state.set_state(Builder.get_url)


@router.message(Builder.get_time_start)
async def process_get_time_start(message: Message, state: FSMContext):
    log.info("Пользователь ввел время и дату публикации.")
    try:
        text_time = message.text + ":00"
        time_start = datetime.datetime.strptime(text_time, "%Y-%m-%d %H:%M:%S")
        await state.update_data(time_start=time_start)
        await message.answer("Время принято")
        await state.set_state(Builder.menu)
        await gone_set(message, state)

    except ValueError:
        log.error("Неправильный формат времени для публикации.")
        await message.reply("Неправильный формат времени. Попробуйте еще раз.")
        await state.set_state(Builder.get_time_start)


@router.message(Builder.get_time_del)
async def process_get_time_del(message: Message, state: FSMContext):
    log.info("Пользователь ввел время и дату удаления.")
    try:
        text_time = message.text + ":00"
        time_del = datetime.datetime.strptime(text_time, "%Y-%m-%d %H:%M:%S")
        await state.update_data(time_del=time_del)
        await message.reply("Время принято")
        await state.set_state(Builder.menu)
        await gone_set(message, state)

    except ValueError:
        log.error("Неправильный формат времени для удаления.")
        await message.reply("Неправильный формат времени. Попробуйте еще раз.")
        await state.set_state(Builder.get_time_del)
