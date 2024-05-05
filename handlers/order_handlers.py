from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from sqlalchemy.ext.asyncio import AsyncSession
from keyboards.inline import (order_menu_kb, dish_count_kb_new, inline_confirm_cancel_kb,
                              order_delete_scroll_kb, order_view_scroll_kb)
from keyboards.reply import confirm_cancel_kb, back_to_initial_kb, initial_kb
from states.order_states import NewOrderState, CancelOrderState, OrdersViewState
from services.other_services import terminate_state_branch
from exceptions import (InvalidPositionQuantity, ValidMenusNotExist, IsNotCustomer,
                        OrdersNotExist, NoPositionsSelected, InvalidOrder, EmptyException)
from presentation.order_views import position_view_new, order_view
from presentation.responses import message_response, callback_response, edit_response
from middlewares import ServiceManagerMiddleware
from services.managers import OrderManager

router = Router()
router.message.middleware(ServiceManagerMiddleware(OrderManager))
router.callback_query.middleware(ServiceManagerMiddleware(OrderManager))


@router.message(F.text.endswith('Новый заказ'), StateFilter(default_state))
async def process_new_order(
        message: Message, session: AsyncSession, state: FSMContext, manager: OrderManager) -> None:
    text = 'Произошла ошибка при инициализации нового заказа.'
    reply_markup = None
    try:
        await manager.start_process_new_order(session, state, message)
        valid_menus = await manager.receive_valid_menus(session, state)
        await state.set_state(NewOrderState.menu_choice)
        text = 'Выберите меню для заказа:'
        reply_markup = order_menu_kb(valid_menus)
    except ValidMenusNotExist:
        text = 'Нет доступных меню для заказа'
        reply_markup = initial_kb()
    except IsNotCustomer:
        text = ('Вас больше нет в списке заказчиков. Пройдите повторную авторизацию. '
                'Для этого выберите в меню команду /start')
        reply_markup = ReplyKeyboardRemove()
    finally:
        await message_response(
            message=message,
            text=text,
            reply_markup=reply_markup,
            state=state
        )


@router.message(
    ~StateFilter(default_state), F.text.endswith('Просмотр/Удаление заказов') | F.text.endswith('Новый заказ'))
async def process_menu_button_with_context(message: Message) -> None:
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
    await process_positions_response(callback.message, state, positions)
    await state.set_state(NewOrderState.dish_choice)
    await message_response(
        message=callback.message,
        text='После добавления блюд нажмите <b><i>Подтвердить</i></b>, чтобы сохранить заказ. '
             'Для продолжения вывода позиций меню нажмите на кнопку <b><i>Продолжить список</i></b>.'
             'Для отмены заказа нажмите <b><i>Отменить</i></b>.',
        reply_markup=confirm_cancel_kb(),
        state=state
    )
    await callback_response(callback)


@router.message(StateFilter(NewOrderState.dish_choice), F.text.endswith('Заказать стандартный комплекс'))
async def process_standard_complex(
        message: Message, session: AsyncSession, state: FSMContext, manager: OrderManager) -> None:
    try:
        order = await manager.receive_complex_order(session, state)
        await state.set_state(NewOrderState.check_status)
        await process_new_order_info_response(message, state, order)
    except NoPositionsSelected:
        await message_response(
            message=message,
            text='В данном меню нет комплексных позиций.',
            reply_markup=ReplyKeyboardRemove(),
            state=state
        )


@router.message(StateFilter(NewOrderState.dish_choice), F.text.endswith('Продолжить список'))
async def process_continue_positions(message: Message, state: FSMContext, manager: OrderManager) -> None:
    try:
        positions = await manager.continue_receiving_positions(state)
        await process_positions_response(message, state, positions)
    except EmptyException:
        await message_response(
            message=message,
            text='Все доступные позиции выведены.',
            state=state
        )


@router.callback_query(StateFilter(NewOrderState.dish_choice), F.data.startswith('minus') | F.data.startswith('plus'))
async def change_quantity_of_position(
        callback: CallbackQuery, state: FSMContext, manager: OrderManager) -> None:
    text = None
    try:
        position = await manager.increment_position_quantity(callback, state)
        await edit_response(
            message=callback.message,
            text=position_view_new(position),
            reply_markup=dish_count_kb_new(position)
        )
    except InvalidPositionQuantity:
        text = 'Количество не может быть меньше 1'
    finally:
        await callback_response(callback, text=text)


@router.callback_query(StateFilter(NewOrderState.dish_choice), F.data.startswith('add'))
async def add_new_position_to_order(
        callback: CallbackQuery, state: FSMContext, manager: OrderManager) -> None:
    await manager.add_position_to_order(callback, state)
    await callback_response(
        callback=callback,
        text='Позиция успешно добавлена',
        show_alert=True,
        delete_after=True
    )


@router.message(StateFilter(NewOrderState.dish_choice), F.text.endswith('Подтвердить'))
async def process_order_info(
        message: Message, state: FSMContext, manager: OrderManager) -> None:
    try:
        order = manager.receive_full_order()
        await state.set_state(NewOrderState.check_status)
        await process_new_order_info_response(message, state, order)
    except NoPositionsSelected:
        await message_response(
            message=message,
            text='Вы не выбрали ни одной позиции для заказа. '
                 'Выберите необходимые позиции или отмените заполнение заказа с помощью кнопки <b><i>Отменить</i></b>',
            reply_markup=confirm_cancel_kb(),
            state=state
        )


@router.message(StateFilter(NewOrderState.dish_choice), F.text.endswith('Отменить'))
async def process_cancel_order(message: Message, state: FSMContext) -> None:
    await terminate_state_branch(message, state, add_last=False)
    await message_response(
        message=message,
        text='Возврат в главное меню',
        reply_markup=initial_kb()
    )


@router.callback_query(StateFilter(NewOrderState.check_status), F.data == 'save')
async def process_pending_new_order(
        callback: CallbackQuery, session: AsyncSession, state: FSMContext, manager: OrderManager) -> None:
    text = ('Произошла ошибка при сохранении заказа. '
            'Попробуйте еще раз или нажмите /cancel для возврата в главное меню')
    try:
        await manager.confirm_pending_order(session)
        text = 'Ваш заказ отправлен'
    except InvalidOrder:
        text = 'Заказ не может быть отправлен.'
    finally:
        await callback_response(
            callback=callback,
            text=text,
            show_alert=True
        )
        await terminate_state_branch(callback.message, state)
        await message_response(
            message=callback.message,
            text='Возврат в главное меню',
            reply_markup=initial_kb()
        )


@router.callback_query(StateFilter(NewOrderState.check_status), F.data == 'cancel')
async def process_cancel_new_order(callback: CallbackQuery, state: FSMContext) -> None:
    await callback_response(
        callback=callback,
        text='Заказ отменен',
        show_alert=True
    )
    await terminate_state_branch(callback.message, state)
    await message_response(
        message=callback.message,
        text='Возврат в главное меню',
        reply_markup=initial_kb()
    )


@router.message(StateFilter(default_state), F.text.endswith('Просмотр заказов'))
async def process_orders_history(
        message: Message, session: AsyncSession, state: FSMContext, manager: OrderManager) -> None:
    await process_view_orders(
        message=message,
        session=session,
        state=state,
        manager=manager,
        no_orders_text='У вас пока нет заказов.',
        new_state=OrdersViewState.order_views,
        markup_func=order_view_scroll_kb
    )


@router.message(StateFilter(default_state), F.text.endswith('Удаление активных заказов'))
async def process_delete_order(
        message: Message, session: AsyncSession, state: FSMContext, manager: OrderManager) -> None:
    await process_view_orders(
        message=message,
        session=session,
        state=state,
        manager=manager,
        no_orders_text='У вас нет активных заказов.',
        new_state=CancelOrderState.order_choices,
        markup_func=order_delete_scroll_kb,
        valid_orders=True
    )


@router.callback_query(
    StateFilter(OrdersViewState.order_views), F.data.startswith('prev') | F.data.startswith('next'))
@router.callback_query(
    StateFilter(CancelOrderState.order_choices), F.data.startswith('prev') | F.data.startswith('next'))
async def process_listing_orders(
        callback: CallbackQuery, state: FSMContext, manager: OrderManager) -> None:
    await manager.process_scroll(callback, state)
    await edit_order_response(callback, state, manager)


@router.callback_query(StateFilter(CancelOrderState.order_choices), F.data.startswith('delete'))
async def process_delete_order(
        callback: CallbackQuery, session: AsyncSession, manager: OrderManager, state: FSMContext) -> None:
    if order := await manager.valid_order_to_delete(state):
        await manager.cancel_order(session, order)
        text = 'Заказ успешно удален'
    else:
        text = 'Заказ не может быть удален'
    await callback_response(
        callback=callback,
        text=text,
        show_alert=True,
    )
    try:
        await edit_order_response(callback, state, manager)
    except EmptyException:
        await message_response(
            message=callback.message,
            text='Все заказы удалены. Возврат в главное меню.',
            reply_markup=initial_kb(),
            delete_after=True
        )
        await terminate_state_branch(callback.message, state, add_last=False)


@router.message(StateFilter(OrdersViewState.order_views), F.text.endswith('Вернуться в главное меню'))
@router.message(StateFilter(CancelOrderState.order_choices), F.text.endswith('Вернуться в главное меню'))
async def process_back_to_main_menu(message: Message, state: FSMContext) -> None:
    await message_response(
        message=message,
        text='Возврат в главное меню',
        reply_markup=initial_kb()
    )
    await terminate_state_branch(message, state)


async def edit_order_response(callback: CallbackQuery, state: FSMContext, manager: OrderManager) -> None:
    markup = None
    current_state = await state.get_state()
    match current_state:
        case OrdersViewState.order_views:
            markup = order_view_scroll_kb(manager.current_order_position())
        case CancelOrderState.order_choices:
            markup = order_delete_scroll_kb(manager.current_order_position())
    await edit_response(
        message=callback.message,
        text=order_view(manager.current_order()),
        reply_markup=markup
    )


async def process_new_order_info_response(message: Message, state: FSMContext, order) -> None:
    await message_response(
        message=message,
        text='Проверьте свой заказ:',
        reply_markup=ReplyKeyboardRemove(),
        state=state
    )
    await message_response(
        message=message,
        text=order_view(order),
        reply_markup=inline_confirm_cancel_kb(),
        state=state
    )


async def process_positions_response(message: Message, state: FSMContext, positions) -> None:
    for position in positions:
        await message_response(
            message=message,
            text=position_view_new(position),
            reply_markup=dish_count_kb_new(position),
            state=state,
            delay=0.1
        )


async def process_view_orders(
        message: Message,
        session: AsyncSession,
        state: FSMContext,
        manager: OrderManager,
        no_orders_text: str,
        new_state,
        markup_func,
        valid_orders: bool = False
) -> None:
    text = 'Произошла ошибка. Нажмите на команду /start, чтобы попробовать снова.'
    reply_markup = None
    in_state = False
    try:
        await manager.receive_customer_orders(session, message, state, valid=valid_orders)
        await state.set_state(new_state)
        await message_response(
            message=message,
            text=order_view(manager.current_order()),
            reply_markup=markup_func(manager.current_order_position()),
            state=state
        )
        text = 'Для возвращения в главное меню нажмите на кнопку <b><i>Вернуться в главное меню</i></b>'
        reply_markup = back_to_initial_kb()
        in_state = True
    except IsNotCustomer:
        text = ('Вас больше нет в списке заказчиков. Пройдите повторную авторизацию. '
                'Для этого выберите в меню команду /start')
        reply_markup = ReplyKeyboardRemove()
    except OrdersNotExist:
        text = no_orders_text
        reply_markup = initial_kb()
    finally:
        await message_response(
            message=message,
            text=text,
            reply_markup=reply_markup,
            state=state if in_state else None
        )
