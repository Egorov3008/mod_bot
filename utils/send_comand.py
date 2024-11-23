from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault
from config_data.config import DEFAULT_COMMANDS


async def set_default_commands(bot: Bot):
    commands = [BotCommand(command=command, description=description)
                for command, description in DEFAULT_COMMANDS]
    await bot.set_my_commands(commands, BotCommandScopeDefault())