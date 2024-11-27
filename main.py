import asyncio
from aiogram import Bot, Dispatcher
from handlers.default_handlers import adm_handlers, message, topic_handler, help
from loader import dp, bot
from loger.logger_helper import get_logger
from utils.send_comand import set_default_commands

log = get_logger(__name__)

async def on_startup(dispatcher: Dispatcher):
    log.info("Запуск бота...")
    await set_default_commands(bot)

async def main():
    dp.include_router(topic_handler.router)
    dp.include_router(adm_handlers.router)
    dp.include_router(message.router)
    dp.include_router(help.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("Бот остановлен пользователем.")
    except Exception as e:
        log.critical(f"Необработанное исключение: {e}")
