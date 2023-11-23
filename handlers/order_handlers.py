import datetime

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from sqlalchemy.ext.asyncio import AsyncSession
from keyboards.inline import order_menu_kb, dish_count_kb, inline_confirm_cancel_kb,delete_order_kb
from keyboards.reply import confirm_cancel_kb, authorization_kb
from states.order_states import NewOrderState, CancelOrderState
from services.other_services import get_id_from_callback, initiate_track_messages, add_message_to_track
from services.user_services import get_customer_by_tg_id
from services.order_services import (get_menu_positions_by_menu, get_menu_position_by_id, save_new_order,
                                     get_orders_by_customer, get_menu_by_id, delete_order, create_order_form,
                                     add_menu_id_to_order_form, remember_position, load_position,
                                     add_position_to_order_form, create_order_from_form, get_order_form)
from database.models import OrderDetail, MenuPosition, Order


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
    menu_id = get_id_from_callback(callback)
    await add_menu_id_to_order_form(menu_id, state)
    positions = await get_menu_positions_by_menu(session, menu_id)
    for position in positions:
        position.qty = 1
        msg = await callback.message.answer(
            text=f'{position.name}\nКол-во: {position.qty}\nСтоимость: {position.qty*position.cost}',
            reply_markup=dish_count_kb()
        )
        await add_message_to_track(msg, state)
        await remember_position(msg, state, position)
    await state.set_state(NewOrderState.dish_choice)
    await callback.message.answer(
        text='После добавления блюд нажмите Подтвердить, чтобы сохранить заказ.\n'
             'Для отмены заказа нажмите Отменить.',
        reply_markup=confirm_cancel_kb()
    )
    await callback.answer()


@router.callback_query(StateFilter(NewOrderState.dish_choice), F.data.in_(['plus', 'minus']))
async def change_quantity_of_position(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    position = await load_position(state, callback.message)
    if callback.data == 'plus':
        position.qty += 1
    else:
        position.qty -= 1
    await callback.message.edit_text(
        text=f'{position.name}\nКол-во: {position.qty}\nСтоимость: {position.qty * position.cost}',
        reply_markup=dish_count_kb()
    )
    await callback.answer()


@router.callback_query(StateFilter(NewOrderState.dish_choice), F.data == 'add')
async def add_new_position_to_order(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    position = await load_position(state, callback.message)
    await add_position_to_order_form(position, state)
    await callback.answer(
        text='Позиция успешно добавлена',
        show_alert=True
    )
    await callback.message.delete()


@router.message(StateFilter(NewOrderState.dish_choice), F.text == 'Подтвердить')
async def create_full_order(message: Message, session: AsyncSession, state: FSMContext):
    data = await state.get_data()
    details: list[OrderDetail] = data.get('details')
    text_list = []
    costs = []
    for detail in details:
        position = await get_menu_position_by_id(session, detail.menu_pos_id)
        cost = position.cost * detail.quantity
        costs.append(cost)
        text_list.append(f'{position.name} Кол-во: {detail.quantity} Стоимость: {cost}')
    amt = sum(costs)
    text_list.append(f'Общая стоимость заказа: {amt}')
    await state.update_data(amt=amt)
    await state.set_state(NewOrderState.check_status)
    await message.answer(
        text='Проверьте свой заказ:',
        reply_markup=ReplyKeyboardRemove()
    )
    await message.answer(
        text='\n\n'.join(text_list),
        reply_markup=inline_confirm_cancel_kb()
    )


@router.callback_query(StateFilter(NewOrderState.check_status), F.data == 'save')
async def process_save_new_order(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    order_form = await get_order_form(state)
    order = await create_order_from_form(order_form)
    await save_new_order(session, order)
    await state.clear()
    await callback.answer(
        text='Ваш заказ отправлен',
        show_alert=True
    )
    await callback.message.delete()


@router.callback_query(StateFilter(NewOrderState.check_status), F.data == 'cancel')
async def process_cancel_new_order(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    await state.clear()
    await callback.answer(
        text='Заказ отменен',
        show_alert=True
    )
    await callback.message.delete()


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



















