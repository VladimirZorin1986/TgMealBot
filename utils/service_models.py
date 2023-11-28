from dataclasses import dataclass, field
from decimal import Decimal
from aiogram.types import Message
from database.models import OrderDetail


MenuId = int
CustomerId = int
MenuPosId = int
PlaceId = int
MenuPosName = str
MenuPosCost = Decimal


@dataclass
class TrackCallback:
    message: Message
    callback_data: str


@dataclass
class OrderForm:
    customer_id: CustomerId
    place_id: PlaceId = field(default=None)
    menu_id: MenuId = field(default=None)
    amt: Decimal = field(default=None)
    details: dict[tuple[MenuPosName, MenuPosCost], OrderDetail] = field(default_factory=dict)
