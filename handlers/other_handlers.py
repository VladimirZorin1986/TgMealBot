from aiogram import Router
from aiogram.types import Message, CallbackQuery

router = Router()


@router.message()
async def process_user_message(message: Message):
    await message.answer(
        text='Данный бот пока не умеет общаться с пользователями. '
             'Возможно в новой версии это исправят. '
             'А пока, если вам нужна помощь по работе бота '
             'нажмите на команду /help и следуйте инструкциям.'
    )


@router.callback_query()
async def process_old_callback(callback: CallbackQuery):
    await callback.answer(
        text='Данное действие отменено и не может быть выполнено.'
    )
    await callback.message.delete()
