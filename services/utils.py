from aiogram.types import CallbackQuery


def get_id_from_callback(callback: CallbackQuery) -> int:
    return int(callback.data.split(':')[-1])