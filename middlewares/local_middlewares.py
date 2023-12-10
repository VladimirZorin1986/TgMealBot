from typing import Callable, Awaitable, Dict, Any
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from aiogram.fsm.context import FSMContext


class ServiceManagerMiddleware(BaseMiddleware):
    def __init__(self, service_manager: Callable):
        super().__init__()
        self.service_manager = service_manager

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        state: FSMContext = data['state']
        state_data = await state.get_data()
        if self.service_manager.__name__ not in state_data:
            state_data[self.service_manager.__name__] = self.service_manager()
        data['manager'] = state_data.get(self.service_manager.__name__)
        return await handler(event, data)
