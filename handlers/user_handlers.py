from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from sqlalchemy.ext.asyncio import AsyncSession
from keyboards.reply import authorization_kb, initial_kb
from keyboards.inline import show_canteens_kb, show_places_kb, show_settings_kb
from states.user_states import AuthState, SettingsState
from services.user_services import (is_auth, get_customer_by_phone, get_id_from_callback, update_customer_data,
                                    get_customer_by_tg_id)


router = Router()


@router.message(CommandStart(), StateFilter(default_state))
async def process_start(message: Message, state: FSMContext, session: AsyncSession):
    if not await is_auth(session, message.from_user.id):
        await state.set_state(AuthState.get_contact)
        await message.answer('Для продолжения работы необходимо авторизоваться.',
                             reply_markup=authorization_kb())
    else:
        await message.answer('Теперь вы можете сделать заказ', reply_markup=initial_kb())


@router.message(StateFilter(AuthState.get_contact), F.contact)
async def process_auth_with_contact(message: Message, state: FSMContext, session: AsyncSession):
    phone_number = message.contact.phone_number
    print(phone_number)
    customer = await get_customer_by_phone(session, phone_number)
    if customer:
        await state.update_data(customer_id=customer.id)
        await state.set_state(AuthState.get_canteen)
        await message.answer(
            text='Выберите столовую, в которой будете заказывать еду:',
            reply_markup=await show_canteens_kb(session)
        )
        await message.delete()
    else:
        await message.answer(
            text='Вас нет в списке заказчиков столовой. Обратитесь в поддержку.',
        )


@router.message(StateFilter(AuthState.get_contact), ~F.contact)
async def process_auth_no_contact(message: Message):
    await message.answer('Необходимо дать доступ к контактным данным.'
                         'Иначе авторизация невозможна')


@router.message(StateFilter(AuthState.get_canteen))
async def process_no_canteen(message: Message, session: AsyncSession):
    await message.answer(
        text='Для продолжения выберите столовую:',
        reply_markup=await show_canteens_kb(session)
    )


@router.callback_query(StateFilter(AuthState.get_place), F.data.startswith('canteen'))
@router.callback_query(StateFilter(AuthState.get_canteen))
async def process_get_canteen(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    canteen_id = get_id_from_callback(callback)
    current_state = await state.get_state()
    message_text = 'Выберите место доставки еды:'
    if current_state == AuthState.get_canteen:
        await state.set_state(AuthState.get_place)
        msg = await callback.message.answer(
            text=message_text,
            reply_markup=await show_places_kb(session, canteen_id)
        )
        await state.update_data(target_message=msg)
        await state.update_data(cb_data=callback.data)
    else:
        data = await state.get_data()
        msg: Message = data.get('target_message')
        cb_data = data.get('cb_data')
        if cb_data != callback.data:
            await msg.edit_text(
                text=message_text,
                reply_markup=await show_places_kb(session, canteen_id)
            )
            await state.update_data(cb_data=callback.data)
    await callback.answer()


@router.callback_query(StateFilter(AuthState.get_place), F.data.startswith('place'))
async def process_get_place(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    place_id = get_id_from_callback(callback)
    tg_id = callback.from_user.id
    data = await state.get_data()
    await update_customer_data(
        session=session,
        customer_id=data.get('customer_id'),
        tg_id=tg_id,
        place_id=place_id
    )
    await state.clear()
    await callback.message.answer(
        text='Вы успешно авторизовались. Теперь можно заказывать еду.',
        reply_markup=initial_kb()
    )


@router.message(F.text == 'Настройки', StateFilter(default_state))
async def process_settings(message: Message, session: AsyncSession, state: FSMContext):
    customer = await get_customer_by_tg_id(session, message.from_user.id)
    if customer:
        await state.set_state(SettingsState.get_option)
        await state.update_data(customer_id=customer.id)
        await message.answer(
            text='Варианты настроек:',
            reply_markup=show_settings_kb()
        )
    else:
        await message.answer(
            text='Вас больше нет в списке заказчиков. Вам необходимо заново пройти авторизацию.',
            reply_markup=authorization_kb()
        )


@router.callback_query(StateFilter(SettingsState.get_option), F.data == 'change_place')
async def process_change_place_setting(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await state.set_state(SettingsState.set_option)
    await callback.message.answer(
        text='Выберите столовую для заказа еды',
        reply_markup=await show_canteens_kb(session)
    )
    await callback.answer()




