import os
from dotenv import load_dotenv, find_dotenv
from loger.logger_helper import get_logger

log = get_logger(__name__)

if not find_dotenv():
    log.info("Переменные окружения не загружены т.к отсутствует файл .env")
else:
    load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
DEFAULT_COMMANDS = (
    ("start", "Запустить бота"),
    ("check_bot_rights", "Проверка статуса бота"),
    ("get_forum_info", "Информация о чате"),
)
