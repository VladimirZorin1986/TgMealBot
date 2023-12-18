from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.models import Canteen, Menu, DeliveryPlace
from keyboards.callbacks import CanteenCallbackFactory, PlaceCallbackFactory, MenuCallbackFactory
from services.models import DetailForm


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


def delete_order_kb_new_new(prev_id: int, next_id: int, size: int) -> InlineKeyboardMarkup:
    if size == 1:
        keyboard = [
            [
                InlineKeyboardButton(
                    text='❌ Удалить',
                    callback_data='delete_order'
                )
            ]
        ]
    else:
        keyboard = [
            [
                InlineKeyboardButton(
                    text=f'⏪ ({prev_id + 1}/{size})',
                    callback_data='prev'
                ),
                InlineKeyboardButton(
                    text='❌ Удалить',
                    callback_data='delete_order'
                ),
                InlineKeyboardButton(
                    text=f'⏩ ({next_id + 1}/{size})',
                    callback_data='next'
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
