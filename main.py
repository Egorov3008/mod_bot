import asyncio
from handlers.default_handlers import adm_handlers, message, topic_handler
from loader import dp, bot
from loger.logger_helper import get_logger
from utils.send_comand import set_default_commands

log = get_logger(__name__)


async def main():
    log.info("Запуск бота...")
    try:
        dp.include_routers(adm_handlers.router,
                           message.router,
                           topic_handler.router,
                           )
        await set_default_commands(bot)
        await dp.start_polling(bot)
    except Exception as e:
        log.error(f"Произошла ошибка во время работы бота: {e}")
    finally:
        log.info("Бот завершил работу.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("Бот остановлен пользователем.")
    except Exception as e:
        log.critical(f"Необработанное исключение: {e}")
