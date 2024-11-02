import datetime
from aiogram import Bot
from database.hd_dao import HDRepository
from services.models import SHDType, SNewHDRequest, SCurrentHDRequest
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.fsm.context import FSMContext
from exceptions.hd_exceptions import RequestsNotExists


class HDService:

    @classmethod
    async def get_hd_types(cls, session: AsyncSession) -> list[SHDType]:
        raw_types = await HDRepository.get_all_types(session)
        return [
            SHDType(id=hd_type.id, name=hd_type.name) for hd_type in raw_types
        ]

    @classmethod
    async def remember_variables(cls, state: FSMContext, **kwargs) -> None:
        data = await state.get_data()
        await state.update_data(data, **kwargs)

    @classmethod
    async def _get_new_request_from_state(cls, state: FSMContext) -> SNewHDRequest:
        data = await state.get_data()
        return SNewHDRequest(
            type_id=data.get('type_id'),
            user_id=data.get('user_id'),
            request_text=data.get('request_text'),
            phone_number=data.get('phone_number'),
            user_name=data.get('user_name')
        )

    @classmethod
    async def save_request(cls, session: AsyncSession, state: FSMContext):
        request = await cls._get_new_request_from_state(state)
        new_request_id = await HDRepository.save_new_request(session, request.model_dump())
        return new_request_id

    @classmethod
    async def answer_user_request(cls, session: AsyncSession, state: FSMContext):
        data = await state.get_data()
        await HDRepository.update_request(
            session,
            data.get('request_id'),
            {
                'solution_text': data.get('solution_text'),
                'done_at': datetime.datetime.now()
            }
        )
        return data.get('request_id'), data.get('send_user_id')

    @classmethod
    async def get_user_requests(cls, session: AsyncSession, user_id: int) -> dict[int, SCurrentHDRequest]:
        raw_requests = await HDRepository.get_requests_by_user_with_boundaries(session, user_id)
        if not raw_requests:
            raise RequestsNotExists
        return {raw_request['id']: SCurrentHDRequest(**raw_request) for raw_request in raw_requests}

    @classmethod
    async def get_requests_by_admin(cls, session: AsyncSession, mode: str = 'all') -> dict[int, SCurrentHDRequest]:
        if mode == 'new':
            raw_requests = await HDRepository.get_new_requests_with_boundaries(session)
        else:
            raw_requests = await HDRepository.get_all_requests_with_boundaries(session)
        if not raw_requests:
            raise RequestsNotExists
        return {raw_request['id']: SCurrentHDRequest(**raw_request) for raw_request in raw_requests}

    @classmethod
    async def get_request_from_cache(cls, state: FSMContext, request_id: int) -> SCurrentHDRequest:
        data = await state.get_data()
        return data['requests'].get(request_id)

    @classmethod
    async def send_message_to_user(cls, bot: Bot, user_id: int, msg_text: str) -> None:
        try:
            await bot.send_message(chat_id=user_id, text=msg_text)
        except Exception as e:
            print(f'Произошла ошибка при отправке сообщения пользователю с id={user_id}.\nТекст ошибки: {e}')

    # @classmethod
    # async def _get_user_ids(cls, session: AsyncSession) -> list[int]:
    #     raw_user_ids = await HDRepository.get_bot_users(session)
    #     return [tg_id for tg_id in raw_user_ids]

    @classmethod
    async def send_message_to_bot_users(cls, bot: Bot, msg_text: str, session: AsyncSession) -> None:
        user_ids = await HDRepository.get_bot_users(session)
        for user_id in user_ids:
            await cls.send_message_to_user(bot, user_id, msg_text)

    @classmethod
    async def is_auth_user(cls, session: AsyncSession, user_id: int) -> bool:
        if not await HDRepository.auth_user_check(session, user_id):
            return False
        return True
