from aiogram.fsm.state import State, StatesGroup


class AuthState(StatesGroup):
    get_contact = State()
    get_canteen = State()
    get_place = State()


class SettingsState(StatesGroup):
    get_option = State()
    set_option = State()
