import logging
from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio

# Введите токен вашего бота
TOKEN = '7686103082:AAGZguErdQVrgWvjpNaRg26oPURBfi7z_l0'
CHAT_ID = -2352818663  # ID вашего канала
router = Router()

# Включаем логирование
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s - Line: %(lineno)d', )
log = logging.getLogger('bot')

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Словарь для хранения ссылок на темы
threads = {}

# Словарь для хранения выбранных тем
topic = {}


# Класс состояний для FSM
class Form(StatesGroup):
    set_topic = State()
    add_task_time = State()
    add_task_content = State()


# Обработка команды /start
@router.message(CommandStart())
async def send_welcome(message: types.Message):
    log.info(f"Команда /start от пользователя {message.from_user.id}")
    await message.reply(
        "Привет! Я бот, который может перейти по ссылкам тем. Используйте команду /go <тема>, чтобы перейти.")



# Обработка команды /announce
@router.message(Command('announce'))
async def announce_to_channel(message: types.Message):
    announcement = message.text.split(' ', 1)[1] if len(message.text.split(' ', 1)) > 1 else None

    if not announcement:
        await message.reply("Пожалуйста, укажите текст объявления после команды /announce.")
        return

    try:
        chat_id = "-2352818663"  # Получаем chat_id из topic, или используем глобальный
        logging.debug(f"ссылка {chat_id} передана")
        await bot.send_message(message.chat.id, announcement, message_thread_id=message.message_thread_id)
        await message.reply("Сообщение успешно отправлено в канал.")
    except Exception as e:
        log.error(f"Ошибка при отправке сообщения в канал: {e}")
        await message.reply("Произошла ошибка при отправке сообщения в канал.")

@router.message()
async def handle_messages(message: types.Message):
    # Проверяем, является ли сообщение частью потока
    if message.reply_to_message:
        thread_id = message.reply_to_message.message_id
        msg = message.reply_to_message.text


        # Если поток еще не существует, создаем новый
        # if thread_id not in threads:
        #     threads[message.text] = thread_id  # Записываем текст первого сообщения в потоке
        #     logging.info(f"Создан новый поток {message.text}: {thread_id}")
        # else:
        #     logging.info(f"Поток {thread_id} уже существует.")

    # Отвечаем в чат, что поток отслеживается
        await message.reply(f"Я отвечаю на сообщение: {msg} отслеживается в потоке с ID {thread_id}")

# Основная функция для запуска бота
async def main():
    logging.info("Запуск бота...")
    dp.include_router(router)
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Произошла ошибка во время работы бота: {e}")
    finally:
        logging.info("Бот завершил работу.")


if __name__ == "__main__":
    try:
        asyncio.run(main(), debug=True)
    except KeyboardInterrupt:
        logging.info("Бот остановлен пользователем.")
    except Exception as e:
        logging.critical(f"Необработанное исключение: {e}")
