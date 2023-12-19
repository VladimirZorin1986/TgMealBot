from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from sqlalchemy.ext.asyncio import AsyncSession
from keyboards.reply import initial_kb
from keyboards.inline import show_canteens_kb, show_places_kb_new
from states.user_states import AuthState, ChangeDeliveryPlace
from services.other_services import (terminate_state_branch, set_track_callback,
                                     update_track_callback, get_track_callback)
from middlewares import ServiceManagerMiddleware
from services.managers import UserManager
from presentation.responses import message_response, callback_response, edit_response
from presentation.user_views import old_place_view
from exceptions import IsNotCustomer, ValidCanteensNotExist

router = Router()
router.message.middleware(ServiceManagerMiddleware(UserManager))
router.callback_query.middleware(ServiceManagerMiddleware(UserManager))


@router.message(StateFilter(AuthState.get_contact), F.contact)
async def process_auth_with_contact(
        message: Message, state: FSMContext, session: AsyncSession, manager: UserManager):
    await process_choice_canteens_places(
        message=message,
        state=state,
        session=session,
        manager=manager,
        canteen_state=AuthState.get_canteen,
        place_state=AuthState.get_place
    )


@router.message(StateFilter(AuthState.get_contact), ~F.contact)
async def process_auth_no_contact(message: Message):
    await message_response(
        message=message,
        text='Необходимо дать доступ к контактным данным. '
             'Иначе авторизация невозможна.'
    )


@router.message(StateFilter(AuthState.get_canteen))
@router.message(StateFilter(AuthState.get_place))
async def process_no_canteen(message: Message, state: FSMContext):
    await message_response(
        message=message,
        text='Для продолжения авторизации необходимо следовать инструкции. '
             'Если хотите отменить это действие нажмите на команду /cancel',
        state=state
    )


@router.callback_query(StateFilter(AuthState.get_place), F.data.startswith('canteen'))
@router.callback_query(StateFilter(AuthState.get_canteen))
async def process_set_place_auth(
        callback: CallbackQuery, state: FSMContext, session: AsyncSession, manager: UserManager):
    markup = show_places_kb_new(await manager.receive_canteen_places(session=session, callback=callback))
    current_state = await state.get_state()
    message_text = 'Выберите новое место доставки еды:'
    if current_state == AuthState.get_canteen:
        await state.set_state(AuthState.get_place)
        msg = await message_response(
            message=callback.message,
            text=message_text,
            reply_markup=markup,
            state=state,
            return_msg=True
        )
        await set_track_callback(callback, msg, state)
    else:
        track_cb = await get_track_callback(state)
        if track_cb.callback_data != callback.data:
            await edit_response(
                message=track_cb.message,
                text=message_text,
                reply_markup=markup
            )
            await update_track_callback(track_cb, callback, state)
    await callback_response(callback)


@router.callback_query(StateFilter(AuthState.get_place), F.data.startswith('place'))
async def process_get_place(
        callback: CallbackQuery, state: FSMContext, session: AsyncSession, manager: UserManager):
    await manager.authorize_customer(session, callback)
    await message_response(
        message=callback.message,
        text='Теперь вы можете сделать заказ.',
        reply_markup=initial_kb()
    )
    await callback_response(
        callback=callback,
        text='Вы успешно авторизовались!',
        show_alert=True
    )
    await terminate_state_branch(callback.message, state, add_last=False)


@router.message(F.text.endswith('Изменить место доставки'), StateFilter(default_state))
async def process_change_delivery_place(
        message: Message, session: AsyncSession, state: FSMContext, manager: UserManager):
    await process_choice_canteens_places(
        message=message,
        state=state,
        session=session,
        manager=manager,
        canteen_state=ChangeDeliveryPlace.set_new_canteen,
        place_state=ChangeDeliveryPlace.set_new_place
    )


@router.message(F.text.endswith('Изменить место доставки'), ~StateFilter(default_state))
async def process_menu_button_with_context(message: Message):
    await message_response(
        message=message,
        text='Сначала закончите выполняемое действие. '
             'Для отмены действия нажмите на команду /cancel',
        reply_markup=ReplyKeyboardRemove()
    )


@router.callback_query(StateFilter(ChangeDeliveryPlace.set_new_place), F.data.startswith('canteen'))
@router.callback_query(StateFilter(ChangeDeliveryPlace.set_new_canteen))
async def process_change_place(
        callback: CallbackQuery, state: FSMContext, session: AsyncSession, manager: UserManager):
    await process_choice_delivery_place(
        callback=callback,
        session=session,
        state=state,
        manager=manager,
        canteen_state=ChangeDeliveryPlace.set_new_canteen,
        place_state=ChangeDeliveryPlace.set_new_place
    )


@router.callback_query(StateFilter(ChangeDeliveryPlace.set_new_place), F.data.startswith('place'))
async def process_get_place(
        callback: CallbackQuery, state: FSMContext, session: AsyncSession, manager: UserManager):
    await manager.change_delivery_place(session, callback)
    await message_response(
        message=callback.message,
        text='Теперь вы можете сделать заказ.',
        reply_markup=initial_kb()
    )
    await callback_response(
        callback=callback,
        text='Место доставки успешно изменено!',
        show_alert=True
    )
    await terminate_state_branch(callback.message, state, add_last=False)


async def process_choice_canteens_places(
        message: Message,
        session: AsyncSession,
        state: FSMContext,
        manager: UserManager,
        canteen_state,
        place_state
) -> None:
    text = 'Произошла ошибка при обработке контактных данных.'
    reply_markup = None
    try:
        await manager.validate_customer(session, message, state)
        if manager.is_auth():
            place = await manager.receive_place(session)
            await message_response(
                message=message,
                text=old_place_view(place),
                state=state
            )
        canteens = await manager.receive_canteens(session)
        if manager.allowed_several_canteens():
            await state.set_state(canteen_state)
            text = 'Выберите столовую, в которой будете заказывать еду:'
            reply_markup = show_canteens_kb(canteens)
        else:
            await state.set_state(place_state)
            text = 'Выберите место доставки:'
            reply_markup = show_places_kb_new(await manager.receive_canteen_places(canteen=canteens[0]))

    except (IsNotCustomer, ValidCanteensNotExist) as exc:
        await state.clear()
        reply_markup = ReplyKeyboardRemove()
        if isinstance(exc, IsNotCustomer):
            text = 'Вас нет в списке заказчиков столовой.'
        else:
            text = 'У вас истек срок разрешения для заказа еды.'
    finally:
        await message_response(
            message=message,
            text=text,
            reply_markup=reply_markup,
            state=state,
            delete_after=True
        )


async def process_choice_delivery_place(
        callback: CallbackQuery,
        session: AsyncSession,
        state: FSMContext,
        manager: UserManager,
        canteen_state,
        place_state
) -> None:
    markup = show_places_kb_new(await manager.receive_canteen_places(session=session, callback=callback))
    current_state = await state.get_state()
    message_text = 'Выберите новое место доставки еды:'
    if current_state == canteen_state:
        await state.set_state(place_state)
        msg = await message_response(
            message=callback.message,
            text=message_text,
            reply_markup=markup,
            state=state,
            return_msg=True
        )
        await set_track_callback(callback, msg, state)
    else:
        track_cb = await get_track_callback(state)
        if track_cb.callback_data != callback.data:
            await edit_response(
                message=track_cb.message,
                text=message_text,
                reply_markup=markup
            )
            await update_track_callback(track_cb, callback, state)
    await callback_response(callback)
