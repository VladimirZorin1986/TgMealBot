from aiogram import Bot
from aiogram.types import BotCommand


async def set_main_menu(bot: Bot):

    commands = [
        BotCommand(
            command='/start',
            description='Начало работы с ботом'
        ),
        BotCommand(
            command='/help',
            description='Помощь по работе бота'
        ),
        BotCommand(
            command='/cancel',
            description='Глобальная отмена действия'
        )
    ]

    await bot.set_my_commands(commands=commands)


async def on_startup(bot: Bot):
    await set_main_menu(bot)
