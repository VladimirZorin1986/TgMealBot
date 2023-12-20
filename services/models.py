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


@dataclass
class DataPosition:
    prev_ind: int = field(default=0)
    cur_ind: int = field(default=0)
    next_ind: int = field(default=0)
    size: int = field(default=0)

    def handling_data(self, data: list[OrderForm]):
        if len(data) >= 1:
            self.cur_ind = 0
            self.prev_ind = len(data) - 1
            self.next_ind = 1
        self.size = len(data)

    def step_right(self) -> None:
        if self.is_empty():
            raise EmptyException
        self.prev_ind = self.cur_ind
        self.cur_ind = self.next_ind
        self.next_ind = (self.next_ind + 1) % self.size

    def step_left(self) -> None:
        if self.is_empty():
            raise EmptyException
        self.next_ind = self.cur_ind
        self.cur_ind = self.prev_ind
        self.prev_ind = (self.prev_ind - 1) % self.size

    def center(self) -> None:
        if not self.is_empty():
            self.cur_ind = self.cur_ind % self.size
            self.prev_ind = (self.cur_ind - 1) % self.size
            self.next_ind = (self.cur_ind + 1) % self.size

    def decrement_size(self) -> None:
        self.size -= 1

    def is_empty(self) -> bool:
        return not self.size


class OrdersDLL:

    def __init__(self) -> None:
        self.data: list[OrderForm] | None = None
        self.data_position = DataPosition()

    def _initialize_model(self):
        self.data_position.handling_data(self.data)

    def set_data(self, data: list[OrderForm]) -> None:
        if not data:
            raise EmptyException
        self.data = data
        self._initialize_model()

    def turn_next(self) -> None:
        self.data_position.step_right()

    def turn_prev(self) -> None:
        self.data_position.step_left()

    def get_cur_data(self) -> OrderForm:
        if self.data_position.is_empty():
            raise EmptyException
        return self.data[self.data_position.cur_ind]

    def delete_cur_data(self) -> OrderForm:
        if self.data_position.is_empty():
            raise EmptyException
        self.data_position.decrement_size()
        result = self.data.pop(self.data_position.cur_ind)
        self.data_position.center()
        return result


