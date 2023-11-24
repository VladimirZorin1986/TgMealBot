from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from sqlalchemy.ext.asyncio import AsyncSession
from states.user_states import AuthState
from services.user_services import is_auth
from services.other_services import initiate_track_messages
from keyboards.reply import authorization_kb, initial_kb


router = Router()


@router.message(CommandStart(), StateFilter(default_state))
async def process_start_command(message: Message, state: FSMContext, session: AsyncSession):
    if not await is_auth(session, message.from_user.id):
        await state.set_state(AuthState.get_contact)
        msg = await message.answer(
            text='Для продолжения работы необходимо авторизоваться.',
            reply_markup=authorization_kb())
        await initiate_track_messages(msg, state)
    else:
        await message.answer(
            text='Теперь вы можете сделать заказ',
            reply_markup=initial_kb()
        )
