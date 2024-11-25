from telethon.sync import TelegramClient
from telethon.tl.functions.channels import GetParticipantsRequest

# Ваш API ID и HASH, полученные при регистрации приложения в Telegram
api_id = 'YOUR_API_ID'
api_hash = 'YOUR_API_HASH'

# Имя сеанса (можете задать любое уникальное имя)
session_name = 'my_session'

# Создаем клиента для работы с Telegram API
client = TelegramClient(session_name, api_id, api_hash)

# Авторизуемся под своим аккаунтом
client.start(phone=lambda: input('Введите номер телефона: '),
             password=lambda: input('Введите пароль двухэтапной аутентификации (если применимо): '))


async def get_group_participants(group_username):
    # Получаем объект группы по имени
    group_entity = await client.get_input_entity(group_username)

    # Используем метод GetParticipantsRequest для получения списка участников
    participants = await client(GetParticipantsRequest(
        channel=group_entity,
        filter=None,  # Фильтры можно применить для получения определённых участников
        offset=0,
        limit=200,  # Лимит участников, которые будут получены за один запрос
        search=None  # Поиск по участникам
    ))

    # Сохраняем ID участников
    participant_ids = [p.user_id for p in participants.users]

    return participant_ids


with client:
    participant_ids = client.loop.run_until_complete(get_group_participants('название_группы'))
    print(participant_ids)