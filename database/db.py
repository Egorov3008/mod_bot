from loger.logger_helper import get_logger

from datetime import datetime
from peewee import Model, DateField, IntegerField, TextField, BooleanField
from playhouse.sqlite_ext import SqliteDatabase
from typing import List, Optional


db = SqliteDatabase('tg_tab.db')


class TelegramData(Model):
    """
    Модель для хранения данных о взаимодействиях пользователей с Telegram.

    Attributes:
        date (datetime.date): Дата добавления записи.
        user_id (int): Идентификатор пользователя.
        filter (str): Фильтр, использованный при запросе.
        result (str): Результат запроса.
    """
    date: DateField = DateField(default=datetime.now)  # Изменено на DateField
    user_id: IntegerField = IntegerField()
    filter: TextField = TextField()
    result: TextField = TextField()

    class Meta:
        database = db


db.connect()
db.create_tables([TelegramData], safe=True)


def add_data(user_id: int, filter_value: str, result_value: str) -> None:
    """
    Добавляет новые данные о взаимодействии пользователя с Telegram в базу данных.

    Args:
        user_id (int): Идентификатор пользователя.
        filter_value (str): Фильтр, использованный при запросе.
        result_value (str): Результат запроса.

    Returns:
        None
    """
    with db.atomic():
        TelegramData.create(date=datetime.now().date(), user_id=user_id, filter=filter_value, result=result_value)
        bot_logger.logger.info(f"Данные добавлены: user_id={user_id}, filter={filter_value}, result={result_value}")


def get_data_by_date(user_id: int, start_date_str: str, end_date_str: str) -> Optional[List[str]]:
    """
    Получает данные о взаимодействиях пользователя за указанный период.

    Args:
        user_id (int): Идентификатор пользователя.
        start_date_str (str): Начальная дата в формате 'YYYY-MM-DD'.
        end_date_str (str): Конечная дата в формате 'YYYY-MM-DD'.

    Returns:
        Optional[List[str]]: Список уникальных результатов запросов за указанный период или None, если данные не найдены.
    """
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    bot_logger.logger.debug(f"Начало периода {start_date}, Конец периода {end_date}")
    results = TelegramData.select().where(
        (TelegramData.date >= start_date) &
        (TelegramData.date <= end_date) &
        (TelegramData.user_id == user_id)
    )

    if results:
        bot_logger.logger.info(
            f"Найдены данные за период {start_date.strftime('%Y-%m-%d')} - {end_date.strftime('%Y-%m-%d')}:"
        )
        seen_results = set()
        for item in results:
            result_key = item.result
            if result_key not in seen_results:
                seen_results.add(
                    f"*ДАТА ПОИСКА*: {item.date}\n*ПАРАМЕТРЫ ПОИСК*: '{item.filter}'\n*РЕЗУЛЬТАТ*: '{item.result}'")
                bot_logger.logger.info(f"user_id={item.user_id}, filter='{item.filter}', result='{item.result}'")
        return list(seen_results)
    else:
        bot_logger.logger.info(
            f"Данные за период {start_date.strftime('%Y-%m-%d')} - {end_date.strftime('%Y-%m-%d')} не найдены."
        )
        return None
