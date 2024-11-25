import traceback
from aiogram.enums import ChatMemberStatus, ChatType
from aiogram.filters import Command, CommandStart
from aiogram import Router, F, exceptions
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from loger.logger_helper import get_logger
from loader import bot
from config_data.config import CHAT_ID
from states.states_bot import Form, Topic
from keyboards.inline.inline_config import choice, topic_kb
from utils.utils_custom import save_to_json, load_from_json

log = get_logger(__name__)
router = Router()
chat_id = CHAT_ID


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
        admins = await get_group_admins(chat_id)
        is_admin = user.id in admins

        if is_admin:
            kb = await choice()
            await state.set_state(Form.admin_true)
            await message.answer(f"Привет {user.first_name}! Я готов к работе\n"
                                 f"Выбери действие", reply_markup=kb)
            await message.delete()
        elif is_admin:
            await message.answer(f"Привет {user.first_name}! Вы должны сделать меня админом в группе")
    except Exception:
        await message.answer("Что-то пошло не так 🤷‍♂️\n"
                             "Возможно, меня нет в Вашей группе")


async def get_group_info(chat_id):
    """
    Получает информацию о группе, включая список идентификаторов администраторов.

    :param chat_id: int - Идентификатор чата группы.
    :return: dict - Словарь с информацией о группе и администраторах.
    """
    try:
        chat = await bot.get_chat(chat_id)

        if chat.type != ChatType.SUPERGROUP:
            log.debug("Этот чат не является супергруппой.")
            return

        administrators = await bot.get_chat_administrators(chat_id)
        users = [usr.user for usr in administrators]
        log.debug(f"Полученные данные: {users}")

        chat_info = {f"{chat_id}":
            {
            "Название чата": chat.title,
            "Тип чата": chat.type,
            "Количество администраторов": len(administrators),
            "Администраторы": [
                {
                    "Admin ID": user.id,
                    "Имя администратора": user.full_name,
                    "Username": f"@{user.username}" if hasattr(user, 'username') and user.username else "Нет"
                }
                for user in users
            ]
        }}

        await save_to_json(chat_info, "info_chats.json")
        return chat_info  # Возвращаем информацию о группе
    except Exception as e:
        log.error(f"Возникла ошибка: {e}\nТрассировка:\n{traceback.format_exc()}")
        return None  # Возвращаем None в случае ошибки


async def get_group_admins(chat_id):
    try:
        await get_group_info(chat_id)
        data_admins = await load_from_json("info_chats.json")
        if data_admins:
            print(f"Данные переданы: {data_admins}")
        list_adm = data_admins.get("Администраторы")
        print(list_adm)
        return [itm.get("Admin ID") for itm in list_adm]
    except Exception as e:
        log.error(f"Возникла ошибка: {e}\nТрассировка:\n{traceback.format_exc()}")
        return []  # Возвращаем пустой список в случае ошибки



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
        await message.reply("Бот не состоит в группе")


@router.message(Command('get_chat_info'))
async def get_chat_info(message: Message):
    """
    Обрабатывает команду /get_chat_info. Получает информацию о чате и
    отправляет её пользователю.

    :param message: Message - Сообщение, содержащее команду.
    """
    try:
        chat_info = await load_from_json("info_chats.json")
        if chat_info:

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

# @router.callback_query(F.data == "choice_topic")
# async def choose_topic_for_choice(callback: CallbackQuery):
#     """
#     Позволяет пользователю выбрать тему для регистрации.
#
#     Загружает список тем из JSON-файла и предлагает пользователю выбрать
#     одну из них для последующих действий.
#
#     Args:
#         callback (CallbackQuery): Объект обратного вызова, содержащий информацию о нажатой кнопке.
#     """
#     log.info("Пользователь выбрал 'choice_topic'.")
#     topics = await load_from_json("topic.json")
#     if not topics:
#         await callback.message.answer("Темы не найдены.")
#         return
#
#     builder = InlineKeyboardBuilder()
#     for topic in topics.keys():
#         builder.button(text=topic, callback_data=f"choice_{topic}")
#     builder.adjust(1)
#
#     await callback.message.answer("Выберите тему:", reply_markup=builder.as_markup())
#
#
# @router.callback_query(F.data.startswith("choice_"))
# async def register_to_topic(callback: CallbackQuery):
#     """
#     Регистрирует пользователя на выбранную тему.
#
#     Извлекает название темы из данных обратного вызова и добавляет
#     пользователя в список зарегистрированных. Уведомляет о результате.
#
#     Args:
#         callback (CallbackQuery): Объект обратного вызова, содержащий информацию о нажатой кнопке.
#     """
#     topic = callback.data[len("choice_"):]
#     topics = await load_from_json("topic.json")
#
#     if topic not in topics:
#         await callback.message.answer(f"Тема '{topic}' не найдена.")
#         return
#
#     user_id = callback.from_user.id
#
#     if user_id not in topics[topic]["users"]:
#         topics[topic]["users"].append(user_id)
#         await save_to_json(topics, "topic.json")
#         await callback.message.answer(f"Вы успешно зарегистрированы на тему '{topic}'.")
#     else:
#         await callback.message.answer(f"Вы уже зарегистрированы на тему '{topic}'.")
#
#
# @router.callback_query(F.data == "unsubscribe_topic")
# async def choose_topic_for_unsubscribe(callback: CallbackQuery):
#     """
#     Позволяет пользователю выбрать тему для отписки.
#
#     Загружает список тем из JSON-файла и предлагает пользователю выбрать
#     одну из них для отписки.
#
#     Args:
#         callback (CallbackQuery): Объект обратного вызова, содержащий информацию о нажатой кнопке.
#     """
#     log.info("Пользователь выбрал 'unsubscribe_topic'.")
#     topics = await load_from_json("topic.json")
#     if not topics:
#         await callback.message.answer("Темы не найдены.")
#         return
#
#     builder = InlineKeyboardBuilder()
#     for topic in topics.keys():
#         builder.button(text=topic, callback_data=f"unsubscribe_{topic}")
#     builder.adjust(1)
#
#     await callback.message.answer("Выберите тему для отписки:", reply_markup=builder.as_markup())
#
#
# @router.callback_query(F.data.startswith("unsubscribe_"))
# async def unsubscribe_from_topic(callback: CallbackQuery):
#     """
#     Отписывает пользователя от выбранной темы.
#
#     Извлекает название темы из данных обратного вызова и удаляет
#     пользователя из списка зарегистрированных. Уведомляет о результате.
#
#     Args:
#         callback (CallbackQuery): Объект обратного вызова, содержащий информацию о нажатой кнопке.
#     """
#     topic = callback.data[len("unsubscribe_"):]
#     topics = await load_from_json("topic.json")
#
#     if topic not in topics:
#         await callback.message.answer(f"Тема '{topic}' не найдена.")
#         return
#
#     user_id = callback.from_user.id
#
#     if user_id in topics[topic]["users"]:
#         topics[topic]["users"].remove(user_id)
#         await save_to_json(topics, "topic.json")
#         await callback.message.answer(f"Вы успешно отписались от темы '{topic}'.")
#     else:
#         await callback.message.answer(f"Вы не зарегистрированы на тему '{topic}'.")
#
#
# @router.callback_query(F.data == "view_registered_users")
# async def choose_topic_for_view_users(callback: CallbackQuery):
#     """
#     Позволяет пользователю выбрать тему для просмотра зарегистрированных пользователей.
#
#     Загружает список тем из JSON-файла и предлагает пользователю выбрать
#     одну из них для просмотра зарегистрированных пользователей.
#
#     Args:
#         callback (CallbackQuery): Объект обратного вызова, содержащий информацию о нажатой кнопке.
#     """
#     log.info("Пользователь выбрал 'view_registered_users'.")
#     topics = await load_from_json("topic.json")
#     if not topics:
#         await callback.message.answer("Темы не найдены.")
#         return
#
#     builder = InlineKeyboardBuilder()
#     for topic in topics.keys():
#         builder.button(text=topic, callback_data=f"view_users_{topic}")
#     builder.adjust(1)
#
#     await callback.message.answer("Выберите тему для просмотра пользователей:", reply_markup=builder.as_markup())
#
#
# @router.callback_query(F.data.startswith("view_users_"))
# async def view_registered_users(callback: CallbackQuery):
#     """
#     Отображает зарегистрированных пользователей для выбранной темы.
#
#     Извлекает название темы из данных обратного вызова и загружает
#     список зарегистрированных пользователей. Уведомляет пользователя о результате.
#
#     Args:
#         callback (CallbackQuery): Объект обратного вызова, содержащий информацию о нажатой кнопке.
#     """
#     topic = callback.data[len("view_users_"):]
#     topics = await load_from_json("topic.json")
#
#     if topic not in topics:
#         await callback.message.answer(f"Тема '{topic}' не найдена.")
#         return
#
#     users = topics[topic]["users"]
#     if not users:
#         await callback.message.answer(f"Нет зарегистрированных пользователей для темы '{topic}'.")
#     else:
#         users_list = "\n".join(users)
#         await callback.message.answer(f"Зарегистрированные пользователи для темы '{topic}':\n{users_list}")
