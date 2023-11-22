from aiogram.filters import BaseFilter
from aiogram.types import Message


class IsAuth(BaseFilter):

    def __init__(self, db: dict[str, dict[int, str]]):
        self.db = db

    async def __call__(self, message: Message) -> bool:
        user_data = self.db['users'].get(message.from_user.id)
        if user_data and len(user_data) == 2:
            return True
        return False
