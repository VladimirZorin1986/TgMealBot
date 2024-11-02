from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from sqlalchemy.ext.asyncio import AsyncSession
from keyboards.reply import hd_initial_kb, initial_kb, admin_kb, authorization_kb
from keyboards.inline import show_hd_types_kb, confirm_request_kb, scroll_requests, group_choice_kb
from states.hd_states import HdState, AdminState, AdminResponseState, AdminMessageState
from states.user_states import AuthState
from services.hd import HDService
from services.other_services import terminate_state_branch
from presentation.responses import message_response, callback_response, edit_response
from presentation.hd_views import show_request_info
from exceptions import RequestsNotExists


router = Router()
ADMIN_ID = 1106699847


@router.message(Command('support'), StateFilter(default_state))
@router.message(Command('support'), StateFilter(AuthState.get_contact))
async def process_support(message: Message, state: FSMContext):
    await message_response(
        message=message,
        text='Вы находитесь в разделе техподдержки. Если хотите задать вопрос нажмите на соответствующую кнопку внизу.\n'
             'Для возврата в основное меню выберите команду из меню или введите /cancel',
        reply_markup=hd_initial_kb(message.from_user.id == ADMIN_ID),
        state=state,
        delete_after=True
    )
    await state.set_state(HdState.initial)


@router.message(Command('support'), ~StateFilter(default_state), ~StateFilter(AuthState.get_contact))
async def process_cancel_support(message: Message):
    await message_response(
        message=message,
        text='Перед переходом в техподдержку необходимо закончить выполняемое действие или отменить его командой /cancel',
        delete_after=True
    )


@router.message(StateFilter(HdState.initial), F.text.endswith('Задать вопрос администратору'))
async def process_show_hd_types(message: Message, state: FSMContext, session: AsyncSession):
    types = await HDService.get_hd_types(session)
    await message_response(
        message=message,
        text='Выберите из списка тему вопроса:',
        reply_markup=show_hd_types_kb(types),
        state=state,
        delete_after=True
    )
    await state.set_state(HdState.get_hd_type)
    await HDService.remember_variables(state, user_id=message.from_user.id)


@router.callback_query(StateFilter(HdState.get_hd_type), F.data.startswith('hd_type'))
async def process_set_request_text(callback: CallbackQuery, state: FSMContext):
    type_id = int(callback.data.split(':')[-1])
    await message_response(
        message=callback.message,
        text='Опишите вашу проблему в стандартной строке набора:',
        reply_markup=ReplyKeyboardRemove(),
        state=state,
        delete_after=True
    )
    await state.set_state(HdState.set_hd_comment)
    await HDService.remember_variables(state, type_id=type_id)
    await callback.answer()


@router.message(StateFilter(HdState.set_hd_comment), F.text)
async def process_get_request_text(message: Message, state: FSMContext):
    await HDService.remember_variables(state, request_text=message.text.strip())
    await message_response(
        message=message,
        text='Отправить запрос администратору?',
        reply_markup=confirm_request_kb(),
        state=state
    )
    await state.set_state(HdState.confirm_new_request)


@router.callback_query(StateFilter(HdState.confirm_new_request), F.data == 'confirm')
async def process_confirm_request(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    request_id = await HDService.save_request(session, state)
    await HDService.send_message_to_user(
        bot=callback.bot,
        user_id=ADMIN_ID,
        msg_text=f'Поступил новый запрос №{request_id} в обработку!'
    )
    await callback_response(
        callback=callback,
        text='Ваш запрос отправлен администратору!',
        show_alert=True
    )
    await terminate_state_branch(callback.message, state)
    await state.set_state(HdState.initial)
    await message_response(
        message=callback.message,
        text='Возврат в меню техподдержки',
        reply_markup=hd_initial_kb(callback.from_user.id == ADMIN_ID),
        state=state
    )


@router.callback_query(StateFilter(HdState.confirm_new_request), F.data == 'cancel')
async def process_cancel_request(callback: CallbackQuery, state: FSMContext):
    await callback_response(
        callback=callback,
        text='Ваш запрос отменен!',
        show_alert=True
    )
    await terminate_state_branch(callback.message, state)
    await state.set_state(HdState.initial)
    await message_response(
        message=callback.message,
        text='Возврат в меню техподдержки',
        reply_markup=hd_initial_kb(callback.from_user.id == ADMIN_ID),
        state=state
    )


@router.message(StateFilter(HdState.initial), F.text.endswith('Мои вопросы-ответы'))
async def process_show_user_requests(message: Message, state: FSMContext, session: AsyncSession):
    try:
        requests = await HDService.get_user_requests(session, message.from_user.id)
    except RequestsNotExists:
        await message_response(
            message=message,
            text='У вас пока нет запросов в техподдержку',
            reply_markup=hd_initial_kb(message.from_user.id == ADMIN_ID),
            state=state,
            delete_after=True
        )
    else:
        await HDService.remember_variables(state, requests=requests)
        current_request = tuple(requests.items())[0][-1]
        await message_response(
            message=message,
            text=show_request_info(current_request),
            reply_markup=scroll_requests(current_request),
            state=state,
            delete_after=True
        )
        await state.set_state(HdState.show_requests)


@router.callback_query(StateFilter(HdState.show_requests), F.data.startswith('scroll'))
@router.callback_query(StateFilter(AdminResponseState.show_user_requests), F.data.startswith('scroll'))
async def process_scroll_requests(callback: CallbackQuery, state: FSMContext):
    request = await HDService.get_request_from_cache(state, int(callback.data.split(':')[1]))
    if not request.id == request.prev_id == request.next_id:
        await edit_response(
            message=callback.message,
            text=show_request_info(request, callback.from_user.id == ADMIN_ID),
            reply_markup=scroll_requests(request, callback.from_user.id == ADMIN_ID)
        )
    await callback.answer()


@router.callback_query(StateFilter(HdState.show_requests), F.data == 'back')
async def process_back_to_initial(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await message_response(
        message=callback.message,
        text='Возврат в меню техподдержки',
        reply_markup=hd_initial_kb(callback.from_user.id == ADMIN_ID),
        state=state,
        delete_after=True
    )
    await state.set_state(HdState.initial)
    await callback.answer()


@router.message(StateFilter(HdState.initial), F.text.endswith('Вернуться к заказу питания'))
async def process_return_to_main_menu(message: Message, state: FSMContext, session: AsyncSession):
    await terminate_state_branch(message, state)
    is_auth = await HDService.is_auth_user(session, message.from_user.id)
    await message_response(
        message=message,
        text='Возврат в главное меню',
        reply_markup=initial_kb() if is_auth else authorization_kb()
    )
    if not is_auth:
        await state.set_state(AuthState.get_contact)


@router.message(StateFilter(HdState.initial), F.from_user.id == ADMIN_ID | F.text.endswith('Администрирование'))
async def process_show_admin_menu(message: Message, state: FSMContext):
    await message_response(
        message=message,
        text='Выберите раздел для работы:',
        reply_markup=admin_kb(),
        state=state,
        delete_after=True
    )
    await state.set_state(AdminState.initial)


@router.message(StateFilter(AdminState.initial), F.text.endswith('Работа с запросами'))
async def process_show_group_choice(message: Message, state: FSMContext):
    await message_response(
        message=message,
        text='Выберите группу запросов:',
        reply_markup=group_choice_kb(),
        state=state,
        delete_after=True
    )
    await state.set_state(AdminResponseState.group_choice)


@router.message(StateFilter(AdminState.initial), F.text.endswith('Возврат в меню техподдержки'))
async def process_return_to_hd_menu(message: Message, state: FSMContext):
    await terminate_state_branch(message, state)
    await state.set_state(HdState.initial)
    await message_response(
        message=message,
        text='Возврат в меню техподдержки',
        reply_markup=hd_initial_kb(message.from_user.id == ADMIN_ID),
        state=state
    )


@router.callback_query(StateFilter(AdminResponseState.group_choice))
async def process_show_requests(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    try:
        requests = await HDService.get_requests_by_admin(session, mode=callback.data)
    except RequestsNotExists:
        await message_response(
            message=callback.message,
            text='Нет запросов от пользователей',
            reply_markup=admin_kb(),
            state=state,
            delete_after=True
        )
        await state.set_state(AdminState.initial)
    else:
        await HDService.remember_variables(state, requests=requests)
        current_request = tuple(requests.items())[0][-1]
        print(current_request.user_id)
        await message_response(
            message=callback.message,
            text=show_request_info(current_request, True),
            reply_markup=scroll_requests(current_request, True),
            state=state,
            delete_after=True
        )
        await state.set_state(AdminResponseState.show_user_requests)
        await callback.answer()


@router.callback_query(StateFilter(AdminResponseState.show_user_requests), F.data == 'back')
async def process_back_to_initial(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await message_response(
        message=callback.message,
        text='Возврат в меню администратора',
        reply_markup=admin_kb(),
        state=state,
        delete_after=True
    )
    await state.set_state(AdminState.initial)
    await callback.answer()


@router.callback_query(StateFilter(AdminResponseState.show_user_requests), F.data.startswith('answer'))
async def process_answer_user(callback: CallbackQuery, state: FSMContext):
    await HDService.remember_variables(
        state,
        request_id=int(callback.data.split(':')[-1]),
        send_user_id=int(callback.data.split(':')[-2]),
    )
    await message_response(
        message=callback.message,
        text='Введите в строку ответ пользователю',
        reply_markup=ReplyKeyboardRemove(),
        state=state
    )
    await state.set_state(AdminResponseState.set_solution)
    await callback.answer()


@router.message(StateFilter(AdminResponseState.set_solution))
async def process_set_solution(message: Message, state: FSMContext):
    await HDService.remember_variables(state, solution_text=message.text.strip())
    await message_response(
        message=message,
        text='Отправить ответ пользователю?',
        reply_markup=confirm_request_kb(),
        state=state
    )
    await state.set_state(AdminResponseState.confirm_answer)


@router.callback_query(StateFilter(AdminResponseState.confirm_answer), F.data == 'confirm')
async def process_confirm_answer(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    request_id, send_user_id = await HDService.answer_user_request(session, state)
    await HDService.send_message_to_user(
        bot=callback.bot,
        user_id=send_user_id,
        msg_text=f'Поступил ответ по вашему запросу №{request_id}. Ознакомиться с ответом можно в разделе Мои вопросы-ответы в меню техподдержки.'
    )
    await callback_response(
        callback=callback,
        text='Ответ отправлен пользователю',
        show_alert=True
    )
    await terminate_state_branch(callback.message, state)
    await state.set_state(AdminState.initial)
    await message_response(
        message=callback.message,
        text='Возврат в меню администратора',
        reply_markup=admin_kb(),
        state=state
    )


@router.callback_query(StateFilter(AdminResponseState.confirm_answer), F.data == 'cancel')
@router.callback_query(StateFilter(AdminMessageState.confirm_send), F.data == 'cancel')
async def process_cancel_answer(callback: CallbackQuery, state: FSMContext):
    await callback_response(
        callback=callback,
        text='Отправка сообщения отменена!',
        show_alert=True
    )
    await terminate_state_branch(callback.message, state)
    await state.set_state(AdminState.initial)
    await message_response(
        message=callback.message,
        text='Возврат в меню администратора',
        reply_markup=admin_kb(),
        state=state
    )


@router.message(StateFilter(AdminState.initial), F.text.endswith('Рассылка сообщений'))
async def process_mailing_chapter(message: Message, state: FSMContext):
    await message_response(
        message=message,
        text='Введите сообщение для рассылки пользователям:',
        state=state,
        delete_after=True
    )
    await state.set_state(AdminMessageState.set_message)


@router.message(StateFilter(AdminMessageState.set_message), F.text)
async def process_set_message(message: Message, state: FSMContext):
    await HDService.remember_variables(state, admin_msg_text=message.text.strip())
    await message_response(
        message=message,
        text='Отправить сообщение пользователям?',
        reply_markup=confirm_request_kb(),
        state=state
    )
    await state.set_state(AdminMessageState.confirm_send)


@router.callback_query(StateFilter(AdminMessageState.confirm_send), F.data == 'confirm')
async def process_send_message(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    await HDService.send_message_to_bot_users(
        bot=callback.bot,
        msg_text=data['admin_msg_text'],
        session=session
    )
    await callback_response(
        callback=callback,
        text='Сообщение отправлено пользователям бота',
        show_alert=True
    )
    await terminate_state_branch(callback.message, state)
    await state.set_state(AdminState.initial)
    await message_response(
        message=callback.message,
        text='Возврат в меню администратора',
        reply_markup=admin_kb(),
        state=state
    )
