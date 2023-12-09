from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, default_state
from sqlalchemy.ext.asyncio import AsyncSession
from services.user_services import get_customer_from_msg, get_valid_canteens
from services.other_services import add_message_to_track, set_track_callback, get_track_callback, update_track_callback
from keyboards.inline import show_canteens_kb, show_places_kb
from exceptions import IsNotCustomer, ValidCanteensNotExist


async def process_choice_canteens_or_places(
        message: Message,
        state: FSMContext,
        session: AsyncSession,
        canteen_state: State,
        place_state: State):
    current_state = state.get_state()
    try:
        customer = await get_customer_from_msg(session, state, message)
        valid_canteens = await get_valid_canteens(session, customer)
        if len(valid_canteens) > 1:
            await state.set_state(canteen_state)
            msg = await message.answer(
                text='Выберите столовую, в которой будете заказывать еду:',
                reply_markup=show_canteens_kb(valid_canteens)
            )
        else:
            await state.set_state(place_state)
            msg = await message.answer(
                text='Выберите место доставки:',
                reply_markup=await show_places_kb(session, *valid_canteens)
            )
        await add_message_to_track(msg, state)
    except IsNotCustomer:
        if current_state != default_state:
            await state.clear()
        await message.answer(
            text='Вас нет в списке заказчиков столовой.',
            reply_markup=ReplyKeyboardRemove()
        )
    except ValidCanteensNotExist:
        if current_state != default_state:
            await state.clear()
        await message.answer(
            text='У вас истек срок разрешения для заказа еды.',
            reply_markup=ReplyKeyboardRemove()
        )
    finally:
        await message.delete()


async def process_choice_delivery_place(
        callback: CallbackQuery,
        state: FSMContext,
        session: AsyncSession,
        canteen_state: State,
        place_state: State):
    markup = await show_places_kb(session, callback=callback)
    current_state = await state.get_state()
    message_text = 'Выберите новое место доставки еды:'
    if current_state == canteen_state:
        await state.set_state(place_state)
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

