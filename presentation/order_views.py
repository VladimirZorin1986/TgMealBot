from prettytable import PrettyTable
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
    body = PrettyTable(field_names=['Наименование', 'Количество', 'Стоимость'])
    body.add_rows(
        [
            [detail.menu_pos_name, detail.quantity, detail.menu_pos_cost * detail.quantity]
            for detail in order_form.details
        ]
    )
    body_repr = body.get_string()
    width = int(len(body_repr) / (len(body.rows) + 4))

    head = '\n'.join(
        [f'Наименование меню: {order_form.menu_name:>{width - 19}}',
         f'Дата меню: {order_form.menu_date.strftime("%d.%m.%Y"):>{width - 11}}',
         f'Дата и время создания: {order_form.created_at.strftime("%d.%m.%Y %H:%M:%S"):>{width - 23}}']
    )
    tail = f'Общая стоимость заказа: {order_form.amt:>{width - 24}}'

    return '\n\n'.join(map(lambda s: f'<code>{s}</code>', [head, body_repr, tail]))
