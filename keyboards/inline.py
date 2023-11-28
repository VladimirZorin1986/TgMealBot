from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Canteen
from utils.service_functions import get_id_from_callback
from services.user_services import get_places_by_canteen, get_canteen_by_id
from services.order_services import get_valid_menus_by_user, get_menu_positions_by_menu
from keyboards.callbacks import (CanteenCallbackFactory, PlaceCallbackFactory, MenuCallbackFactory,
                                 PositionCallbackFactory)


def show_canteens_kb(canteens: list[Canteen]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for canteen in canteens:
        builder.button(
            text=canteen.name,
            callback_data=CanteenCallbackFactory(
                canteen_id=canteen.id
            ).pack()
        )
    return builder.adjust(2).as_markup()


async def show_places_kb(
        session: AsyncSession,
        canteen: Canteen | None = None,
        callback: CallbackQuery | None = None) -> InlineKeyboardMarkup:
    canteen = canteen or await get_canteen_by_id(session, get_id_from_callback(callback))
    places = await get_places_by_canteen(session, canteen)
    builder = InlineKeyboardBuilder()
    for place in places:
        builder.button(
            text=place.name,
            callback_data=PlaceCallbackFactory(
                place_id=place.id
            ).pack()
        )
    return builder.adjust(1).as_markup()


async def order_menu_kb(session: AsyncSession, customer_id: int) -> InlineKeyboardMarkup:
    menus = await get_valid_menus_by_user(session, customer_id)
    builder = InlineKeyboardBuilder()
    for menu in menus:
        builder.button(
            text=f'{menu.name} на {menu.date}',
            callback_data=MenuCallbackFactory(
                menu_id=menu.id
            ).pack()
        )
    return builder.adjust(1).as_markup()


async def order_positions_kb(session: AsyncSession, menu_id: int):
    positions = await get_menu_positions_by_menu(session, menu_id)
    builder = InlineKeyboardBuilder()
    for position in positions:
        builder.button(
            text=f'{position.name}',
            callback_data=PositionCallbackFactory(
                position_id=position.id
            ).pack()
        )
    return builder.adjust(1).as_markup()


def dish_count_kb() -> InlineKeyboardMarkup:
    keyboard = [[
        InlineKeyboardButton(
            text='-1',
            callback_data='minus'
        ),
        InlineKeyboardButton(
            text='Добавить',
            callback_data=f'add'
        ),
        InlineKeyboardButton(
            text='+1',
            callback_data='plus'
        )
    ]]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def inline_confirm_cancel_kb() -> InlineKeyboardMarkup:
    kb = [
        [
            InlineKeyboardButton(
                text='Отправить',
                callback_data='save'
            ),
            InlineKeyboardButton(
                text='Отменить',
                callback_data='cancel'
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


def delete_order_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text='Удалить заказ', callback_data='delete_order')]]
    )

