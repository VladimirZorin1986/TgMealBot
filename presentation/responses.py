import asyncio
from typing import NewType, Optional
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from services.other_services import add_message_to_track

KeyboardMarkup = NewType('KeyboardMarkup', Optional[InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove])


async def message_response(
        message: Message,
        text: str,
        reply_markup: KeyboardMarkup,
        state: FSMContext | None = None,
        delay: float | None = None,
        delete_after: bool | None = None
) -> None:
    msg = await message.answer(
        text=text,
        reply_markup=reply_markup
    )
    if state:
        await add_message_to_track(msg, state)
    if delay:
        await asyncio.sleep(delay)
    if delete_after:
        await message.delete()


async def edit_response(
        message: Message,
        text: str,
        reply_markup: KeyboardMarkup
) -> None:
    await message.edit_text(
        text=text,
        reply_markup=reply_markup
    )


async def callback_response(
        callback: CallbackQuery,
        text: str | None = None,
        show_alert: bool | None = None,
        delete_after: bool | None = None
) -> None:
    await callback.answer(
        text=text,
        show_alert=show_alert
    )
    if delete_after:
        await callback.message.delete()
