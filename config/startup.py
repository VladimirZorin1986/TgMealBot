from aiogram import Bot
from aiogram.types import BotCommand

DESCRIPTION = '''
Добро пожаловать в бот заказа питания в столовой ГК "ОТЭКО".
Бот предназначен для удаленного формирования заказов для столовой предприятия.
Для начала работы необходимо авторизоваться.
Убедитесь, что вы являетесь действующим заказчиком столовой 
и ваш номер телефона с приложением Telegram установлен основным контактом в кадровой службе.
Для продуктивной работы с ботом настоятельно рекомендуем ознакомиться с разделом /help .
'''


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
    await bot.set_my_description(DESCRIPTION)
