import datetime
from utils.service_models import OrderForm, ExistOrderForm
from database.models import MenuPosition


def full_order_view(order_form: OrderForm) -> str:
    result = [
        f'{name} Кол-во: {detail.quantity} Стоимость: {cost * detail.quantity}'
        for (name, cost), detail in order_form.details.items()
    ]
    result.append(f'Общая стоимость заказа: {order_form.amt}')
    return '\n\n'.join(result)


def position_view(position: MenuPosition) -> str:
    result = f'{position.name}\nКол-во: {position.quantity}\nСтоимость: {position.quantity * position.cost}'
    return result


def delete_order_view(order_form: ExistOrderForm) -> str:
    head = f'Наименование меню: {order_form.menu_name}\n'\
           f'Дата меню: {order_form.menu_date}\n'\
           f'Дата и время создания: {order_form.created_at}'
    body = '\n'.join([
        f'{detail.menu_pos_name} Кол-во: {detail.quantity} Стоимость: {detail.menu_pos_cost * detail.quantity}'
        for detail in order_form.details
    ])
    tail = f'Общая стоимость заказа: {order_form.amt}'
    return '\n\n'.join([head, body, tail])

