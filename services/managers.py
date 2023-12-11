import datetime
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, ScalarResult
from sqlalchemy.orm import selectinload
from services.models import OrderForm, UserForm, DetailForm
from database.managers import DatabaseManager, DbSessionManager
from database.models import (Canteen, DeliveryPlace, Menu, Order, OrderDetail, Customer,
                             CustomerPermission, MenuPosition)
from services.utils import get_id_from_callback
from exceptions import *


class ServiceManager:

    def __init__(self, model):
        self._model = model
        self._db = DatabaseManager()

    def _get_model(self):
        return self._model

    def _set_attrs(self, **kwargs):
        for (key, value) in kwargs.items():
            setattr(self._model, key, value)

    def _get_attr(self, attr_name: str):
        return getattr(self._model, attr_name)

    async def _save(self, state: FSMContext):
        await state.update_data({self.__class__.__name__: self})

    async def _get_customer_from_msg(self, db_session: DbSessionManager, message: Message) -> Customer:
        if message.contact:
            raw_phone_number = message.contact.phone_number
            phone_number = raw_phone_number if len(raw_phone_number) == 12 else f'+{raw_phone_number}'
            stmt = select(Customer).where(Customer.phone_number == phone_number).options(
                selectinload(Customer.permissions))
        else:
            stmt = select(Customer).where(Customer.tg_id == message.from_user.id).options(
                selectinload(Customer.permissions))
        customer = db_session.execute_stmt_with_one_or_none_return(stmt)
        if customer and self._is_valid_customer(customer):
            return customer
        raise IsNotCustomer

    @staticmethod
    def _is_valid_customer(customer: Customer) -> bool:
        return any(
            filter(
                lambda permission: permission.beg_date <= datetime.date.today() <= (
                        permission.end_date or datetime.date.today()),
                customer.permissions
            )
        )


class OrderManager(ServiceManager):

    def __init__(self):
        super().__init__(OrderForm())

    async def start_process_new_order(
            self, session: AsyncSession, state: FSMContext, message: Message) -> None:
        db_session = self._db(session)
        customer = await self._get_customer_from_msg(db_session, message)
        place = await db_session.get_obj_by_id(DeliveryPlace, customer.place_id)
        canteen = await db_session.get_obj_by_id(Canteen, place.canteen_id)
        self._set_attrs(
            customer_id=customer.id,
            canteen_id=canteen.id,
            canteen_name=canteen.name,
            place_id=place.id,
            place_name=place.name
        )
        await self._save(state)

    async def receive_valid_menus(self, session: AsyncSession) -> list[Menu]:
        db_session = self._db(session)
        canteen_id = await self._get_canteen_id_by_user(db_session)
        stmt = select(Menu).where(Menu.canteen_id == canteen_id).order_by(Menu.date)
        menus = await db_session.execute_stmt_with_many_return(stmt)
        valid_menus = [menu for menu in menus if await self._is_valid_menu(db_session, menu)]
        if valid_menus:
            return valid_menus
        raise ValidMenusNotExist

    async def _get_canteen_id_by_user(self, db_session: DbSessionManager) -> int | None:
        stmt = (select(DeliveryPlace.canteen_id).
                join(DeliveryPlace.customers).
                where(Customer.id == self._get_attr('customer_id')))
        return await db_session.execute_stmt_with_one_or_none_return(stmt)

    async def _is_valid_menu(self, db_session: DbSessionManager, menu: Menu) -> bool:
        stmt = select(Order).where(
            Order.menu_id == menu.id,
            Order.customer_id == self._get_attr('customer_id')
        )
        order = await db_session.execute_stmt_with_one_or_none_return(stmt)
        return not order and (menu.beg_time <= datetime.datetime.now() <= menu.end_time)

    async def receive_menu_positions(
            self, session: AsyncSession, callback: CallbackQuery, state: FSMContext) -> list[DetailForm]:
        db_session = self._db(session)
        menu = await db_session.get_obj_by_id(Menu, get_id_from_callback(callback))
        self._set_attrs(
            menu_id=menu.id,
            menu_name=menu.name,
            menu_date=menu.date
        )
        stmt = select(MenuPosition).where(MenuPosition.menu_id == menu.id).order_by(MenuPosition.id)
        positions = await db_session.execute_stmt_with_many_return(stmt)
        raw_details = {
            position.id: DetailForm(
                menu_pos_id=position.id,
                menu_pos_name=position.name,
                menu_pos_cost=position.cost if position.cost else 0
            ) for position in positions
        }
        self._set_attrs(raw_details=raw_details)
        await self._save(state)
        return list(raw_details.values())

    async def increment_position_quantity(self, callback: CallbackQuery, state: FSMContext) -> DetailForm:
        detail: DetailForm = self._get_attr('raw_details').get(get_id_from_callback(callback))
        if callback.data == 'plus':
            detail.quantity += 1
        elif detail.quantity - 1 > 0:
            detail.quantity -= 1
        else:
            raise InvalidPositionQuantity
        await self._save(state)
        return detail

    async def add_position_to_order(self, callback: CallbackQuery, state: FSMContext):
        detail: DetailForm = self._get_attr('raw_details').get(get_id_from_callback(callback))
        new_amt = detail.quantity * detail.menu_pos_cost + self._get_attr('amt')
        self._set_attrs(amt=new_amt)
        self._get_attr('selected_details').append(detail)
        await self._save(state)

    def receive_full_order(self):
        return self._get_model()

    async def process_pending_order(self, session: AsyncSession):
        db_session = self._db(session)
        order = self._create_order_from_model()
        if await self._is_valid_order(db_session, order):
            await db_session.save_new_obj(order)
        else:
            raise InvalidOrder

    async def _is_valid_order(self, db_session: DbSessionManager, order: Order) -> bool:
        customer = await db_session.get_obj_by_id(Customer, order.customer_id)
        menu = await db_session.get_obj_by_id(Menu, order.menu_id)
        return self._is_valid_customer(customer) and await self._is_valid_menu(db_session, menu)

    def _create_order_from_model(self):
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

    async def _fill_model_by_order(self, db_session, order: Order):
        menu = await db_session.get_obj_by_id(Menu, order.menu_id)
        place = await db_session.get_obj_by_id(DeliveryPlace, order.place_id)
        canteen = await db_session.get_obj_by_id(Canteen, place.canteen_id)
        details = []
        for order_detail in order.details:
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
        return self._set_attrs(
            order_id=order.id,
            created_at=order.created_at,
            amt=order.amt,
            canteen_name=canteen.name,
            place_name=place.name,
            menu_name=menu.name,
            menu_date=menu.date,
            selected_details=details
        )

    async def receive_customer_orders(self, session: AsyncSession, message: Message):
        db_session = self._db(session)
        customer = await self._get_customer_from_msg(db_session, message)
        stmt = select(Order).where(Order.customer_id == customer.id).options(selectinload(Order.details))
        valid_orders = [
            order for order in await db_session.execute_stmt_with_many_return(stmt) if not order.sent_to_eis
        ]
        if valid_orders:
            return valid_orders
        else:
            raise ValidOrdersNotExist










