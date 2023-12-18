from dataclasses import dataclass, field
from decimal import Decimal
import datetime
from typing import Generator
from aiogram.types import Message
from exceptions import EmptyException


@dataclass
class TrackCallback:
    message: Message
    callback_data: str


@dataclass
class UserForm:
    customer_id: int = field(default=None)
    tg_id: int = field(default=None)
    canteen_ids: list[int] = field(default_factory=list)
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
    custom_menu: bool = field(default=None)
    canteen_id: int = field(default=None)
    canteen_name: str = field(default=None)
    menu_id: int = field(default=None)
    menu_name: str = field(default=None)
    menu_date: datetime.date = field(default=None)
    raw_details: dict[int, DetailForm] = field(default_factory=dict)
    temp_details: Generator[DetailForm, None, None] = field(default=None)
    selected_details: list[DetailForm] = field(default_factory=list)


class OrdersDLL:

    def __init__(self) -> None:
        self.data: list[OrderForm] | None = None
        self.cur: int = 0
        self.prev: int = 0
        self.next: int = 0
        self.size: int = 0

    def _initialize_model(self):
        if len(self.data) >= 1:
            self.cur = 0
            self.prev = len(self.data) - 1
            self.next = 1
        self.size = len(self.data)

    def set_data(self, data: list[OrderForm]) -> None:
        if not data:
            raise EmptyException
        self.data = data
        self._initialize_model()

    def turn_next(self) -> None:
        if self.size == 0:
            raise EmptyException
        self.prev = self.cur
        self.cur = self.next
        self.next = (self.next + 1) % self.size

    def turn_prev(self) -> None:
        if self.size == 0:
            raise EmptyException
        self.next = self.cur
        self.cur = self.prev
        self.prev = (self.prev - 1) % self.size

    def get_cur_data(self) -> OrderForm:
        if self.size == 0:
            raise EmptyException
        return self.data[self.cur]

    def delete_cur_data(self) -> OrderForm:
        if self.size == 0:
            raise EmptyException
        self.size -= 1
        result = self.data.pop(self.cur)
        if self.size != 0:
            self.cur = self.cur % self.size
            self.prev = (self.cur - 1) % self.size
            self.next = (self.cur + 1) % self.size
        return result


