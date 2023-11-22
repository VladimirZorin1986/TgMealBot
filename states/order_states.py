from aiogram.fsm.state import State, StatesGroup


class NewOrderState(StatesGroup):
    menu_choice = State()
    dish_choice = State()
    check_status = State()


class CancelOrderState(StatesGroup):
    order_choices = State()
