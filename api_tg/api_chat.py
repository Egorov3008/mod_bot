import traceback
from datetime import datetime, timedelta
from aiogram.types import Message
from aiogram.filters import Command
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.types import InputMediaPhoto, InlineKeyboardMarkup, InlineKeyboardButton
from apscheduler.triggers.interval import IntervalTrigger
from config_data.config import CHAT_ID
from loader import bot
from aiogram import Router
from loger.logger_helper import get_logger
from database.data_db import deleting_rows_by_date, Msg_chat, insert_message


log = get_logger(__name__)
router = Router()
chat_id = CHAT_ID
scheduler = AsyncIOScheduler()
log.info("Планировщик задач запущен")



async def send_to_thread(chat_id, text=None, img=None, link_text=None, link_url=None, topic_id=None):
    """
    Отправляет сообщение в заданный чат с возможностью прикрепления изображения и кнопки.

    Параметры:
    - chat_id (int): Идентификатор чата, куда будет отправлено сообщение.
    - text (str, optional): Текст сообщения. По умолчанию None.
    - img (str, optional): URL изображения для отправки. По умолчанию None.
    - link_text (str, optional): Текст кнопки, если необходимо добавить кнопку. По умолчанию None.
    - link_url (str, optional): URL, на который будет вести кнопка. По умолчанию None.
    - topic_id (int, optional): Идентификатор сообщения для ответа. По умолчанию None.

    Если указаны link_text и link_url, создаётся кнопка и отправляется сообщение с текстом
    и/или изображением. Если указаны только текст и/или изображение, то они отправляются
    без кнопки.

    Исключения:
    - Логирует ошибку, если возникает исключение во время выполнения.
    """
    global id_msg
    try:
        if link_text and link_url:
            button = [[InlineKeyboardButton(text=link_text, url=link_url)]]
            keyboard = InlineKeyboardMarkup(inline_keyboard=button)

            if img and text:
                media = [InputMediaPhoto(media=img)]
                sent_messages = await bot.send_media_group(chat_id=chat_id, media=media, reply_to_message_id=topic_id)
                send_keyboard = await bot.send_message(chat_id=chat_id, text=text, reply_markup=keyboard,
                                                       reply_to_message_id=topic_id)
                insert_message(chat_id=chat_id, msg_id=sent_messages[0].message_id, id_msg_kb=send_keyboard.message_id)

            elif text:
                sent_message = await bot.send_message(chat_id=chat_id, text=text, reply_to_message_id=topic_id,
                                                      reply_markup=keyboard)
                insert_message(chat_id=chat_id, msg_id=sent_message.message_id)
        else:
            if img and text:
                media = [InputMediaPhoto(media=img, caption=text)]
                sent_messages = await bot.send_media_group(chat_id=chat_id, media=media, reply_to_message_id=topic_id)
                insert_message(chat_id=chat_id, msg_id=sent_messages[0].message_id)

            elif text:
                sent_message = await bot.send_message(chat_id=chat_id, text=text, reply_to_message_id=topic_id)
                insert_message(chat_id=chat_id, msg_id=sent_message.message_id)

            elif img:
                media = [InputMediaPhoto(media=img)]
                sent_messages = await bot.send_media_group(chat_id=chat_id, media=media, reply_to_message_id=topic_id)
                insert_message(chat_id=chat_id, msg_id=sent_messages[0].message_id)

        log.info("Сообщение сформировано")

    except Exception as e:
        log.error(f"Возникла ошибка: {e}\nТрассировка:\n{traceback.format_exc()}")


async def del_msg(chat_id, message_id: str=None, id_kb: str=None):
    """
    Удаляет сообщение из заданного чата.

    Параметры:
    - chat_id (int): Идентификатор чата, из которого нужно удалить сообщение.
    - message_id (int): Идентификатор сообщения, которое нужно удалить.

    Исключения:
    - Логирует ошибку, если возникает исключение во время удаления сообщения.
    """
    try:
        await bot.delete_message(chat_id, message_id)
        if id_kb:
            await bot.delete_message(chat_id, id_kb)
    except Exception as e:
        log.error(f"Возникла ошибка при удалении сообщения: {e}\nТрассировка:\n{traceback.format_exc()}")

async def fetch_jobs():
    """
    Извлекает запланированные сообщения из базы данных и добавляет их в планировщик задач.

    Функция проверяет текущее время, извлекает сообщения из базы данных, у которых время начала больше текущего времени,
    и планирует их отправку. Если задача с таким идентификатором уже существует, она пропускается.

    :raises Exception: Если возникает ошибка при извлечении данных или добавлении задач в планировщик.
    """
    global msg
    try:
        date_now = datetime.now()
        current_date = date_now.strftime("%Y-%m-%d %H:%M")
        query = Msg_chat.select().where(Msg_chat.time_start > current_date)
        if query:
            log.debug("Загружаю данные из базы...")

            for msg in query:
                job_id = f"send_{msg.id}"
                if scheduler.get_job(job_id):
                    log.warning(f"Задача с идентификатором {job_id} уже существует. Пропуск создания.")
                    continue
                # Запланируем отправку сообщения и получим его message_id
                scheduler.add_job(send_to_thread, "date", run_date=msg.time_start,
                                  args=[chat_id, msg.text, msg.img, msg.link_text, msg.link_url,
                                        msg.topic_id], id=job_id)

                log.info(f"Сообщение для отправки в {msg.time_start} запланировано.")

                if msg.time_del:
                    date = msg.time_start + timedelta(minutes=1)
                    scheduler.add_job(del_msg_public, "date", run_date=date, args=[msg.time_del])
                if not scheduler.running:
                    scheduler.start()
                    log.info("Планировщик задач запущен.")

    except Exception as e:
        log.error(f"Ошибка при обработке сообщения ID: {e}\nТрассировка:\n{traceback.format_exc()}")


async def del_msg_public(time_del):
    """
    Запланирует удаление сообщения в заданное время.

    Функция получает сообщение из базы данных по времени удаления и добавляет задачу на его удаление в планировщик.
    Если у сообщения есть идентификатор кнопки, он будет использованв аргументах для удаления.

    :param time_del: Время удаления сообщения.
    :raises Exception: Если возникает ошибка при получении сообщения или добавлении задачи в планировщик.
    """
    global job_message_id
    try:
        job_message_id = Msg_chat.get(Msg_chat.time_del == time_del)
        if job_message_id.id_msg_kb:
            args = [chat_id, job_message_id.id_msg_kb, job_message_id.msg_id]
        else:
            args = [chat_id, job_message_id.id_msg_kb, job_message_id.msg_id]

        scheduler.add_job(del_msg, "date", run_date=time_del, args=args)
        log.info(f"Сообщение будет удалено в {time_del}.")
    except Exception as e:
        log.error(
            f"Ошибка при обработке сообщения ID: {job_message_id.id}: {e}\nТрассировка:\n{traceback.format_exc()}")

@router.message(Command("view_tasks"))
async def list_jobs(message: Message):
    """
    Обрабатывает команду /view_tasks и отправляет список запланированных задач пользователю.

    :param message: Сообщение от пользователя, содержащее команду.
    """
    jobs = scheduler.get_jobs()
    if jobs:
        for job in jobs:
            await message.answer(f'Название: {job.name}, Следующий запуск: {job.next_run_time}')
    else:
        await message.answer('Публикации не спланированы')


async def start_fetch_jobs():
    """
    Запускает планировщик задач и добавляет задачи для периодической публикации сообщений и очистки базы данных.

    Добавляет задачу для извлечения сообщений из базы данных каждые 5 минут и задачу для очистки базы данных каждые 5 дней.
    Если планировщик еще не запущен, он будет запущен.

    :return: Экземпляр планировщика задач.
    """
    try:
        # if date_start_scheduler is not None:
        #     pass
        scheduler.add_job(deleting_rows_by_date, name="Отчистка базы данных", trigger=IntervalTrigger(days=5))
        log.info("Задачи запланированы.")

        if not scheduler.running:
            scheduler.start()
            log.info("Планировщик задач запущен.")

        return scheduler  # Возвращаем экземпляр планировщика

    except Exception as e:
        log.error(f"Ошибка в start_fetch_jobs: {e}\nТрассировка:\n{traceback.format_exc()}")