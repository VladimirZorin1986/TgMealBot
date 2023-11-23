from dataclasses import dataclass, field
from aiogram.types import Message


MenuId = int
CustomerId = int
MenuPosId = int


@dataclass
class TrackCallback:
    message: Message
    callback_data: str


@dataclass
class OrderForm:
    customer_id: CustomerId
    menu_id: MenuId = field(default=None)
    details: list = field(default_factory=list)


if __name__ == '__main__':
    print(OrderForm(customer_id=1))




