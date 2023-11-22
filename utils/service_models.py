from dataclasses import dataclass
from aiogram.types import Message


@dataclass
class TrackCallback:
    message: Message
    callback_data: str

