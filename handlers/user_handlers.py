from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from sqlalchemy.ext.asyncio import AsyncSession
from keyboards.reply import initial_kb
from states.user_states import AuthState, ChangeDeliveryPlace
from services.other_services import (add_message_to_track, terminate_state_branch)
from services.user_services import update_customer_data
from handlers.functions import process_choice_canteens_or_places, process_choice_delivery_place

router = Router()


@router.message(StateFilter(AuthState.get_contact), F.contact)
async def process_auth_with_contact(message: Message, state: FSMContext, session: AsyncSession):
    await process_choice_canteens_or_places(
        message, state, session, AuthState.get_canteen, AuthState.get_place
    )


@router.message(StateFilter(AuthState.get_contact), ~F.contact)
async def process_auth_no_contact(message: Message):
    await message.answer(
        text='Необходимо дать доступ к контактным данным. '
             'Иначе авторизация невозможна.'
    )


@router.message(StateFilter(AuthState.get_canteen))
@router.message(StateFilter(AuthState.get_place))
async def process_no_canteen(message: Message, session: AsyncSession, state: FSMContext):
    msg = await message.answer(
        text='Для продолжения авторизации необходимо следовать инструкции. '
             'Если хотите отменить это действие нажмите на команду /cancel'
    )
    await add_message_to_track(msg, state)


@router.callback_query(StateFilter(AuthState.get_place), F.data.startswith('canteen'))
@router.callback_query(StateFilter(AuthState.get_canteen))
async def process_set_place_auth(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await process_choice_delivery_place(
        callback, state, session, AuthState.get_canteen, AuthState.get_place
    )


@router.callback_query(StateFilter(AuthState.get_place), F.data.startswith('place'))
async def process_get_place(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await update_customer_data(session, callback, state)
    await callback.message.answer(
        text='Теперь вы можете сделать заказ.',
        reply_markup=initial_kb()
    )
    await callback.answer(
        text='Вы успешно авторизовались!',
        show_alert=True
    )
    await terminate_state_branch(callback.message, state, add_last=False)


@router.message(F.text.endswith('Изменить место доставки'), StateFilter(default_state))
async def process_change_delivery_place(message: Message, session: AsyncSession, state: FSMContext):
    await process_choice_canteens_or_places(
        message, state, session, ChangeDeliveryPlace.set_new_canteen, ChangeDeliveryPlace.set_new_place
    )


@router.callback_query(StateFilter(ChangeDeliveryPlace.set_new_place), F.data.startswith('canteen'))
@router.callback_query(StateFilter(ChangeDeliveryPlace.set_new_canteen))
async def process_change_place(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await process_choice_delivery_place(
        callback, state, session, ChangeDeliveryPlace.set_new_canteen, ChangeDeliveryPlace.set_new_place
    )


@router.callback_query(StateFilter(ChangeDeliveryPlace.set_new_place), F.data.startswith('place'))
async def process_get_place(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await update_customer_data(session, callback, state)
    await callback.message.answer(
        text='Теперь вы можете сделать заказ.',
        reply_markup=initial_kb()
    )
    await callback.answer(
        text='Место доставки успешно изменено!',
        show_alert=True
    )
    await terminate_state_branch(callback.message, state, add_last=False)
