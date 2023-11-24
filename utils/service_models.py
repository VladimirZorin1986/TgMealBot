from dataclasses import dataclass, field
from decimal import Decimal
from aiogram.types import Message
from database.models import OrderDetail


MenuId = int
CustomerId = int
MenuPosId = int
Money = Decimal
MenuPosName = str
MenuPosCost = Decimal


@dataclass
class TrackCallback:
    message: Message
    callback_data: str


@dataclass
class OrderForm:
    customer_id: CustomerId
    menu_id: MenuId = field(default=None)
    amt: Money = field(default=None)
    details: dict[tuple[MenuPosName, MenuPosCost], OrderDetail] = field(default_factory=dict)
