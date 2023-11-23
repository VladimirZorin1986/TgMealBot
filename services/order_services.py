import datetime
from database.models import Customer, DeliveryPlace, Menu, MenuPosition, Order, OrderDetail
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, ScalarResult
from sqlalchemy.orm import selectinload
from utils.service_models import CustomerId, MenuId, MenuPosId, OrderForm
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext


async def _get_canteen_id_by_user(session: AsyncSession, customer_id: CustomerId):
    stmt = select(DeliveryPlace.canteen_id).join(DeliveryPlace.customers).where(Customer.id == customer_id)
    result = await session.execute(stmt)
    return result.scalar_one()


async def get_valid_menus_by_user(session: AsyncSession, customer_id: CustomerId) -> list[Menu]:
    canteen_id = await _get_canteen_id_by_user(session, customer_id)
    stmt = select(Menu).where(Menu.canteen_id == canteen_id).order_by(Menu.date)
    result = await session.execute(stmt)
    menus = result.scalars()
    return [menu for menu in menus if await _is_valid_menu(session, menu)]


async def _is_valid_menu(session: AsyncSession, menu: Menu) -> bool:
    stmt = select(Order).where(Order.menu_id == menu.id)
    result = await session.execute(stmt)
    return not (result.scalar_one_or_none()) and (menu.beg_time <= datetime.datetime.now() <= menu.end_time)


async def get_menu_positions_by_menu(session: AsyncSession, menu_id: MenuId) -> ScalarResult[MenuPosition]:
    stmt = select(MenuPosition).where(MenuPosition.menu_id == menu_id).order_by(MenuPosition.id)
    positions = await session.execute(stmt)
    return positions.scalars()


async def get_menu_position_by_id(session: AsyncSession, menu_pos_id: MenuPosId) -> MenuPosition | None:
    position = await session.get(MenuPosition, menu_pos_id)
    return position


async def save_new_order(session: AsyncSession, order: Order) -> None:
    session.add(order)
    await session.commit()


async def delete_order(session: AsyncSession, order: Order) -> None:
    await session.delete(order)
    await session.commit()


async def get_orders_by_customer(session: AsyncSession, customer_id: CustomerId) -> ScalarResult[Order]:
    stmt = select(Order).where(Order.customer_id == customer_id).options(selectinload(Order.details))
    result = await session.execute(stmt)
    return result.scalars()


async def get_menu_by_id(session: AsyncSession, menu_id: MenuId) -> Menu | None:
    menu = await session.get(Menu, menu_id)
    return menu


async def create_order_from_form(order_form: OrderForm) -> Order:
    amt = sum(map(lambda detail: detail.cost, order_form.details))
    return Order(
        date=datetime.date.today(),
        amt=amt,
        customer_id=order_form.customer_id,
        menu_id=order_form.menu_id,
        details=order_form.details
    )


async def create_order_form(customer_id: CustomerId, state: FSMContext) -> None:
    await state.update_data({'order_form': OrderForm(customer_id=customer_id)})


async def get_order_form(state: FSMContext) -> OrderForm:
    data = await state.get_data()
    return data.get('order_form')


async def remember_position(message: Message, state: FSMContext, position: MenuPosition) -> None:
    await state.update_data({str(message.message_id): position})


async def load_position(state: FSMContext, message: Message) -> MenuPosition:
    data = await state.get_data()
    return data.get(str(message.message_id))


async def add_position_to_order_form(position: MenuPosition, state: FSMContext) -> None:
    order_form = await get_order_form(state)
    order_form.details.append(OrderDetail(quantity=position.qty, menu_pos_id=position.id))
    await state.update_data(order_form=order_form)


async def add_menu_id_to_order_form(menu_id: MenuId, state: FSMContext) -> None:
    order_form = await get_order_form(state)
    order_form.menu_id = menu_id
    await state.update_data(order_form=order_form)


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


