import datetime
from aiogram.filters import Command

from aiogram import Router, F
from aiogram.enums import ContentType
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from loger.logger_helper import get_logger
from keyboards.inline.inline_config import kb_url, choice_filter_done
from states.states_bot import Form, Builder
from config_data.config import CHAT_ID
from utils.utils_custom import load_from_json, save_to_json

chat_id = CHAT_ID
log = get_logger(__name__)
router = Router()
text = "Если сообщение сформировано, нажми ГОТОВО"


async def gone_set(message: Message):
    kb_done = await choice_filter_done()
    await message.answer(text, reply_markup=kb_done)
    await message.delete()


def is_img_message(message: Message):
    return message.content_type == ContentType.PHOTO


@router.message(Command("schedule_message"), Form.admin_true)
@router.callback_query(F.data == "msg")
async def set_text(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    log.info("Пользователь выбрал 'schedule_message'.")
    kb = await choice_filter_done()
    await callback.message.answer("Выберете элементы", reply_markup=kb)
    await state.set_state(Builder.menu)


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
        kb = await kb_url()
        await callback.message.answer("Загрузите ссылку и ее название", reply_markup=kb)
        await state.set_state(Builder.get_url)
    elif callback.data == "time_out":
        await callback.message.answer("Введите время и дату публикации (в формате ГГГГ-ММ-ДД ЧЧ:ММ)")
        await state.set_state(Builder.get_time_start)
    elif callback.data == "time_del":
        await callback.message.answer("Введите время и дату удаления (в формате ГГГГ-ММ-ДД ЧЧ:ММ)")
        await state.set_state(Builder.get_time_del)
    elif callback.data == "message preview":

        await preview(callback.message, state)
        await state.set_state(Builder.preview)



async def preview(message: Message, state: FSMContext):
    data = await state.get_data()

    # Формируем сообщение о принятых данных
    msg = "Приняты следующие данные:\n"
    data_msg = {
        "Время публикации": data.get("time_start"),
        "Время удаления": data.get("time_del"),
        "Текст": data.get("text"),
        "Картинка": data.get("img"),
        "Название кнопки": data.get("link_text"),
        "Ссылка": data.get("link_url"),
        "Id_topic": data.get("id_topic")
    }

    # Добавляем информацию о данных в сообщение
    for key, value in data_msg.items():
        if key != "Картинка":
            msg += f"{key}: {value}\n"

    # Проверяем наличие картинки и отправляем соответствующее сообщение
    if data_msg.get("Картинка"):
        # Если есть id картинки, отправляем изображение
        file_id = data_msg.get("Картинка")
        await message.answer_photo(photo=file_id, caption=msg)
    else:
        # Отправляем сообщение без изображения
        await message.answer(msg)

    # Проверяем наличие ссылки и создаем кнопку
    if data_msg.get("link_url"):
        button_text = data_msg.get("link_text")
        button = [[InlineKeyboardButton(text=button_text, url=data_msg["link_url"])]]
        keyboard = InlineKeyboardMarkup(inline_keyboard=button)
        keyboard.add(button)

        # Отправляем сообщение с кнопкой, если есть ссылка
        await message.answer(msg, reply_markup=keyboard)




@router.message(Builder.get_text)
async def process_get_text(message: Message, state: FSMContext):
    log.info("Пользователь ввел текст.")
    await state.update_data(text=message.text)

    await gone_set(message)
    await state.set_state(Builder.menu)


@router.message(Builder.get_img, is_img_message)
async def process_get_img(message: Message, state: FSMContext):
    log.info("Пользователь загрузил изображение.")
    await state.update_data(img=message.photo[-1].file_id)

    await gone_set(message)
    await state.set_state(Builder.menu)


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
        await gone_set(message)
        await state.set_state(Builder.menu)


@router.callback_query(Builder.get_url)
async def get_name_url(callback: CallbackQuery, state: FSMContext):
    log.info("Пользователь выбрал 'get_url'.")
    await callback.message.reply("Введите название кнопки")
    await state.set_state(Builder.get_url)


@router.message(Builder.get_time_start)
async def process_get_time_start(message: Message, state: FSMContext):
    log.info("Пользователь ввел время и дату публикации.")
    try:
        time_start = datetime.datetime.strptime(message.text, "%Y-%m-%d %H:%M")
        await state.update_data(time_start=time_start)
        await message.answer("Время принято")
        await gone_set(message)
        await state.set_state(Form.msg)
    except ValueError:
        log.error("Неправильный формат времени для публикации.")
        await message.reply("Неправильный формат времени. Попробуйте еще раз.")
        await state.set_state(Builder.get_time_start)


@router.message(Builder.get_time_del)
async def process_get_time_del(message: Message, state: FSMContext):
    log.info("Пользователь ввел время и дату удаления.")
    try:
        time_del = datetime.datetime.strptime(message.text, "%Y-%m-%d %H:%M")
        await state.update_data(time_del=time_del)
        await message.reply("Время принято")
        await gone_set(message)
        await state.set_state(Builder.menu)
    except ValueError:
        log.error("Неправильный формат времени для удаления.")
        await message.reply("Неправильный формат времени. Попробуйте еще раз.")
        await state.set_state(Builder.get_time_del)
