import datetime
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
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

    def _set_attrs(self, **kwargs):
        for (key, value) in kwargs.items():
            setattr(self._model, key, value)

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
        customer = await db_session.execute_stmt_with_one_or_none_return(stmt)
        if customer and self._is_valid_customer(customer):
            return customer
        raise IsNotCustomer

    def _is_valid_customer(self, customer: Customer) -> bool:
        return any(filter(self._is_valid_permission, customer.permissions))

    @staticmethod
    def _is_valid_permission(permission: CustomerPermission) -> bool:
        return permission.beg_date <= datetime.date.today() <= (permission.end_date or datetime.date.today())


class UserManager(ServiceManager):

    def __init__(self):
        super().__init__(UserForm())

    async def start_auth_process(self, session: AsyncSession, message: Message, state: FSMContext):
        db_session = self._db(session)
        customer = await self._get_customer_from_msg(db_session, message)
        valid_canteen_ids = self._get_valid_canteen_ids(customer)
        self._set_attrs(
            customer_id=customer.id,
            tg_id=message.from_user.id,
            canteen_ids=valid_canteen_ids
        )
        await self._save(state)

    def _get_valid_canteen_ids(self, customer: Customer) -> list[int]:
        valid_canteen_ids = set(permission.canteen_id for permission in customer.permissions
                                if self._is_valid_permission(permission))
        if valid_canteen_ids:
            return sorted(valid_canteen_ids)
        raise ValidCanteensNotExist

    def allowed_several_canteens(self) -> bool:
        return len(self._model.canteen_ids) > 1

    async def receive_canteens(self, session: AsyncSession) -> list[Canteen]:
        db_session = self._db(session)
        return [db_session.get_obj_by_id(Canteen, canteen_id) for canteen_id in self._model.canteen_ids]

    async def receive_canteen_places(self, session: AsyncSession, canteen_id: int | None = None):
        canteen_id = canteen_id or self._model.canteen_ids[0]
        db_session = self._db(session)
        stmt = select(DeliveryPlace).where(DeliveryPlace.canteen_id == canteen_id)
        return await db_session.execute_stmt_with_many_return(stmt)

    async def authorize_customer(self, session: AsyncSession, callback: CallbackQuery) -> None:
        self._set_attrs(place_id=get_id_from_callback(callback))
        await self._update_customer_data(
            session=session,
            tg_id=self._model.tg_id,
            place_id=self._model.place_id
        )

    async def change_delivery_place(self, session: AsyncSession, callback: CallbackQuery) -> None:
        self._set_attrs(place_id=get_id_from_callback(callback))
        await self._update_customer_data(
            session=session,
            place_id=self._model.place_id
        )

    async def _update_customer_data(self, session: AsyncSession, **kwargs):
        db_session = self._db(session)
        await db_session.update_obj(
            obj=db_session.get_obj_by_id(Customer, self._model.customer_id),
            **kwargs
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
                where(Customer.id == self._model.customer_id))
        return await db_session.execute_stmt_with_one_or_none_return(stmt)

    async def _is_valid_menu(self, db_session: DbSessionManager, menu: Menu) -> bool:
        stmt = select(Order).where(
            Order.menu_id == menu.id,
            Order.customer_id == self._model.customer_id
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
        detail: DetailForm = self._model.raw_details.get(get_id_from_callback(callback))
        if callback.data == 'plus':
            detail.quantity += 1
        elif detail.quantity - 1 > 0:
            detail.quantity -= 1
        else:
            raise InvalidPositionQuantity
        await self._save(state)
        return detail

    async def add_position_to_order(self, callback: CallbackQuery, state: FSMContext) -> None:
        detail: DetailForm = self._model.raw_details.get(get_id_from_callback(callback))
        new_amt = detail.quantity * detail.menu_pos_cost + self._model.amt
        self._set_attrs(amt=new_amt)
        self._model.selected_details.append(detail)
        await self._save(state)

    def receive_full_order(self):
        return self._model

    async def process_pending_order(self, session: AsyncSession) -> None:
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
        details = await self._create_form_details_from_order_details(db_session, order.details)
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
            self, session: AsyncSession, message: Message) -> list[OrderForm]:
        db_session = self._db(session)
        customer = await self._get_customer_from_msg(db_session, message)
        stmt = select(Order).where(Order.customer_id == customer.id).options(selectinload(Order.details))
        valid_orders = [
            order for order in await db_session.execute_stmt_with_many_return(stmt) if not order.sent_to_eis
        ]
        if valid_orders:
            return [await self._create_order_form_from_order(db_session, order) for order in valid_orders]
        else:
            raise ValidOrdersNotExist

    async def cancel_order(self, session: AsyncSession, callback: CallbackQuery) -> None:
        db_session = self._db(session)
        await db_session.delete_obj_by_id(Order, get_id_from_callback(callback))
