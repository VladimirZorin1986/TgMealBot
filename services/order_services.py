import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, ScalarResult
from sqlalchemy.orm import selectinload
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from services.user_services import get_customer_from_msg
from utils.service_models import CustomerId, MenuId, OrderForm, ExistOrderForm, DetailForm, NewOrderForm, ServiceManager
from database.models import Customer, DeliveryPlace, Menu, MenuPosition, Order, OrderDetail, Canteen
from exceptions import InvalidPositionQuantity, InvalidOrderMenu, ValidMenusNotExist, ValidOrdersNotExist, NoPositionsSelected
from utils.service_functions import get_id_from_callback
from database.functions import get_obj_by_id


class OrderManager(ServiceManager):

    def __init__(self):
        super().__init__(NewOrderForm())

    async def start_process_new_order(
            self, session: AsyncSession, state: FSMContext, message: Message) -> None:
        customer = await get_customer_from_msg(session, message)
        place = await get_obj_by_id(session, DeliveryPlace, customer.place_id)
        canteen = await get_obj_by_id(session, Canteen, place.canteen_id)
        self.set_attrs(
            customer_id=customer.id,
            canteen_id=canteen.id,
            canteen_name=canteen.name,
            place_id=place.id,
            place_name=place.name
        )
        await self.save(state)

    async def receive_valid_menus(self, session: AsyncSession) -> list[Menu]:
        return await get_valid_menus_by_user(session, self.get_attr('customer_id'))

    async def process_set_order_menu(
            self, session: AsyncSession, callback: CallbackQuery, state: FSMContext) -> None:
        menu = await get_obj_by_id(session, Menu, get_id_from_callback(callback))
        self.set_attrs(
            menu_id=menu.id,
            menu_name=menu.name,
            menu_date=menu.date
        )
        await self.save(state)

    async def receive_menu_positions(self, session: AsyncSession):
        return await get_menu_positions_by_menu(session, self.get_attr('menu_id'))


async def _get_canteen_id_by_user(session: AsyncSession, customer_id: CustomerId):
    stmt = select(DeliveryPlace.canteen_id).join(DeliveryPlace.customers).where(Customer.id == customer_id)
    result = await session.execute(stmt)
    return result.scalar_one()


async def get_valid_menus_by_user(session: AsyncSession, customer_id: CustomerId) -> list[Menu]:
    canteen_id = await _get_canteen_id_by_user(session, customer_id)
    stmt = select(Menu).where(Menu.canteen_id == canteen_id).order_by(Menu.date)
    result = await session.execute(stmt)
    menus = result.scalars()
    valid_menus = [menu for menu in menus if await _is_valid_menu(session, menu, customer_id)]
    if valid_menus:
        return valid_menus
    raise ValidMenusNotExist


async def _is_valid_menu(session: AsyncSession, menu: Menu, customer_id: CustomerId) -> bool:
    stmt = select(Order).where(
        Order.menu_id == menu.id,
        Order.customer_id == customer_id
    )
    result = await session.execute(stmt)
    return not (result.scalar_one_or_none()) and (menu.beg_time <= datetime.datetime.now() <= menu.end_time)


async def get_menu_positions_by_menu(session: AsyncSession, menu_id: MenuId) -> ScalarResult[MenuPosition]:
    stmt = select(MenuPosition).where(MenuPosition.menu_id == menu_id).order_by(MenuPosition.id)
    positions = await session.execute(stmt)
    return positions.scalars()


async def get_menu_positions(
        session: AsyncSession, callback: CallbackQuery, state: FSMContext) -> ScalarResult[MenuPosition]:
    menu_id = get_id_from_callback(callback)
    await add_menu_id_to_order_form(menu_id, state)
    return await get_menu_positions_by_menu(session, menu_id)


async def confirm_pending_order(session: AsyncSession, state: FSMContext) -> None:
    order_form = await get_order_form(state)
    menu = await get_obj_by_id(session, Menu, order_form.menu_id)
    if _is_valid_menu(session, menu, order_form.customer_id):
        order = await create_order_from_form(order_form)
        session.add(order)
        await session.commit()
    else:
        raise InvalidOrderMenu


async def delete_order(session: AsyncSession, order: Order) -> None:
    await session.delete(order)
    await session.commit()


async def get_orders_by_customer(session: AsyncSession, customer_id: CustomerId) -> list[Order]:
    stmt = select(Order).where(Order.customer_id == customer_id).options(selectinload(Order.details))
    result = await session.execute(stmt)
    orders = [order for order in result.scalars() if not order.sent_to_eis]
    if orders:
        return orders
    raise ValidOrdersNotExist


async def create_order_from_form(order_form: OrderForm) -> Order:
    return Order(
        created_at=datetime.datetime.now(),
        amt=order_form.amt,
        customer_id=order_form.customer_id,
        menu_id=order_form.menu_id,
        place_id=order_form.place_id,
        details=list(order_form.details.values())
    )


async def create_form_from_order(session: AsyncSession, order: Order) -> ExistOrderForm:
    menu = await get_obj_by_id(session, Menu, order.menu_id)
    place = await get_obj_by_id(session, DeliveryPlace, order.place_id)
    canteen = await get_obj_by_id(session, Canteen, place.canteen_id)
    details = []
    for order_detail in order.details:
        menu_pos = await get_obj_by_id(session, MenuPosition, order_detail.menu_pos_id)
        details.append(
            DetailForm(
                detail_id=order_detail.id,
                quantity=order_detail.quantity,
                menu_pos_id=menu_pos.id,
                menu_pos_name=menu_pos.name,
                menu_pos_cost=menu_pos.cost
            )
        )
    return ExistOrderForm(
        order_id=order.id,
        created_at=order.created_at,
        amt=order.amt,
        canteen_name=canteen.name,
        place_name=place.name,
        menu_name=menu.name,
        menu_date=menu.date,
        details=details
    )


async def create_order_form(customer: Customer, state: FSMContext) -> None:
    await state.update_data({'order_form': OrderForm(customer_id=customer.id, place_id=customer.place_id)})


async def get_order_form(state: FSMContext) -> OrderForm:
    data = await state.get_data()
    return data.get('order_form')


async def remember_position(message: Message, state: FSMContext, position: MenuPosition) -> None:
    await state.update_data({str(message.message_id): position})


async def load_position(state: FSMContext, message: Message) -> MenuPosition:
    data = await state.get_data()
    return data.get(str(message.message_id))


async def add_position_to_order_form(callback: CallbackQuery, state: FSMContext) -> None:
    position = await load_position(state, callback.message)
    order_form = await get_order_form(state)
    order_form.details.update(
        {(position.name, position.cost): OrderDetail(quantity=position.quantity, menu_pos_id=position.id)}
    )
    await state.update_data(order_form=order_form)


async def set_order_amt(state: FSMContext):
    order_form = await get_order_form(state)
    if order_form.details:
        amt = sum(detail.quantity * cost for (_, cost), detail in order_form.details.items())
        order_form.amt = amt
        await state.update_data(order_form=order_form)
        return order_form
    else:
        raise NoPositionsSelected


async def add_menu_id_to_order_form(menu_id: MenuId, state: FSMContext) -> None:
    order_form = await get_order_form(state)
    order_form.menu_id = menu_id
    await state.update_data(order_form=order_form)


async def increment_position_qty(state: FSMContext, callback: CallbackQuery) -> MenuPosition:
    position = await load_position(state, callback.message)
    if callback.data == 'plus':
        position.quantity += 1
    elif position.quantity - 1 > 0:
        position.quantity -= 1
    else:
        raise InvalidPositionQuantity
    return position


if __name__ == '__main__':
    import asyncio
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker


    async def test_funcs():
        engine = create_async_engine(
            "postgresql+asyncpg://postgres:postgres@localhost/test_pg",
            echo=True,
        )

        # async_sessionmaker: a factory for new AsyncSession objects.
        # expire_on_commit - don't expire objects after transaction commit
        async_session = async_sessionmaker(engine, expire_on_commit=False)

        async with async_session() as session:
            menus = await get_valid_menus_by_user(session, 1106699847)
            for menu in menus:
                print(f'{menu.id} {menu.name}')
                positions = await get_menu_positions_by_menu(session, menu.id)
                for position in positions:
                    print(f'{position.id} {position.name}')


        # for AsyncEngine created in function scope, close and
        # clean-up pooled connections
        await engine.dispose()


    asyncio.run(test_funcs())


