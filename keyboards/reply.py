from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def authorization_kb() -> ReplyKeyboardMarkup:
    kb = [[KeyboardButton(text='🚶‍➡️ Авторизоваться', request_contact=True)]]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)


def initial_kb() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text='🍱 Новый заказ'),
         KeyboardButton(text='🚚 Изменить место доставки')],
        [KeyboardButton(text='📖 Просмотр заказов'),
         KeyboardButton(text='🛑 Удаление активных заказов')]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)


def confirm_cancel_kb() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text='✅ Подтвердить'),
         KeyboardButton(text='❌ Отменить')
         ],
        [KeyboardButton(text='⬇ Продолжить список')],
        [KeyboardButton(text='🍽 Заказать стандартный комплекс')]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def back_to_initial_kb() -> ReplyKeyboardMarkup:
    kb = [[KeyboardButton(text='🔙 Вернуться в главное меню')]]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
