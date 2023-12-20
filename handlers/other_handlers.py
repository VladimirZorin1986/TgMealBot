from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from presentation.responses import message_response, callback_response

router = Router()


@router.message()
async def process_user_message(message: Message):
    await message_response(
        message=message,
        text='Данный бот пока не умеет общаться с пользователями. '
             'Возможно в новой версии это исправят. '
             'А пока, если вам нужна помощь по работе бота '
             'нажмите на команду /help и следуйте инструкциям.'
    )


@router.callback_query(F.data == 'no action')
async def process_no_action_callback(callback: CallbackQuery):
    await callback_response(callback)


@router.callback_query()
async def process_old_callback(callback: CallbackQuery):
    await callback_response(
        callback=callback,
        text='Данное действие не может быть выполнено.',
        delete_after=True
    )
