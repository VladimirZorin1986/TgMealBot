import asyncio
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from sqlalchemy.ext.asyncio import AsyncSession
from keyboards.inline import order_menu_kb, dish_count_kb_new, inline_confirm_cancel_kb, delete_order_kb_new
from keyboards.reply import confirm_cancel_kb, back_to_initial_kb, initial_kb
from states.order_states import NewOrderState, CancelOrderState
from services.other_services import add_message_to_track, terminate_state_branch
from exceptions import (InvalidPositionQuantity, ValidMenusNotExist, IsNotCustomer,
                        ValidOrdersNotExist, NoPositionsSelected, InvalidOrder)
from presentation.order_views import position_view_new, order_view
from presentation.responses import message_response
from middlewares.local_middlewares import ServiceManagerMiddleware
from services.managers import OrderManager

router = Router()
router.message.middleware(ServiceManagerMiddleware(OrderManager))
router.callback_query.middleware(ServiceManagerMiddleware(OrderManager))


@router.message(F.text.endswith('Новый заказ'), StateFilter(default_state))
async def process_new_order(
        message: Message, session: AsyncSession, state: FSMContext, manager: OrderManager) -> None:
    try:
        await manager.start_process_new_order(session, state, message)
        valid_menus = await manager.receive_valid_menus(session, state)
        await state.set_state(NewOrderState.menu_choice)
        await message_response(
            message=message,
            text='Выберите меню для заказа:',
            reply_markup=order_menu_kb(valid_menus),
            state=state
        )
    except ValidMenusNotExist:
        await message_response(
            message=message,
            text='Нет доступных меню для заказа',
            reply_markup=initial_kb()
        )
    except IsNotCustomer:
        await message_response(
            message=message,
            text='Вас больше нет в списке заказчиков. Пройдите повторную авторизацию.'
                 'Для этого выберите в меню команду /start',
            reply_markup=ReplyKeyboardRemove()
        )


@router.message(
    ~StateFilter(default_state), F.text.endswith('Просмотр/Удаление заказов') | F.text.endswith('Новый заказ'))
async def process_menu_button_with_context(message: Message):
    await message_response(
        message=message,
        text='Сначала закончите выполняемое действие. '
             'Для отмены действия нажмите на команду /cancel',
        reply_markup=ReplyKeyboardRemove()
    )


@router.callback_query(StateFilter(NewOrderState.menu_choice))
async def new_order_positions(
        callback: CallbackQuery, session: AsyncSession, state: FSMContext, manager: OrderManager) -> None:
    positions = await manager.receive_menu_positions(session, callback, state)
    for position in positions:
        msg = await callback.message.answer(
            text=position_view_new(position),
            reply_markup=dish_count_kb_new(position)
        )
        await add_message_to_track(msg, state)
        await asyncio.sleep(0.3)
    await state.set_state(NewOrderState.dish_choice)
    cb_msg = await callback.message.answer(
        text='После добавления блюд нажмите <b><i>Подтвердить</i></b>, чтобы сохранить заказ. '
             'Для отмены заказа нажмите <b><i>Отменить</i></b>.',
        reply_markup=confirm_cancel_kb()
    )
    await add_message_to_track(cb_msg, state)
    await callback.answer()


@router.callback_query(StateFilter(NewOrderState.dish_choice), F.data.startswith('minus') | F.data.startswith('plus'))
async def change_quantity_of_position(
        callback: CallbackQuery, state: FSMContext, manager: OrderManager):
    try:
        position = await manager.increment_position_quantity(callback, state)
        await callback.message.edit_text(
            text=position_view_new(position),
            reply_markup=dish_count_kb_new(position)
        )
    except InvalidPositionQuantity:
        await callback.answer(
            text='Количество не может быть меньше 1'
        )
    await callback.answer()


@router.callback_query(StateFilter(NewOrderState.dish_choice), F.data.startswith('add'))
async def add_new_position_to_order(
        callback: CallbackQuery, state: FSMContext, manager: OrderManager) -> None:
    await manager.add_position_to_order(callback, state)
    await callback.answer(
        text='Позиция успешно добавлена',
        show_alert=True
    )
    await callback.message.delete()


@router.message(StateFilter(NewOrderState.dish_choice), F.text.endswith('Подтвердить'))
async def process_order_info(
        message: Message, state: FSMContext, manager: OrderManager):
    try:
        order = manager.receive_full_order()
        await state.set_state(NewOrderState.check_status)
        msg1 = await message.answer(
            text='Проверьте свой заказ:',
            reply_markup=ReplyKeyboardRemove()
        )
        await add_message_to_track(msg1, state)
        msg2 = await message.answer(
            text=order_view(order),
            reply_markup=inline_confirm_cancel_kb()
        )
        await add_message_to_track(msg2, state)
    except NoPositionsSelected:
        await message.answer(
            text='Вы не выбрали ни одной позиции для заказа. '
                 'Выберите необходимые позиции или отмените заполнение заказа с помощью кнопки <b><i>Отменить</i></b>',
            reply_markup=confirm_cancel_kb()
        )


@router.message(StateFilter(NewOrderState.dish_choice), F.text.endswith('Отменить'))
async def process_cancel_order(message: Message, state: FSMContext):
    await terminate_state_branch(message, state, add_last=False)
    await message.answer(
        text='Возврат в главное меню',
        reply_markup=initial_kb()
    )


@router.callback_query(StateFilter(NewOrderState.check_status), F.data == 'save')
async def process_pending_new_order(
        callback: CallbackQuery, session: AsyncSession, state: FSMContext, manager: OrderManager):
    try:
        await manager.confirm_pending_order(session)
        await callback.answer(
            text='Ваш заказ отправлен',
            show_alert=True
        )
    except InvalidOrder:
        await callback.answer(
            text='Заказ не может быть отправлен.',
            show_alert=True
        )
    finally:
        await terminate_state_branch(callback.message, state)
        await callback.message.answer(
            text='Возврат в главное меню',
            reply_markup=initial_kb()
        )


@router.callback_query(StateFilter(NewOrderState.check_status), F.data == 'cancel')
async def process_cancel_new_order(callback: CallbackQuery, state: FSMContext):
    await callback.answer(
        text='Заказ отменен',
        show_alert=True
    )
    await terminate_state_branch(callback.message, state)
    await callback.message.answer(
        text='Возврат в главное меню',
        reply_markup=initial_kb()
    )


@router.message(StateFilter(default_state), F.text.endswith('Просмотр/Удаление заказов'))
async def process_delete_order(
        message: Message, session: AsyncSession, state: FSMContext, manager: OrderManager):
    try:
        orders = await manager.receive_customer_orders(session, message)
        for order in orders:
            msg = await message.answer(
                text=order_view(order),
                reply_markup=delete_order_kb_new(order)
            )
            await add_message_to_track(msg, state)
        await state.set_state(CancelOrderState.order_choices)
        await message.answer(
            text='Для возвращения в главное меню, после удаления выбранных заказов, нажмите на кнопку '
                 '<b><i>Вернуться в главное меню</i></b>',
            reply_markup=back_to_initial_kb()
        )
    except IsNotCustomer:
        await message.answer(
            text='Вас больше нет в списке заказчиков. Пройдите повторную авторизацию.'
                 'Для этого выберите в меню команду /start',
            reply_markup=ReplyKeyboardRemove()
        )
    except ValidOrdersNotExist:
        await message.answer(
            text='У вас нет активных заказов для удаления.',
            reply_markup=initial_kb()
        )


@router.callback_query(StateFilter(CancelOrderState.order_choices), F.data.startswith('order'))
async def process_delete_order(
        callback: CallbackQuery, session: AsyncSession, manager: OrderManager):
    await manager.cancel_order(session, callback)
    await callback.answer(
        text='Заказ успешно удален',
        show_alert=True
    )
    await callback.message.delete()


@router.message(StateFilter(CancelOrderState.order_choices), F.text.endswith('Вернуться в главное меню'))
async def process_back_to_main_menu(message: Message, state: FSMContext):
    await message.answer(
        text='Возврат в главное меню',
        reply_markup=initial_kb()
    )
    await terminate_state_branch(message, state)
