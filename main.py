import asyncio
from handlers.default_handlers import adm_handlers, message_handler, topic_handler, help
from api_tg import api_chat
from loader import dp, bot
from loger.logger_helper import get_logger
from utils.send_comand import set_default_commands
from api_tg.api_chat import start_fetch_jobs

log = get_logger(__name__)

# Глобальная переменная для хранения планировщика
scheduler = None

async def on_startup():
    log.info("Запуск бота...")
    await set_default_commands(bot)

    global scheduler
    scheduler = await start_fetch_jobs()  # Сохраняем экземпляр планировщика

async def stop_scheduler():
    global scheduler
    if scheduler:
        log.info("Остановка планировщика задач...")
        scheduler.shutdown()  # Остановка планировщика, если он был запущен
        log.info("Планировщик задач остановлен.")

async def main():
    dp.include_router(topic_handler.router)
    dp.include_router(adm_handlers.router)
    dp.include_router(message_handler.router)
    dp.include_router(help.router)
    dp.include_router(api_chat.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await on_startup()  # Запускаем планировщик при старте
    try:
        await dp.start_polling(bot)
    finally:
        await stop_scheduler()  # Останавливаем планировщик перед завершением работы

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("Бот остановлен пользователем.")
    except Exception as e:
        log.critical(f"Необработанное исключение: {e}")
