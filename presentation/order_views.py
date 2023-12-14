from prettytable import PrettyTable
from utils.service_models import OrderForm, ExistOrderForm
from database.models import MenuPosition
from services.models import DetailForm, OrderForm


def full_order_view(order_form: OrderForm) -> str:
    body = PrettyTable(field_names=['Наименование', 'Кол-во', 'Стоимость'], padding_width=0)
    rows = [
        [
            '\n'.join(map(lambda s: s.strip(), name.split())),
            detail.quantity,
            cost * detail.quantity
        ]
        for (name, cost), detail in order_form.details.items()
    ]
    for row in rows:
        body.add_row(row, divider=True)

    tail = f'Общая стоимость заказа: {order_form.amt}'
    return '\n\n'.join(map(lambda s: f'<code>{s}</code>', [body.get_string(), tail]))


def order_view(order_form: OrderForm):
    body = PrettyTable(field_names=['Наименование', 'Кол-во', 'Стоимость'], padding_width=0)
    rows = [
        [
            '\n'.join(map(lambda s: s.strip(), detail.menu_pos_name.split())),
            detail.quantity,
            detail.menu_pos_cost * detail.quantity
        ]
        for detail in order_form.selected_details
    ]
    for row in rows:
        body.add_row(row, divider=True)

    head_list = [f'{order_form.menu_name}\n',
                 f'Дата меню:\n{order_form.menu_date.strftime("%d.%m.%Y")}',
                 f'Место доставки:\n{order_form.place_name} ({order_form.canteen_name})']
    if order_form.created_at:
        head_list.append(f'Дата и время создания:\n{order_form.created_at.strftime("%d.%m.%Y %H:%M:%S")}')

    head = '\n'.join(head_list)
    tail = f'Общая стоимость заказа: {order_form.amt}'

    return '\n\n'.join(map(lambda s: f'<code>{s}</code>', [head, body.get_string(), tail]))


def position_view(position: MenuPosition) -> str:
    body = PrettyTable(field_names=['Наименование', 'Кол-во', 'Стоимость'], padding_width=0)
    body.add_row(
        [
            '\n'.join(map(lambda s: s.strip(), position.name.split())),
            position.quantity,
            position.quantity * position.cost
        ]
    )
    return f'<code>{body.get_string()}</code>'


def position_view_new(detail_form: DetailForm) -> str:
    body = PrettyTable(field_names=['Наименование', 'Кол-во', 'Стоимость'], padding_width=0)
    body.add_row(
        [
            '\n'.join(map(lambda s: s.strip(), detail_form.menu_pos_name.split())),
            detail_form.quantity,
            detail_form.quantity * detail_form.menu_pos_cost
        ]
    )
    return f'<code>{body.get_string()}</code>'


def delete_order_view(order_form: ExistOrderForm) -> str:
    body = PrettyTable(field_names=['Наименование', 'Кол-во', 'Стоимость'], padding_width=0)
    rows = [
            [
                '\n'.join(map(lambda s: s.strip(), detail.menu_pos_name.split())),
                detail.quantity,
                detail.menu_pos_cost * detail.quantity
            ]
            for detail in order_form.details
        ]
    for row in rows:
        body.add_row(row, divider=True)

    head = '\n'.join(
        [f'{order_form.menu_name}\n',
         f'Дата меню:\n{order_form.menu_date.strftime("%d.%m.%Y")}',
         f'Дата и время создания:\n{order_form.created_at.strftime("%d.%m.%Y %H:%M:%S")}',
         f'Место доставки:\n{order_form.place_name} ({order_form.canteen_name})']
    )
    tail = f'Общая стоимость заказа: {order_form.amt}'

    return '\n\n'.join(map(lambda s: f'<code>{s}</code>', [head, body.get_string(), tail]))
