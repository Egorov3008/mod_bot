import traceback
from datetime import datetime
from aiogram.types import Message
from aiogram.filters import Command
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.types import InputMediaPhoto, InlineKeyboardMarkup, InlineKeyboardButton
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger

from loader import bot
from aiogram import Router
from loger.logger_helper import get_logger
from database.data_db import deleting_rows_by_date, Msg_chat

log = get_logger(__name__)
router = Router()

scheduler = AsyncIOScheduler()
log.info("Планировщик задач запущен")


async def send_to_thread(chat_id, text=None, img=None, link_text=None, link_url=None, topic_id=None):
    try:
        if link_text and link_url:
            button = [[InlineKeyboardButton(text=link_text, url=link_url)]]
            keyboard = InlineKeyboardMarkup(inline_keyboard=button)

            if img and text:
                media = [InputMediaPhoto(media=img, caption=text)]
                sent_messages = await bot.send_media_group(chat_id=chat_id, media=media, reply_to_message_id=topic_id)
                # await bot.send_message(chat_id=chat_id, text=text, reply_markup=keyboard,
                #                        reply_to_message_id=sent_messages[0].message_id)
                await bot.send_message(chat_id=chat_id, reply_markup=keyboard, reply_to_message_id=topic_id) # попытка отправить только кнопку
                return sent_messages[0].message_id

            elif text:
                sent_message = await bot.send_message(chat_id=chat_id, text=text, reply_to_message_id=topic_id,
                                                      reply_markup=keyboard)
                return sent_message.message_id

            elif img:
                media = [InputMediaPhoto(media=img)]
                sent_messages = await bot.send_media_group(chat_id=chat_id, media=media, reply_to_message_id=topic_id)
                return sent_messages[0].message_id

        else:
            if img and text:
                media = [InputMediaPhoto(media=img, caption=text)]
                sent_messages = await bot.send_media_group(chat_id=chat_id, media=media, reply_to_message_id=topic_id)
                return sent_messages[0].message_id

            elif text:
                sent_message = await bot.send_message(chat_id=chat_id, text=text, reply_to_message_id=topic_id)
                return sent_message.message_id

            elif img:
                media = [InputMediaPhoto(media=img)]
                sent_messages = await bot.send_media_group(chat_id=chat_id, media=media, reply_to_message_id=topic_id)
                return sent_messages[0].message_id

        log.info("Сообщение сформировано")

    except Exception as e:
        log.error(f"Возникла ошибка: {e}\nТрассировка:\n{traceback.format_exc()}")


async def del_msg(chat_id, message_id):
    try:
        await bot.delete_message(chat_id, message_id)
    except Exception as e:
        log.error(f"Возникла ошибка при удалении сообщения: {e}\nТрассировка:\n{traceback.format_exc()}")


async def fetch_jobs():
    try:
        date_now = datetime.now()
        current_date = date_now.strftime("%Y-%m-%d %H:%M")
        query = Msg_chat.select().where(Msg_chat.time_start > current_date)
        if query:
            log.debug("Загружаю данные из базы...")

            for msg in query:
                try:

                    chat_id = msg.chat_id
                    job_id = f"send_{msg.id}"

                    if scheduler.get_job(job_id):
                        log.warning(f"Задача с идентификатором {job_id} уже существует. Пропуск создания.")
                        continue

                    # Запланируем отправку сообщения и получим его message_id
                    job = scheduler.add_job(send_to_thread, "date", run_date=msg.time_start,
                                            args=[chat_id, msg.text, msg.img, msg.link_text, msg.link_url,
                                                  msg.topic_id],
                                            id=job_id)

                    job_message_id = await job.func(*job.args)
                    log.info(f"Сообщение для отправки в {msg.time_start} запланировано (ID: {job.id}).")

                    if msg.time_del:
                        delete_job_id = f"delete_{msg.id}"

                        if scheduler.get_job(delete_job_id):
                            log.warning(f"Задача с идентификатором {delete_job_id} уже существует. Пропуск создания.")
                            continue

                        # Запланируем удаление сообщения
                        scheduler.add_job(del_msg, "date", run_date=msg.time_del, args=[chat_id, job_message_id],
                                          id=delete_job_id)
                        log.info(f"Сообщение будет удалено в {msg.time_del} (ID: {delete_job_id}).")

                    if not scheduler.running:
                        scheduler.start()
                        log.info("Планировщик задач запущен.")

                except Exception as e:
                    log.error(
                        f"Ошибка при обработке сообщения ID: {msg.id}: {e}\nТрассировка:\n{traceback.format_exc()}")

    except Exception as e:
        log.error(f"Ошибка в fetch_jobs: {e}\nТрассировка:\n{traceback.format_exc()}")


@router.message(Command("view_tasks"))
async def list_jobs(message: Message):
    jobs = scheduler.get_jobs()
    if jobs:
        for job in jobs:
            await message.answer(f'Название: {job.name}, Следующий запуск: {job.next_run_time}')
    else:
        await message.answer('Публикации не спланированы')


async def start_fetch_jobs():
    try:
        log.info("Запуск start_fetch_jobs...")
        scheduler.add_job(fetch_jobs, trigger=IntervalTrigger(minutes=5 ))
        scheduler.add_job(deleting_rows_by_date, trigger=IntervalTrigger(days=5))
        log.info("Задачи запланированы.")

        if not scheduler.running:
            scheduler.start()
            log.info("Планировщик задач запущен.")

        return scheduler  # Возвращаем экземпляр планировщика

    except Exception as e:
        log.error(f"Ошибка в start_fetch_jobs: {e}\nТрассировка:\n{traceback.format_exc()}")
