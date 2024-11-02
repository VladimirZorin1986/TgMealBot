from aiogram.fsm.state import State, StatesGroup


class HdState(StatesGroup):
    initial = State()
    get_hd_type = State()
    set_user_info = State()
    set_hd_comment = State()
    show_requests = State()
    confirm_new_request = State()


class AdminState(StatesGroup):
    initial = State()
    group_choice = State()
    show_user_requests = State()
    set_solution = State()
    confirm_answer = State()


class AdminResponseState(StatesGroup):
    group_choice = State()
    show_user_requests = State()
    set_solution = State()
    confirm_answer = State()


class AdminMessageState(StatesGroup):
    set_message = State()
    confirm_send = State()
