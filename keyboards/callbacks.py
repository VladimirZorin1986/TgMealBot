from aiogram.filters.callback_data import CallbackData


class CanteenCallbackFactory(CallbackData, prefix='canteen'):
    canteen_id: int


class PlaceCallbackFactory(CallbackData, prefix='place'):
    place_id: int


class MenuCallbackFactory(CallbackData, prefix='menu'):
    menu_id: int
