from prettytable import PrettyTable
from services.models import DetailForm, OrderForm


emoji_num_dict = {
    1: '\U0001F534',
    2: '\U0001F7E1',
    3: '\U0001F7E2'
}


def order_view(order_form: OrderForm):
    body = PrettyTable(field_names=['Наименование', 'Кол-во', 'Цена', 'Цвет'], padding_width=0)
    rows = [
        [
            '\n'.join(map(lambda s: s.strip(), detail.menu_pos_name.split())),
            detail.quantity,
            detail.menu_pos_cost * detail.quantity,
            emoji_num_dict.get(detail.color_num, '\U000026AA')
        ]
        for detail in order_form.selected_details
    ]
    for row in rows:
        body.add_row(row, divider=True)

    menu_head_name = ' '.join(['Заказное' if order_form.custom_menu else 'Комплексное', order_form.menu_name.lower()])
    head_list = [f'{menu_head_name}\n',
                 f'Дата меню:\n{order_form.menu_date.strftime("%d.%m.%Y")}',
                 f'Место доставки:\n{order_form.place_name} ({order_form.canteen_name})']
    if order_form.created_at:
        head_list.append(f'Дата и время создания:\n{order_form.created_at.strftime("%d.%m.%Y %H:%M:%S")}')

    head = '\n'.join(head_list)
    tail = f'Общая стоимость заказа: {order_form.amt}'

    return '\n\n'.join(map(lambda s: f'<code>{s}</code>', [head, body.get_string(), tail]))


def position_view_new(detail_form: DetailForm) -> str:
    body = PrettyTable(field_names=['Наименование', 'Кол-во', 'Цена', 'Цвет'], padding_width=0)
    body.add_row(
        [
            '\n'.join(map(lambda s: s.strip(), detail_form.menu_pos_name.split())),
            detail_form.quantity,
            detail_form.quantity * detail_form.menu_pos_cost,
            emoji_num_dict.get(detail_form.color_num, '⚪')
        ]
    )
    return f'<code>{body.get_string()}</code>'
