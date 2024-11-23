from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup

list_command = (
    "Текст",
    "Видео",
    "Ссылка",
)


async def cmd_start() -> ReplyKeyboardMarkup:
    """
    Обрабатывает команду '/start' и отправляет пользователю клавиатуру с
    основными опциями.

    Параметры:
    - message (Message): Сообщение от пользователя, содержащая информацию о команде.

    Возвращает:
    - None: Функция ничего не возвращает, но отправляет сообщение пользователю
            с клавиатурой.
    """
    kb = [[KeyboardButton(text=command)] for command in list_command]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb, resize_keyboard=True, input_field_placeholder="Выберите фильтр"
    )
    return keyboard


async def params() -> ReplyKeyboardMarkup:
    """
    Создает клавиатуру с параметрами фильтрации для выбора.

    Возвращает:
    - ReplyKeyboardMarkup: Клавиатура с кнопками для выбора параметров
                          фильтрации (жанр, год, тип, бюджет, возрастной рейтинг, рейтинг, результат).
    """
    kb = [
        [KeyboardButton(text="ЖАНР"), KeyboardButton(text="ГОД")],
        [KeyboardButton(text="ТИП"), KeyboardButton(text="БЮДЖЕТ")],
        [KeyboardButton(text="ВОЗРАСТНОЙ РЕЙТИНГ"), KeyboardButton(text="РЕЙТИНГ")],
        [KeyboardButton(text="РЕЗУЛЬТАТ")],
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Выберите фильтр или нажмите кнопку 'РЕЗУЛЬТАТ'",
    )
    return keyboard


async def result() -> ReplyKeyboardMarkup:
    """
    Создает клавиатуру с кнопкой для отображения результатов.

    Возвращает:
    - ReplyKeyboardMarkup: Клавиатура с кнопкой 'РЕЗУЛЬТАТ'.
    """
    kb = [[KeyboardButton(text="РЕЗУЛЬТАТ")]]
    keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    return keyboard


async def cancel() -> ReplyKeyboardMarkup:
    """
    Создает клавиатуру с кнопкой для отображения результатов.

    Возвращает:
    - ReplyKeyboardMarkup: Клавиатура с кнопкой 'РЕЗУЛЬТАТ'.
    """
    kb = [[KeyboardButton(text="НАЗАД")]]
    keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    return keyboard
