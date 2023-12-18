import datetime
from typing import Generator, Any, Iterable
from itertools import islice
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from services.models import OrderForm, UserForm, DetailForm, OrdersDLL
from database.managers import DatabaseManager, DbSessionManager
from database.models import (Canteen, DeliveryPlace, Menu, Order, OrderDetail, Customer,
                             CustomerPermission, MenuPosition)
from exceptions import *


class ServiceManager:

    def __init__(self, model) -> None:
        self._model = model
        self._db = DatabaseManager()

    def _set_attrs(self, **kwargs) -> None:
        for (key, value) in kwargs.items():
            setattr(self._model, key, value)

    async def _save(self, state: FSMContext) -> None:
        await state.update_data({self.__class__.__name__: self})

    async def _get_customer_from_msg(self, db_session: DbSessionManager, message: Message) -> Customer:
        attr_dict = {'tg_id': message.from_user.id}
        if message.contact:
            raw_phone_number = message.contact.phone_number
            phone_number = raw_phone_number if len(raw_phone_number) == 12 else f'+{raw_phone_number}'
            attr_dict = {'phone_number': phone_number}
        customer = await db_session.get_obj_by_attrs(Customer, **attr_dict)
        if await self._is_valid_customer(customer):
            return customer
        raise IsNotCustomer

    async def _is_valid_customer(self, customer: Customer) -> bool:
        return (customer and
                any(filter(self._is_valid_permission, await customer.awaitable_attrs.permissions)))

    @staticmethod
    def _is_valid_permission(permission: CustomerPermission) -> bool:
        return permission.beg_date <= datetime.date.today() <= (permission.end_date or datetime.date.today())

    @staticmethod
    def _get_id_from_callback(callback: CallbackQuery) -> int:
        return int(callback.data.split(':')[-1])


class UserManager(ServiceManager):

    def __init__(self):
        super().__init__(UserForm())

    async def validate_customer(self, session: AsyncSession, message: Message, state: FSMContext) -> None:
        db_session = self._db(session)
        customer = await self._get_customer_from_msg(db_session, message)
        valid_canteen_ids = await self._get_valid_canteen_ids(customer)
        self._set_attrs(
            customer_id=customer.id,
            tg_id=message.from_user.id,
            place_id=customer.place_id,
            canteen_ids=valid_canteen_ids
        )
        await self._save(state)

    async def _get_valid_canteen_ids(self, customer: Customer) -> list[int]:
        valid_canteen_ids = set(permission.canteen_id for permission in await customer.awaitable_attrs.permissions
                                if self._is_valid_permission(permission))
        if valid_canteen_ids:
            return sorted(valid_canteen_ids)
        raise ValidCanteensNotExist

    def is_auth(self) -> bool:
        return bool(self._model.place_id and self._model.tg_id)

    async def receive_place(self, session: AsyncSession) -> DeliveryPlace:
        db_session = self._db(session)
        return await db_session.get_obj_by_id(DeliveryPlace, self._model.place_id)

    def allowed_several_canteens(self) -> bool:
        return len(self._model.canteen_ids) > 1

    async def receive_canteens(self, session: AsyncSession) -> list[Canteen]:
        db_session = self._db(session)
        return [await db_session.get_obj_by_id(Canteen, canteen_id) for canteen_id in self._model.canteen_ids]

    async def receive_canteen_places(
            self,
            canteen: Canteen | None = None,
            session: AsyncSession | None = None,
            callback: CallbackQuery | None = None) -> list[DeliveryPlace]:
        if not canteen:
            db_session = self._db(session)
            canteen = await db_session.get_obj_by_id(Canteen, self._get_id_from_callback(callback))
        return await canteen.awaitable_attrs.places

    async def authorize_customer(self, session: AsyncSession, callback: CallbackQuery) -> None:
        await self._update_customer_data(
            session=session,
            tg_id=self._model.tg_id,
            place_id=self._get_id_from_callback(callback)
        )

    async def change_delivery_place(self, session: AsyncSession, callback: CallbackQuery) -> None:
        await self._update_customer_data(
            session=session,
            place_id=self._get_id_from_callback(callback)
        )

    async def _update_customer_data(self, session: AsyncSession, **kwargs):
        db_session = self._db(session)
        await db_session.update_obj(
            obj=await db_session.get_obj_by_id(Customer, self._model.customer_id),
            **kwargs
        )


class OrderManager(ServiceManager):

    def __init__(self):
        super().__init__(OrderForm())
        self._dll = OrdersDLL()
        self._offset = 3

    async def start_process_new_order(
            self, session: AsyncSession, state: FSMContext, message: Message) -> None:
        db_session = self._db(session)
        customer = await self._get_customer_from_msg(db_session, message)
        place = await db_session.get_obj_by_id(DeliveryPlace, customer.place_id)
        self._set_attrs(
            customer_id=customer.id,
            canteen_id=place.canteen_id,
            place_id=place.id,
            place_name=place.name,
            custom_menu=place.custom_menu
        )
        await self._save(state)

    async def receive_valid_menus(self, session: AsyncSession, state: FSMContext) -> list[Menu]:
        db_session = self._db(session)
        canteen = await db_session.get_obj_by_id(Canteen, self._model.canteen_id)
        valid_menus = [
            menu for menu in await canteen.awaitable_attrs.menus if await self._is_valid_menu(db_session, menu)
        ]
        if valid_menus:
            self._set_attrs(canteen_name=canteen.name)
            await self._save(state)
            return valid_menus
        raise ValidMenusNotExist

    async def _is_valid_menu(self, db_session: DbSessionManager, menu: Menu) -> bool:
        order = await db_session.get_obj_by_attrs(Order, menu_id=menu.id, customer_id=self._model.customer_id)
        return not order and (menu.beg_time <= datetime.datetime.now() <= menu.end_time)

    async def _get_menu_info(self, db_session: DbSessionManager, menu_id: int) -> Menu:
        menu = await db_session.get_obj_by_id(Menu, menu_id)
        self._set_attrs(
            menu_id=menu.id,
            menu_name=menu.name,
            menu_date=menu.date
        )
        return menu

    async def _get_raw_details_from_menu(self, menu: Menu) -> dict[int, DetailForm]:
        raw_details = {
            position.id: DetailForm(
                menu_pos_id=position.id,
                menu_pos_name=position.name,
                menu_pos_cost=position.cost if position.cost else 0
            ) for position in await menu.awaitable_attrs.positions
        }
        self._set_attrs(raw_details=raw_details)
        return raw_details

    async def receive_menu_positions(
            self, session: AsyncSession, callback: CallbackQuery, state: FSMContext) -> tuple[DetailForm]:
        db_session = self._db(session)
        menu = await self._get_menu_info(db_session, self._get_id_from_callback(callback))
        raw_details = await self._get_raw_details_from_menu(menu)
        temp_details = self._chunked_by_offset(raw_details.values(), self._offset)
        self._set_attrs(temp_details=temp_details)
        result = next(self._model.temp_details)
        await self._save(state)
        return result

    @staticmethod
    def _chunked_by_offset(iterable: Iterable, offset: int) -> Generator[Any, None, None]:
        it = iter(iterable)
        while batch := tuple(islice(it, offset)):
            yield batch

    async def continue_receiving_positions(self, state: FSMContext) -> tuple[DetailForm]:
        try:
            result = next(self._model.temp_details)
            await self._save(state)
            return result
        except StopIteration:
            raise EmptyException

    def complex_menu(self) -> bool:
        return not self._model.custom_menu

    async def _get_details_from_complex_menu(self, menu: Menu) -> list[DetailForm]:
        selected_details = [
            DetailForm(
                menu_pos_id=position.id,
                menu_pos_name=position.name,
                menu_pos_cost=position.cost if position.cost else 0,
                quantity=position.complex_qty
            ) for position in await menu.awaitable_attrs.positions if position.complex_qty
        ]
        self._set_attrs(selected_details=selected_details)
        return selected_details

    async def receive_complex_order(
            self, session: AsyncSession, callback: CallbackQuery, state: FSMContext) -> OrderForm:
        db_session = self._db(session)
        menu = await self._get_menu_info(db_session, self._get_id_from_callback(callback))
        selected_details = await self._get_details_from_complex_menu(menu)
        self._set_attrs(amt=sum(detail.menu_pos_cost * detail.quantity for detail in selected_details))
        await self._save(state)
        return self.receive_full_order()

    async def increment_position_quantity(self, callback: CallbackQuery, state: FSMContext) -> DetailForm:
        detail: DetailForm = self._model.raw_details.get(self._get_id_from_callback(callback))
        if callback.data.startswith('plus'):
            detail.quantity += 1
        elif detail.quantity - 1 > 0:
            detail.quantity -= 1
        else:
            raise InvalidPositionQuantity
        await self._save(state)
        return detail

    async def add_position_to_order(self, callback: CallbackQuery, state: FSMContext) -> None:
        detail: DetailForm = self._model.raw_details.get(self._get_id_from_callback(callback))
        new_amt = detail.quantity * detail.menu_pos_cost + self._model.amt
        self._set_attrs(amt=new_amt)
        self._model.selected_details.append(detail)
        await self._save(state)

    def receive_full_order(self) -> OrderForm:
        if not self._model.selected_details:
            raise NoPositionsSelected
        return self._model

    async def confirm_pending_order(self, session: AsyncSession) -> None:
        db_session = self._db(session)
        order = self._create_order_from_model()
        if await self._is_valid_order(db_session, order):
            await db_session.save_new_obj(order)
        else:
            raise InvalidOrder

    async def _is_valid_order(self, db_session: DbSessionManager, order: Order) -> bool:
        customer = await db_session.get_obj_by_id(Customer, order.customer_id)
        menu = await db_session.get_obj_by_id(Menu, order.menu_id)
        return await self._is_valid_customer(customer) and await self._is_valid_menu(db_session, menu)

    def _create_order_from_model(self) -> Order:
        order_details = [
            OrderDetail(
                menu_pos_id=detail.menu_pos_id,
                quantity=detail.quantity
            ) for detail in self._model.selected_details
        ]
        return Order(
            created_at=datetime.datetime.now(),
            amt=self._model.amt,
            customer_id=self._model.customer_id,
            menu_id=self._model.menu_id,
            place_id=self._model.place_id,
            details=order_details
        )

    @staticmethod
    async def _create_form_details_from_order_details(
            db_session: DbSessionManager, order_details: list[OrderDetail]) -> list[DetailForm]:
        details = []
        for order_detail in order_details:
            menu_pos = await db_session.get_obj_by_id(MenuPosition, order_detail.menu_pos_id)
            details.append(
                DetailForm(
                    detail_id=order_detail.id,
                    quantity=order_detail.quantity,
                    menu_pos_id=menu_pos.id,
                    menu_pos_name=menu_pos.name,
                    menu_pos_cost=menu_pos.cost
                )
            )
        return details

    async def _create_order_form_from_order(self, db_session, order: Order) -> OrderForm:
        menu = await db_session.get_obj_by_id(Menu, order.menu_id)
        place = await db_session.get_obj_by_id(DeliveryPlace, order.place_id)
        canteen = await db_session.get_obj_by_id(Canteen, place.canteen_id)
        details = await self._create_form_details_from_order_details(db_session, await order.awaitable_attrs.details)
        return OrderForm(
            order_id=order.id,
            created_at=order.created_at,
            amt=order.amt,
            canteen_name=canteen.name,
            place_name=place.name,
            menu_name=menu.name,
            menu_date=menu.date,
            selected_details=details
        )

    async def receive_customer_orders(
            self, session: AsyncSession, message: Message, state: FSMContext) -> None:
        db_session = self._db(session)
        customer = await self._get_customer_from_msg(db_session, message)
        valid_orders = [
            order for order in await customer.awaitable_attrs.orders if not order.sent_to_eis
        ]
        if valid_orders:
            data = [await self._create_order_form_from_order(db_session, order) for order in valid_orders]
            self._dll.set_data(data)
            await self._save(state)
        else:
            raise ValidOrdersNotExist

    def current_order(self) -> OrderForm:
        return self._dll.get_cur_data()

    def current_order_position(self) -> tuple[int, int]:
        return self._dll.cur, self._dll.size

    async def process_scroll(self, callback: CallbackQuery, state: FSMContext) -> None:
        if callback.data.startswith('next'):
            self._dll.turn_next()
        elif callback.data.startswith('prev'):
            self._dll.turn_prev()
        await self._save(state)

    async def cancel_order(self, session: AsyncSession, state: FSMContext) -> None:
        db_session = self._db(session)
        order_form = self._dll.delete_cur_data()
        await db_session.delete_obj_by_id(Order, order_form.order_id)
        await self._save(state)
