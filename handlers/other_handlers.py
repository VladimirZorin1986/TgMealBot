from aiogram import Router
from aiogram.types import Message, CallbackQuery

router = Router()


@router.message()
async def process_any_message(message: Message):
    await message.answer('Я вас не понимаю')


@router.callback_query()
async def process_any_callback(callback: CallbackQuery):
    await callback.answer('Нет хэндлера')
