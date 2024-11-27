import json
from loger.logger_helper import get_logger
import aiofiles
from config_data.config import CHAT_ID

chat_id = CHAT_ID
log = get_logger(__name__)


async def load_from_json(name_file, key=None):
    """
    Асинхронная функция для извлечения значения по ключу из JSON-файла.

    Args:
        name_file (str): Путь к файлу, содержащему JSON-данные.
        key (str): Ключ для поиска данных.

    Returns:
        значение (Any): Значение, соответствующее указанному ключу, если он существует в JSON-файле.
                        Если файл не найден или произошла ошибка при его чтении, возвращает False.

    Raises:
        FileNotFoundError: Если указанный файл не существует.
        json.JSONDecodeError: Если содержимое файла не является корректным JSON.

    Примечания:
        Функция использует библиотеку aiofiles для асинхронного чтения файлов.
        Если файл пустой, возвращается пустой словарь.
    """
    try:
        async with aiofiles.open(name_file, mode='r', encoding='utf-8') as f:
            contents = await f.read()
            if contents.strip():
                data = json.loads(contents)
                log.info(f"Значение успешно извлечено из файла '{data}'.")

            else:
                data = {}
                log.warning(f"Файл '{name_file}' пуст, возвращается пустой словарь.")
    except (FileNotFoundError, json.JSONDecodeError) as e:
        log.error(f"Произошла ошибка при чтении файла '{name_file}': {e}")
        return False
    if key is None:
        return {} if data is None else data

    if key in data:
        for k in data:
            if k == key:
                log.info(f"Данные загружены: {data[k]}")
                return data[k]
    else:
        log.warning(f"Chat_id '{chat_id}' не найден в файле '{name_file}'.")
        return {}


async def save_to_json(data, name_file):
    """
    Сохраняет данные в JSON файл. Если файл уже существует, данные
    будут объединены с существующими.

    :param data: dict - Данные, которые нужно сохранить в файл.
    :param name_file: str - Имя файла, вкоторый будут сохранены данные.
    """
    try:
        async with aiofiles.open(name_file, mode='r', encoding='utf-8') as f:
            contents = await f.read()
            if contents.strip():  # Проверка на пустое содержимое
                existing_data = json.loads(contents)
                log.info(f"Загружены существующие данные из файла '{name_file}'.")
            else:
                existing_data = {}
                log.warning(f"Файл '{name_file}' пуст, новые данные будут записаны.")
    except (FileNotFoundError, json.JSONDecodeError) as e:
        log.error(f"Произошла ошибка при чтении файла '{name_file}': {e}")
        existing_data = {}

    # Обновляем существующие данные новыми
    for key, value in data.items():
        existing_data[key] = value
        log.debug(f"Обновление ключа '{key}' с новым значением: {value}")

    try:
        # Запись обновленных данных в файл
        async with aiofiles.open(name_file, mode='w', encoding='utf-8') as f:
            await f.write(json.dumps(existing_data, indent=4, ensure_ascii=False))
            log.info(f"Данные успешно сохранены в файл '{name_file}'.")
    except Exception as e:
        log.error(f"Произошла ошибка при записи в файл '{name_file}': {e}")



async def delete_from_json(key, name_file):
    """
    Удаляет запись по заданному ключу из JSON файла.

    :param key: str - Ключ, который нужно удалить.
    :param name_file: str - Имя файла, из которого нужно удалить данные.
    :return: bool - True, если удаление прошло успешно, иначе False.
    """
    try:
        async with aiofiles.open(name_file, mode='r', encoding='utf-8') as f:
            contents = await f.read()
            if contents.strip():
                data = json.loads(contents)
                log.info(f"Данные загружены для удаления ключа '{key}' из файла '{name_file}'.")
            else:
                log.warning(f"Файл '{name_file}' пуст, ничего не удаляется.")
                return False
    except (FileNotFoundError, json.JSONDecodeError) as e:
        log.error(f"Произошла ошибка при чтении файла '{name_file}': {e}")
        return False

    if key in data:
        del data[key]
        log.info(f"Ключ '{key}' успешно удален из файла '{name_file}'.")
        try:
            async with aiofiles.open(name_file, mode='w', encoding='utf-8') as f:
                await f.write(json.dumps(data, indent=4, ensure_ascii=False))
                log.info(f"Изменения успешно сохранены в файл '{name_file}'.")
                return True
        except Exception as e:
            log.error(f"Произошла ошибка при записи в файл '{name_file}': {e}")
            return False
    else:
        log.warning(f"Ключ '{key}' не найден в файле '{name_file}', ничего не удаляется.")
        return False




