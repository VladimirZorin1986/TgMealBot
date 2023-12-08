from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from sqlalchemy.ext.asyncio import AsyncSession
from states.user_states import AuthState
from services.user_services import is_auth
from services.other_services import add_message_to_track, terminate_state_branch
from keyboards.reply import authorization_kb, initial_kb
from keyboards.inline import help_chapters_kb
from presentation import help_info


router = Router()


@router.message(CommandStart(), StateFilter(default_state))
async def process_start_command(message: Message, state: FSMContext, session: AsyncSession):
    if not await is_auth(session, message.from_user.id):
        await state.set_state(AuthState.get_contact)
        msg = await message.answer(
            text='Для продолжения работы необходимо авторизоваться.',
            reply_markup=authorization_kb())
        await add_message_to_track(msg, state)
    else:
        await message.answer(
            text='Теперь вы можете сделать заказ',
            reply_markup=initial_kb()
        )


@router.message(Command('help'))
async def process_help_command(message: Message):
    await message.answer(
        text=help_info('base_help'),
        reply_markup=help_chapters_kb()
    )


@router.callback_query(F.data.endswith('help'))
async def process_auth_help(callback: CallbackQuery):
    await callback.message.answer(
        text=help_info(callback.data)
    )
    await callback.answer()


@router.message(Command('cancel'), ~StateFilter(default_state))
async def process_global_cancel_command(message: Message, state: FSMContext):
    await terminate_state_branch(message, state, add_last=False)

