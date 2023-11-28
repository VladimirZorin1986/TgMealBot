from aiogram.fsm.state import State, StatesGroup


class AuthState(StatesGroup):
    get_contact = State()
    get_canteen = State()
    get_place = State()


class ChangeDeliveryPlace(StatesGroup):
    set_new_canteen = State()
    set_new_place = State()
