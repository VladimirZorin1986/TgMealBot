from typing import Any
from contextlib import suppress
from aiogram import Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from utils.service_models import TrackCallback


async def initiate_track_messages(message: Message, state: FSMContext) -> None:
    await state.update_data({'track_messages': [message.message_id]})


async def add_message_to_track(message: Message, state: FSMContext) -> None:
    data: dict[str, Any] = await state.get_data()
    track_list: list | None = data.get('track_messages')
    if track_list:
        track_list.append(message.message_id)
        await state.update_data(track_messages=track_list)


async def set_track_callback(callback: CallbackQuery, message: Message, state: FSMContext) -> None:
    await state.update_data(
        cb=TrackCallback(
            message=message,
            callback_data=callback.data
        )
    )


async def get_track_callback(state: FSMContext) -> TrackCallback | None:
    data = await state.get_data()
    track_cb = data.get('cb')
    if track_cb:
        return track_cb


async def update_track_callback(track_cb: TrackCallback, callback: CallbackQuery, state: FSMContext) -> None:
    track_cb.callback_data = callback.data
    await state.update_data(cb=track_cb)


async def erase_track_messages(state: FSMContext, bot: Bot, chat_id: int) -> None:
    data: dict[str, Any] = await state.get_data()
    track_msgs = data.get('track_messages')
    if track_msgs:
        for msg_id in track_msgs:
            with suppress(TelegramBadRequest):
                await bot.delete_message(chat_id=chat_id, message_id=msg_id)


