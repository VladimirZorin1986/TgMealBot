from dataclasses import dataclass, field
from decimal import Decimal
import datetime
from aiogram.types import Message


@dataclass
class TrackCallback:
    message: Message
    callback_data: str


@dataclass
class UserForm:
    customer_id: int = field(default=None)
    tg_id: int = field(default=None)
    canteen_id: int = field(default=None)
    place_id: int = field(default=None)


@dataclass
class DetailForm:
    detail_id: int = field(default=None)
    quantity: int = field(default=1)
    menu_pos_id: int = field(default=None)
    menu_pos_name: str = field(default=None)
    menu_pos_cost: Decimal = field(default=None)


@dataclass
class OrderForm:
    order_id: int = field(default=None)
    customer_id: int = field(default=None)
    created_at: datetime.datetime = field(default=None)
    amt: Decimal = field(default=0)
    place_id: int = field(default=None)
    place_name: str = field(default=None)
    canteen_id: int = field(default=None)
    canteen_name: str = field(default=None)
    menu_id: int = field(default=None)
    menu_name: str = field(default=None)
    menu_date: datetime.date = field(default=None)
    raw_details: dict[int, DetailForm] = field(default_factory=dict)
    selected_details: list[DetailForm] = field(default_factory=list)


