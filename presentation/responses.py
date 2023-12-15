import asyncio
from typing import NewType, Optional
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from services.other_services import add_message_to_track

KeyboardMarkup = NewType('KeyboardMarkup', Optional[InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove])


async def message_response(
        message: Message, text: str,
        reply_markup: KeyboardMarkup,
        state: FSMContext | None = None,
        delay: float = None
) -> None:
    msg = await message.answer(
        text=text,
        reply_markup=reply_markup
    )
    if state:
        await add_message_to_track(msg, state)
    if delay:
        await asyncio.sleep(delay)
