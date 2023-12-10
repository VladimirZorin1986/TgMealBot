from dataclasses import dataclass, field
from decimal import Decimal
import datetime
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from database.models import OrderDetail


MenuId = int
CustomerId = int
MenuPosId = int
PlaceId = int
CanteenId = int
OrderId = int
DetailId = int
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


@dataclass
class DetailForm:
    detail_id: int
    quantity: int
    menu_pos_id: int
    menu_pos_name: str
    menu_pos_cost: Decimal


@dataclass
class ExistOrderForm:
    order_id: int
    created_at: datetime.datetime
    amt: Decimal
    canteen_name: str
    place_name: str
    menu_name: str
    menu_date: datetime.date
    details: list[DetailForm]


@dataclass
class NewOrderForm:
    order_id: OrderId = field(default=None)
    customer_id: CustomerId = field(default=None)
    created_at: datetime.datetime = field(default=None)
    amt: Decimal = field(default=None)
    place_id: PlaceId = field(default=None)
    place_name: str = field(default=None)
    canteen_id: CanteenId = field(default=None)
    canteen_name: str = field(default=None)
    menu_id: MenuId = field(default=None)
    menu_name: str = field(default=None)
    menu_date: datetime.date = field(default=None)
    details: list[DetailForm] = field(default_factory=list)


class ServiceManager:

    def __init__(self, model):
        self._model = model

    def get_model(self):
        return self._model

    def set_attrs(self, **kwargs):
        for (key, value) in kwargs.items():
            setattr(self._model, key, value)

    def get_attr(self, attr_name: str):
        return getattr(self._model, attr_name)

    async def save(self, state: FSMContext):
        await state.update_data({self.__class__.__name__: self})
