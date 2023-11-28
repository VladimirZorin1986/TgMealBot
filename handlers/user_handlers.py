from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from sqlalchemy.ext.asyncio import AsyncSession
from keyboards.reply import authorization_kb, initial_kb
from keyboards.inline import show_canteens_kb, show_places_kb
from states.user_states import AuthState, ChangeDeliveryPlace
from services.other_services import (add_message_to_track, get_track_callback, set_track_callback,
                                     update_track_callback, terminate_state_branch)
from services.user_services import (get_customer_by_phone, update_customer_data, get_customer_by_tg_id,
                                    get_valid_canteens)
from exceptions import IsNotCustomer

router = Router()


@router.message(StateFilter(AuthState.get_contact), F.contact)
async def process_auth_with_contact(message: Message, state: FSMContext, session: AsyncSession):
    try:
        customer = await get_customer_by_phone(session, state, message.contact.phone_number)
        valid_canteens = await get_valid_canteens(session, customer)
        if len(valid_canteens) > 1:
            await state.set_state(AuthState.get_canteen)
            msg = await message.answer(
                text='Выберите столовую, в которой будете заказывать еду:',
                reply_markup=show_canteens_kb(valid_canteens)
            )
        else:
            await state.set_state(AuthState.get_place)
            msg = await message.answer(
                text='Выберите место доставки:',
                reply_markup=await show_places_kb(session, *valid_canteens)
            )
        await add_message_to_track(msg, state)
    except IsNotCustomer:
        await state.clear()
        await message.answer(
            text='Вас нет в списке заказчиков столовой. Обратитесь в поддержку.',
        )
    finally:
        await message.delete()


@router.message(StateFilter(AuthState.get_contact), ~F.contact)
async def process_auth_no_contact(message: Message):
    await message.answer('Необходимо дать доступ к контактным данным.'
                         'Иначе авторизация невозможна.')


@router.message(StateFilter(AuthState.get_canteen))
@router.message(StateFilter(AuthState.get_place))
async def process_no_canteen(message: Message, session: AsyncSession, state: FSMContext):
    msg = await message.answer(
        text='Для продолжения авторизации необходимо следовать инструкции'
    )
    await add_message_to_track(msg, state)


@router.callback_query(StateFilter(AuthState.get_place), F.data.startswith('canteen'))
@router.callback_query(StateFilter(AuthState.get_canteen))
async def process_get_canteen(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    markup = await show_places_kb(session, callback=callback)
    current_state = await state.get_state()
    message_text = 'Выберите место доставки еды:'
    if current_state == AuthState.get_canteen:
        await state.set_state(AuthState.get_place)
        msg = await callback.message.answer(
            text=message_text,
            reply_markup=markup
        )
        await add_message_to_track(msg, state)
        await set_track_callback(callback, msg, state)
    else:
        track_cb = await get_track_callback(state)
        if track_cb.callback_data != callback.data:
            await track_cb.message.edit_text(
                text=message_text,
                reply_markup=markup
            )
            await update_track_callback(track_cb, callback, state)
    await callback.answer()


@router.callback_query(StateFilter(AuthState.get_place), F.data.startswith('place'))
async def process_get_place(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await update_customer_data(session, callback, state)
    await callback.message.answer(
        text='Готов принять ваш первый заказ.',
        reply_markup=initial_kb()
    )
    await callback.answer(
        text='Вы успешно авторизовались!',
        show_alert=True
    )
    await terminate_state_branch(callback.message, state, add_last=False)


@router.message(F.text == 'Изменить место доставки', StateFilter(default_state))
async def process_settings(message: Message, session: AsyncSession, state: FSMContext):
    try:
        customer = await get_customer_by_tg_id(session, state, message.from_user.id)
        valid_canteens = await get_valid_canteens(session, customer)
        if len(valid_canteens) > 1:
            await state.set_state(AuthState.get_canteen)
            await message.answer(
                text='Выберите столовую:',
                reply_markup=show_canteens_kb(valid_canteens)
            )
        else:
            await state.set_state(AuthState.get_place)
            await message.answer(
                text='Выберите новое место доставки:',
                reply_markup=await show_places_kb(session, *valid_canteens)
            )
    except IsNotCustomer:
        await message.answer(
            text='Вас больше нет в списке заказчиков. Вам необходимо заново пройти авторизацию.',
            reply_markup=authorization_kb()
        )
    finally:
        await message.delete()
