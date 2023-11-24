import asyncio
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from sqlalchemy.ext.asyncio import AsyncSession
from keyboards.inline import order_menu_kb, dish_count_kb, inline_confirm_cancel_kb,delete_order_kb
from keyboards.reply import confirm_cancel_kb
from states.order_states import NewOrderState, CancelOrderState
from services.other_services import (initiate_track_messages, add_message_to_track, erase_track_messages,
                                     terminate_state_branch)
from services.user_services import get_customer_by_tg_id
from services.order_services import (get_menu_positions, get_menu_position_by_id,
                                     get_orders_by_customer, get_menu_by_id, delete_order, create_order_form,
                                     remember_position, load_position, set_order_amt,
                                     add_position_to_order_form, confirm_pending_order, increment_position_qty)
from exceptions import InvalidPositionQuantity, InvalidOrderMenu
from presentation.order_views import full_order_view, position_view


router = Router()


@router.message(F.text == 'Сделать новый заказ', StateFilter(default_state))
async def process_new_order(message: Message, session: AsyncSession, state: FSMContext):
    customer = await get_customer_by_tg_id(session, message.from_user.id)
    if customer:
        msg = await message.answer(
            text='Выберите меню для заказа:',
            reply_markup=await order_menu_kb(session, customer_id=customer.id)
        )
        await initiate_track_messages(msg, state)
        await create_order_form(customer.id, state)
        await state.set_state(NewOrderState.menu_choice)
    else:
        await message.answer(
            text='Вас больше нет в списке заказчиков. Пройдите повторную авторизацию.'
                 'Для этого выберите в меню команду /start',
            reply_markup=ReplyKeyboardRemove()
        )


@router.callback_query(StateFilter(NewOrderState.menu_choice))
async def new_order_positions(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    positions = await get_menu_positions(session, callback, state)
    for position in positions:
        msg = await callback.message.answer(
            text=position_view(position),
            reply_markup=dish_count_kb()
        )
        await add_message_to_track(msg, state)
        await remember_position(msg, state, position)
        await asyncio.sleep(0.1)
    await state.set_state(NewOrderState.dish_choice)
    cb_msg = await callback.message.answer(
        text='После добавления блюд нажмите Подтвердить, чтобы сохранить заказ.\n'
             'Для отмены заказа нажмите Отменить.',
        reply_markup=confirm_cancel_kb()
    )
    await add_message_to_track(cb_msg, state)
    await callback.answer()


@router.callback_query(StateFilter(NewOrderState.dish_choice), F.data.in_(['plus', 'minus']))
async def change_quantity_of_position(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    position = await load_position(state, callback.message)
    try:
        increment_position_qty(position, callback.data)
        await callback.message.edit_text(
            text=f'{position.name}\nКол-во: {position.quantity}\nСтоимость: {position.quantity * position.cost}',
            reply_markup=dish_count_kb()
        )
    except InvalidPositionQuantity:
        await callback.answer(
            text='Количество не может быть меньше 1'
        )
    await callback.answer()


@router.callback_query(StateFilter(NewOrderState.dish_choice), F.data == 'add')
async def add_new_position_to_order(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    await add_position_to_order_form(callback, state)
    await callback.answer(
        text='Позиция успешно добавлена',
        show_alert=True
    )
    await callback.message.delete()


@router.message(StateFilter(NewOrderState.dish_choice), F.text == 'Подтвердить')
async def process_order_info(message: Message, session: AsyncSession, state: FSMContext):
    order_form = await set_order_amt(state)
    await state.set_state(NewOrderState.check_status)
    msg1 = await message.answer(
        text='Проверьте свой заказ:',
        reply_markup=ReplyKeyboardRemove()
    )
    await add_message_to_track(msg1, state)
    msg2 = await message.answer(
        text=await full_order_view(order_form),
        reply_markup=inline_confirm_cancel_kb()
    )
    await add_message_to_track(msg2, state)


@router.message(StateFilter(NewOrderState.dish_choice), F.text == 'Отменить')
async def process_cancel_order(message: Message, session: AsyncSession, state: FSMContext):
    await message.answer(
        text='Заполнение заказа отменено',
        reply_markup=ReplyKeyboardRemove()
    )
    await terminate_state_branch(message, state, add_last=False)


@router.callback_query(StateFilter(NewOrderState.check_status), F.data == 'save')
async def process_pending_new_order(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    try:
        await confirm_pending_order(session, state)
        await callback.answer(
            text='Ваш заказ отправлен',
            show_alert=True
        )
    except InvalidOrderMenu:
        await callback.answer(
            text='Срок для заказа истек.',
            show_alert=True
        )
    finally:
        await terminate_state_branch(callback.message, state)


@router.callback_query(StateFilter(NewOrderState.check_status), F.data == 'cancel')
async def process_cancel_new_order(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    await callback.answer(
        text='Заказ отменен',
        show_alert=True
    )
    await terminate_state_branch(callback.message, state)


@router.message(StateFilter(default_state), F.text == 'Отменить заказ')
async def process_delete_order(message: Message, session: AsyncSession, state: FSMContext):
    customer = await get_customer_by_tg_id(session, message.from_user.id)
    orders = await get_orders_by_customer(session, customer.id)
    for order in orders:
        order_text_list = []
        menu = await get_menu_by_id(session, order.menu_id)
        order_text_list.append(f'Заказ {menu.name} на {menu.date}. Сделан {order.date}.\n')
        for detail in order.details:
            menu_pos = await get_menu_position_by_id(session, detail.menu_pos_id)
            order_text_list.append(f'{menu_pos.name} Кол-во: {detail.quantity}')
        order_text_list.append(f'Итого: {order.amt}')
        msg = await message.answer(
            text='\n'.join(order_text_list),
            reply_markup=delete_order_kb()
        )
        await state.update_data({str(msg.message_id): order})
    await state.set_state(CancelOrderState.order_choices)


@router.callback_query(StateFilter(CancelOrderState.order_choices), F.data == 'delete_order')
async def process_delete_order(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    data = await state.get_data()
    order = data.get(str(callback.message.message_id))
    await delete_order(session, order)
    await callback.answer(
        text='Заказ успешно удален',
        show_alert=True
    )
    await state.clear()
    await callback.message.delete()



















