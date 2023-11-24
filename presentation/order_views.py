from utils.service_models import OrderForm
from database.models import MenuPosition


async def full_order_view(order_form: OrderForm) -> str:
    result = [
        f'{name} Кол-во: {detail.quantity} Стоимость: {cost * detail.quantity}'
        for (name, cost), detail in order_form.details.items()
    ]
    result.append(f'Общая стоимость заказа: {order_form.amt}')
    return '\n\n'.join(result)


def position_view(position: MenuPosition) -> str:
    result = f'{position.name}\nКол-во: {position.quantity}\nСтоимость: {position.quantity*position.cost}'
    return result
