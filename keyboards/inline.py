from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Canteen, Menu, DeliveryPlace
from utils.service_functions import get_id_from_callback
from services.user_services import get_places_by_canteen, get_canteen_by_id
from services.order_services import get_valid_menus_by_user, get_menu_positions_by_menu
from keyboards.callbacks import (CanteenCallbackFactory, PlaceCallbackFactory, MenuCallbackFactory,
                                 PositionCallbackFactory, OrderCallbackFactory)
from services.models import DetailForm, OrderForm, OrdersDLL


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


def show_places_kb_new(places: list[DeliveryPlace]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for place in places:
        builder.button(
            text=place.name,
            callback_data=PlaceCallbackFactory(
                place_id=place.id
            ).pack()
        )
    return builder.adjust(1).as_markup()


def order_menu_kb(menus: list[Menu]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for menu in menus:
        builder.button(
            text=f'{menu.name} на {menu.date.strftime("%d.%m.%Y")}',
            callback_data=MenuCallbackFactory(
                menu_id=menu.id
            ).pack()
        )
    return builder.adjust(1).as_markup()


def dish_count_kb() -> InlineKeyboardMarkup:
    keyboard = [[
        InlineKeyboardButton(
            text='➖1️⃣',
            callback_data='minus'
        ),
        InlineKeyboardButton(
            text='✔ Добавить',
            callback_data=f'add'
        ),
        InlineKeyboardButton(
            text='➕1️⃣',
            callback_data='plus'
        )
    ]]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def dish_count_kb_new(detail_form: DetailForm) -> InlineKeyboardMarkup:
    keyboard = [[
        InlineKeyboardButton(
            text='➖1️⃣',
            callback_data=f'minus:{detail_form.menu_pos_id}'
        ),
        InlineKeyboardButton(
            text='✔ Добавить',
            callback_data=f'add:{detail_form.menu_pos_id}'
        ),
        InlineKeyboardButton(
            text='➕1️⃣',
            callback_data=f'plus:{detail_form.menu_pos_id}'
        )
    ]]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def inline_confirm_cancel_kb() -> InlineKeyboardMarkup:
    kb = [
        [
            InlineKeyboardButton(
                text='✅ Отправить',
                callback_data='save'
            ),
            InlineKeyboardButton(
                text='❌ Отменить',
                callback_data='cancel'
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


def delete_order_kb(order_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='❌ Удалить заказ',
                    callback_data=OrderCallbackFactory(
                        order_id=order_id
                    ).pack()
                )
            ]
        ]
    )


def delete_order_kb_new(order_form: OrderForm) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='❌ Удалить заказ',
                    callback_data=OrderCallbackFactory(
                        order_id=order_form.order_id
                    ).pack()
                )
            ]
        ]
    )


def delete_order_kb_new_new(prev_id: int, next_id: int, size: int) -> InlineKeyboardMarkup:
    if size == 1:
        keyboard = [
            [
                InlineKeyboardButton(
                    text='❌ Удалить заказ',
                    callback_data='delete_order'
                )
            ]
        ]
    else:
        keyboard = [
            [
                InlineKeyboardButton(
                    text=f'<< {prev_id + 1}/{size}',
                    callback_data=f'prev'
                ),
                InlineKeyboardButton(
                    text='❌ Удалить заказ',
                    callback_data=f'delete_order'
                ),
                InlineKeyboardButton(
                    text=f'>> {next_id + 1}/{size}',
                    callback_data=f'next'
                )
            ]
        ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def help_chapters_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='🧍 Авторизация', callback_data='auth_help')],
            [InlineKeyboardButton(text='🚚 Работа с заказами', callback_data='order_help')]
        ]
    )
