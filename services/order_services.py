import asyncio
import datetime
from database.models import Customer, Canteen, DeliveryPlace, Menu, MenuPosition, Order, OrderDetail
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from aiogram.types import CallbackQuery


async def _get_canteen_id_by_user(session: AsyncSession, customer_id: int):
    stmt = select(DeliveryPlace.canteen_id).join(DeliveryPlace.customers).where(Customer.id == customer_id)
    result = await session.execute(stmt)
    return result.scalar_one()


async def get_valid_menus_by_user(session: AsyncSession, customer_id: int) -> list[Menu]:
    canteen_id = await _get_canteen_id_by_user(session, customer_id)
    stmt = select(Menu).where(Menu.canteen_id == canteen_id).order_by(Menu.date)
    result = await session.execute(stmt)
    menus = result.scalars()
    return [menu for menu in menus if await _is_valid_menu(session, menu)]


async def _is_valid_menu(session: AsyncSession, menu: Menu) -> bool:
    stmt = select(Order).where(Order.menu_id == menu.id)
    result = await session.execute(stmt)
    return not (result.scalar_one_or_none()) and (menu.beg_time <= datetime.datetime.now() <= menu.end_time)


async def get_menu_positions_by_menu(session: AsyncSession, menu_id: int):
    stmt = select(MenuPosition).where(MenuPosition.menu_id == menu_id).order_by(MenuPosition.id)
    positions = await session.execute(stmt)
    return positions.scalars()


async def get_menu_position_by_id(session: AsyncSession, menu_pos_id: int):
    stmt = select(MenuPosition).where(MenuPosition.id == menu_pos_id)
    position = await session.execute(stmt)
    return position.scalar_one()


async def save_new_order(session: AsyncSession, order: Order):
    session.add(order)
    await session.commit()


async def delete_order(session: AsyncSession, order: Order):
    await session.delete(order)
    await session.commit()


async def get_orders_by_customer(session: AsyncSession, customer_id: int):
    stmt = select(Order).where(Order.customer_id == customer_id).options(selectinload(Order.details))
    result = await session.execute(stmt)
    return result.scalars()


async def get_menu_by_id(session: AsyncSession, menu_id: int):
    stmt = select(Menu).where(Menu.id == menu_id)
    result = await session.execute(stmt)
    return result.scalar_one()


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


