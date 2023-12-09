from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from sqlalchemy.ext.asyncio import AsyncSession
from states.user_states import AuthState
from services.other_services import terminate_state_branch
from keyboards.inline import help_chapters_kb
from handlers.functions import process_switch_base_keyboards
from presentation import help_info


router = Router()


@router.message(CommandStart(), StateFilter(default_state))
async def process_start_command(message: Message, state: FSMContext, session: AsyncSession):
    await process_switch_base_keyboards(
        message, state, session, AuthState.get_contact
    )


@router.message(CommandStart(), ~StateFilter(default_state))
async def process_start_with_context(message: Message, state: FSMContext):
    await message.answer(
        text='Вы не закончили выполняемое действие. '
             'Закончите или нажмите на команду /cancel для отмены.'
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
async def process_cancel_with_context(message: Message, session: AsyncSession, state: FSMContext):
    await terminate_state_branch(message, state, add_last=False)
    await process_switch_base_keyboards(
        message, state, session, AuthState.get_contact
    )


@router.message(Command('cancel'), StateFilter(default_state))
async def process_cancel_without_context(message: Message):
    await message.answer(
        text='Вы не находитесь в состоянии выполнения действия. '
             'Нажмите на команду /start для возврата в главное меню.'
    )

