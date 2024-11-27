import traceback
from aiogram.enums import ChatMemberStatus, ChatType
from aiogram.filters import Command, CommandStart
from aiogram import Router, exceptions, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from keyboards.inline.inline_config import choice
from config_data.config import DEFAULT_COMMANDS
from states.states_bot import Form
from loader import bot
from config_data.config import CHAT_ID
from loger.logger_helper import get_logger

log = get_logger(__name__)
router = Router()
chat_id = CHAT_ID
commads = DEFAULT_COMMANDS


@router.message(CommandStart())
async def start_bot(message: Message, state: FSMContext):
    """
    Обрабатывает команду /start. Проверяет права администратора пользователя
    и отправляет приветственное сообщение с выбором действия.

    :param message: Message - Сообщение, содержащее команду /start.
    :param state: FSMContext - Контекст состояния для работы с состояниями.
    """
    user = message.from_user

    try:
        bot_user = await bot.get_me()
        bot_member = await bot.get_chat_member(chat_id, bot_user.id)
        user_id = message.from_user.id
        user_member = await bot.get_chat_member(chat_id, user_id)
        user_name = user.first_name or user.username
        log.debug(f"Статус бота: {bot_member}")
        log.debug(f"Статус пользователя: {user_member}")

        if (bot_member.status == ChatMemberStatus.ADMINISTRATOR
                and user_member == ChatMemberStatus.ADMINISTRATOR or ChatMemberStatus.CREATOR):
            kb = await choice()
            await message.answer(f"Привет {user_name}! Я готов к работе\n"
                                 f"Зайди в меню 👇", reply_markup=kb)
            await state.set_state(Form.admin_true)

        else:
            await message.answer(f"Привет {user_name}! У кого-то нет прав администратора в чате!\n"
                                 f"Для проверки введи /check_bot_rights")

    except Exception as e:
        log.error(f"Ошибка в start_bot: {e}")
        await message.answer("Что-то пошло не так 🤷‍♂️\n"
                             "Возможно, меня нет в Вашей группе")


@router.message(Command("check_bot_rights"))
async def check_bot_rights(message: Message):
    """
    Обрабатывает команду /check_bot_rights. Проверяет права бота в указанном чате
    и отправляет информацию о статусе бота.

    :param message: Message - Сообщение, содержащее команду.
    """

    try:
        bot_user = await bot.get_me()
        chat = await bot.get_chat(chat_id)
        try:
            bot_member = await bot.get_chat_member(chat_id, bot_user.id)
            if bot_member:
                text = f"Мои права в чате {chat.title}:\n"
                if bot_member.status == ChatMemberStatus.ADMINISTRATOR:
                    text += "Я являюсь администратором в этом чате."
                elif bot_member.status == ChatMemberStatus.MEMBER:
                    text += "Я являюсь обычным участником в этом чате."
                else:
                    text += "Я не смог определить 🤷‍♂️🤷‍♂️"
                await message.answer(text)
        except Exception as e:
            log.error(f"Возникла ошибка: {e}\nТрассировка:\n{traceback.format_exc()}")
            await message.answer("Не удалось проверить права бота в этом чате.")
    except exceptions.TelegramForbiddenError as e:
        log.error(f"Возникла ошибка: {e}\nТрассировка:\n{traceback.format_exc()}")
        await message.answer("Бот не состоит в группе")


@router.message(Command('get_chat_info'))
async def get_chat_info(message: Message):
    """
    Обрабатывает команду /get_chat_info. Получает информацию о чате и
    отправляет её пользователю.

    :param message: Message - Сообщение, содержащее команду.
    """

    global response
    try:
        chat = await bot.get_chat(chat_id)

        if chat.type != ChatType.SUPERGROUP:
            log.debug("Этот чат не является супергруппой.")
            return

        administrators = await bot.get_chat_administrators(chat_id)
        users = [usr.user for usr in administrators]
        log.debug(f"Полученные данные: {users}")
        chat_info = {"Название чата": chat.title, "Тип чата": chat.type,
                     "Количество администраторов": len(administrators), "Администраторы": [
                {
                    "Admin ID": user.id,
                    "Имя администратора": user.full_name,
                    "Username": f"@{user.username}" if hasattr(user, 'username') and user.username else "Нет"
                }
                for user in users
            ]
                     }

        if chat_info:
            response = ""
            chat_name = chat_info["Название чата"]
            chat_type = chat_info["Тип чата"]
            admin_count = chat_info["Количество администраторов"]
            admins = chat_info["Администраторы"]

            # Форматируем сообщение
            response = f"*Название чата:* {chat_name}\n"
            response += f"*Тип чата:* {chat_type}\n"
            response += f"*Количество администраторов:* {admin_count}\n"
            response += "*Администраторы:*\n\n"

            for admin in admins:
                response += f"  - *Имя:* {admin['Имя администратора']}\n"
                response += f"    *Admin ID:* {admin['Admin ID']}\n"
                response += f"    *Username:* {admin['Username']}\n\n"

        # Отправляем сообщение
        await message.answer(response, parse_mode='Markdown')

    except Exception as e:
        trace = traceback.format_exc()
        log.error(f"Возникла ошибка: {str(e)}\nТрассировка:\n{trace}")


@router.callback_query(F.data == "cancel")
async def get_cancel(callback: CallbackQuery, state: FSMContext):
    kb = await choice()
    await callback.message.answer("Выберете пункт", reply_markup=kb)
    await state.set_state(Form.admin_true)
