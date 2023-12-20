from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.models import Canteen, Menu, DeliveryPlace
from keyboards.callbacks import CanteenCallbackFactory, PlaceCallbackFactory, MenuCallbackFactory
from services.models import DetailForm, DataPosition


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


def order_delete_scroll_kb(position: DataPosition) -> InlineKeyboardMarkup:
    return default_scroll_kb(
        position=position,
        middle_button=InlineKeyboardButton(
            text='❌ Удалить',
            callback_data='delete_order'
        ),
        prev_button_text=f'⏪ ({position.prev_ind + 1}/{position.size})',
        next_button_text=f'⏩ ({position.next_ind + 1}/{position.size})'
    )


def order_view_scroll_kb(position: DataPosition) -> InlineKeyboardMarkup:
    return default_scroll_kb(
        position=position,
        middle_button=InlineKeyboardButton(
            text=f'📃 {position.cur_ind + 1}/{position.size}',
            callback_data='no action'
        ),
        prev_button_text='⏪',
        next_button_text='⏩'
    )


def default_scroll_kb(
        position: DataPosition,
        middle_button: InlineKeyboardButton,
        prev_button_text: str,
        next_button_text: str
) -> InlineKeyboardMarkup:
    if position.size == 1:
        keyboard = [[middle_button]]
    else:
        keyboard = [
            [
                InlineKeyboardButton(
                    text=prev_button_text,
                    callback_data='prev'
                ),
                middle_button,
                InlineKeyboardButton(
                    text=next_button_text,
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
