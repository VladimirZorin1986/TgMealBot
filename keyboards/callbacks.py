from aiogram.filters.callback_data import CallbackData


class CanteenCallbackFactory(CallbackData, prefix='canteen'):
    canteen_id: int


class PlaceCallbackFactory(CallbackData, prefix='place'):
    place_id: int


class MenuCallbackFactory(CallbackData, prefix='menu'):
    menu_id: int


class HDTypeCallbackFactory(CallbackData, prefix='hd_type'):
    hd_type_id: int


class HDRequestCallbackFactory(CallbackData, prefix='hd_request'):
    hd_request_id: int
