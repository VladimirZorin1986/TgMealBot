import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from config import load_config
from middleware import DbSessionMiddleware
from keyboards.main_menu import set_main_menu
from handlers.user_handlers import router as user_router
from handlers.order_handlers import router as order_router
from handlers.other_handlers import router as other_router
from handlers.command_handlers import router as command_router

logger = logging.getLogger(__name__)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s'
    )

    logger.info('Starting bot')

    config = load_config()

    engine = create_async_engine(url=config.db.url, echo=True)
    session_maker = async_sessionmaker(engine, expire_on_commit=False)

    bot = Bot(token=config.bot.token, parse_mode=ParseMode.HTML)
    dp = Dispatcher(storage=config.bot.storage)

    dp.startup.register(set_main_menu)

    dp.update.middleware(DbSessionMiddleware(session_pool=session_maker))

    dp.include_router(command_router)
    dp.include_router(user_router)
    dp.include_router(order_router)
    dp.include_router(other_router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())



