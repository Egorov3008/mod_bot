import json
import aiofiles
from aiogram.enums import ChatMemberStatus
from aiogram.filters import Command, CommandStart
from aiogram import Router, F, exceptions
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from loger.logger_helper import get_logger
from loader import bot
from config_data.config import CHAT_ID
from states.states_bot import Form, Topic
from keyboards.inline.inline_config import choice, topic_kb

log = get_logger(__name__)
router = Router()
chat_id = CHAT_ID


async def save_to_json(data, name_file):
    try:
        async with aiofiles.open(name_file, mode='r', encoding='utf-8') as f:
            contents = await f.read()
            if contents.strip():  # Проверка на пустое содержимое
                existing_data = json.loads(contents)
            else:
                existing_data = {}
    except (FileNotFoundError, json.JSONDecodeError) as e:
        log.error(f"Произошла ошибка при чтении файла: {e}")
        existing_data = {}

    # Обновляем существующие данные новыми
    for key, value in data.items():
        existing_data[key] = value

    try:
        # Запись обновленных данных в файл
        async with aiofiles.open(name_file, mode='w', encoding='utf-8') as f:
            await f.write(json.dumps(existing_data, indent=4, ensure_ascii=False))
            log.debug("Данные сохранны")
    except Exception as e:
        log.error(f"Произошла ошибка при записи файла: {e}")


async def load_from_json(name_file):
    try:
        async with aiofiles.open(name_file, mode='r', encoding='utf-8') as f:
            contents = await f.read()
            if contents.strip():
                return json.loads(contents)
            return {}
    except (FileNotFoundError, json.JSONDecodeError) as e:
        log.error(f"Произошла ошибка при чтении файла: {e}")
        return {}


async def delete_from_json(key, name_file):
    try:
        async with aiofiles.open(name_file, mode='r', encoding='utf-8') as f:
            contents = await f.read()
            if contents.strip():
                data = json.loads(contents)
            else:
                data = {}
    except (FileNotFoundError, json.JSONDecodeError) as e:
        log.error(f"Произошла ошибка при чтении файла: {e}")
        return False

    if key in data:
        del data[key]
        try:
            async with aiofiles.open(name_file, mode='w', encoding='utf-8') as f:
                await f.write(json.dumps(data, indent=4, ensure_ascii=False))
            return True
        except Exception as e:
            log.error(f"Произошла ошибка при записи файла: {e}")
            return False
    return False


@router.message(CommandStart())
async def start_bot(message: Message, state: FSMContext):
    try:
        admins = await get_group_admins()
        user = message.from_user
        status = await check_checking_admin_rights()
        if user.id in admins and status:
            kb = await choice()
            await state.set_state(Form.admin_true)
            await message.answer(f"Привет {user.first_name}! Я готов к работе\n"
                                 f"Выбери действие", reply_markup=kb)
        elif user.id in admins:
            await message.answer(f"Привет {user.first_name}! Вы должны сделать меня админом в группе")
    except Exception as e:
        await message.answer("Что-то пошло не так 🤷‍♂️\n"
                             "Возможно меня нет в Вашей группе")


async def get_group_admins(chat_id: int = CHAT_ID):
    try:
        admins = await bot.get_chat_administrators(chat_id)
        list_admins_id = [adm.user.id for adm in admins]
        return list_admins_id
    except Exception as e:
        log.error(f"Что-то пошло не так {e}")


async def check_checking_admin_rights(chat_id: int = CHAT_ID):
    try:
        bot_user = await bot.get_me()
        bot_member = await bot.get_chat_member(chat_id, bot_user.id)
        if bot_member.status == ChatMemberStatus.ADMINISTRATOR:
            return True
        return False
    except Exception as e:
        log.error(f"Возникла ошибка {str(e)}")


@router.message(Command("check_bot_rights"))
async def check_bot_rights(message: Message, chat_id: int = CHAT_ID):
    try:
        bot_user = await bot.get_me()
        chat = await bot.get_chat(chat_id)
        try:
            bot_member = await bot.get_chat_member(chat_id, bot_user.id)
            if bot_member:
                await message.reply(f"Права бота в чате {chat.title}:")
                if bot_member.status == ChatMemberStatus.ADMINISTRATOR:
                    await message.answer("Я являюсь администратором в этом чате.")
                elif bot_member.status == ChatMemberStatus.MEMBER:
                    await message.answer("Я являюсь обычным участником в этом чате.")
                else:
                    await message.answer("Неизвестный статус бота в этом чате.")
        except Exception as e:
            log.error(f"Ошибка при проверке прав бота: {e}")
            await message.reply("Не удалось проверить права бота в этом чате.")
    except exceptions.TelegramForbiddenError as e:
        await message.reply(f"Бот не состоит в группе")


@router.callback_query(F.data == "topic")
async def topic_menu(callback: CallbackQuery, state: FSMContext):
    kb = await topic_kb()
    await callback.message.answer("Выберите действие", reply_markup=kb)
    await state.set_state(Topic.menu)



@router.callback_query(F.data == "get_topic")
async def set_topic(callback: CallbackQuery, state: FSMContext):
    log.info("Пользователь выбрал 'get_topic'.")
    await callback.message.answer("Введите: 'название темы'|'ссылка на тему'")
    await state.set_state(Topic.menu)


@router.message(Topic.menu)
async def get_topic(message: Message, state: FSMContext):
    text = message.text
    lst = text.split('|')
    if len(lst) != 2:
        await message.answer("Неправильный формат. Попробуйте еще раз ввести 'название темы'|'ссылка на тему'")
        return

    try:
        topic_name, topic_url = lst
        data = {topic_name: topic_url}
        await save_to_json(data, "topic.json")
        await message.answer(f"Тема: {topic_name} принята")
    except Exception as e:
        log.error(f"Что-то пошло не так: {e}")
        await message.answer("Произошла ошибка при сохранении темы. Попробуйте еще раз.")
        await state.set_state(Topic.menu)


@router.callback_query(F.data == "view_topics")
async def view_topics(callback: CallbackQuery):
    log.info("Пользователь выбрал 'view_topics'.")
    topics = await load_from_json("topic.json")
    if not topics:
        await callback.message.answer("Темы не найдены.")
        return

    response = "Список тем:\n"
    for topic, url in topics.items():
        response += f"{topic}: {url}\n"

    await callback.message.answer(response)


@router.callback_query(F.data == "delete_topic")
async def choose_topic_for_deletion(callback: CallbackQuery):
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
    topic = callback.data[len("confirm_delete_"):]
    success = await delete_from_json(topic, "topic.json")
    if success:
        await callback.message.answer(f"Тема '{topic}' успешно удалена.")
    else:
        await callback.message.answer(f"Не удалось удалить тему '{topic}'. Возможно, она не существует.")


@router.callback_query(F.data == "choice_topic")
async def choose_topic_for_deletion(callback: CallbackQuery):
    log.info("Пользователь выбрал 'choice_topic'.")
    topics = await load_from_json("topic.json")
    if not topics:
        await callback.message.answer("Темы не найдены.")
        return

    builder = InlineKeyboardBuilder()
    for topic in topics.keys():
        builder.button(text=topic, callback_data=f"choice_{topic}")
    builder.adjust(1)

    await callback.message.answer("Выберите тему:", reply_markup=builder.as_markup())


@router.callback_query(F.data.startswith("confirm_delete_"))
async def confirm_delete_topic(callback: CallbackQuery):
    topic = callback.data[len("confirm_delete_"):]
    success = await delete_from_json(topic, "topic.json")
    if success:
        await callback.message.answer(f"Тема '{topic}' успешно удалена.")
    else:
        await callback.message.answer(f"Не удалось удалить тему '{topic}'. Возможно, она не существует.")
