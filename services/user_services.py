import datetime
from database.models import Customer, Canteen, DeliveryPlace, CustomerPermission
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, ScalarResult
from sqlalchemy.orm import selectinload
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from utils.service_functions import get_id_from_callback
from exceptions import IsNotCustomer


async def _get_canteens(session: AsyncSession) -> ScalarResult[Canteen]:
    stmt = select(Canteen)
    canteens = await session.execute(stmt)
    return canteens.scalars()


async def get_canteen_by_id(session: AsyncSession, canteen_id: int) -> Canteen | None:
    return await session.get(Canteen, ident=canteen_id)


async def get_valid_canteens(session: AsyncSession, customer: Customer) -> list[Canteen]:
    canteens = await _get_canteens(session)
    valid_canteen_ids = set(permission.canteen_id for permission in customer.permissions
                            if _is_valid_permission(permission))
    return [canteen for canteen in canteens if canteen.id in valid_canteen_ids]


async def get_places_by_canteen(session: AsyncSession, canteen: Canteen) -> ScalarResult[DeliveryPlace]:
    stmt = select(DeliveryPlace).where(DeliveryPlace.canteen_id == canteen.id)
    places = await session.execute(stmt)
    return places.scalars()


async def get_customer_by_phone(session: AsyncSession, state: FSMContext, phone_number: str) -> Customer:
    phone_number = phone_number if len(phone_number) == 12 else f'+{phone_number}'
    stmt = select(Customer).where(Customer.phone_number == phone_number).options(selectinload(Customer.permissions))
    result = await session.execute(stmt)
    customer = result.scalar_one_or_none()
    if customer and _is_valid_customer(customer):
        await state.update_data(customer_id=customer.id)
        return customer
    raise IsNotCustomer


def _is_valid_permission(permission: CustomerPermission) -> bool:
    return permission.beg_date <= datetime.date.today() <= (permission.end_date or datetime.date.today())


def _is_valid_customer(customer: Customer) -> bool:
    return any(filter(_is_valid_permission, customer.permissions))


async def get_customer_by_tg_id(session: AsyncSession, state: FSMContext, tg_id: int) -> Customer:
    stmt = select(Customer).where(Customer.tg_id == tg_id)
    result = await session.execute(stmt.options(selectinload(Customer.permissions)))
    customer = result.scalar_one_or_none()
    if customer and _is_valid_customer(customer):
        await state.update_data(customer_id=customer.id)
        return customer
    raise IsNotCustomer


async def is_auth(session: AsyncSession, user_id: int) -> bool:
    stmt = select(Customer).where(Customer.tg_id == user_id).where(Customer.place_id is not None)
    result = await session.execute(stmt.options(selectinload(Customer.permissions)))
    customer = result.scalar_one_or_none()
    if customer and _is_valid_customer(customer):
        return True
    return False


async def _update_customer(session: AsyncSession, customer_id: int, tg_id: int, place_id: int) -> None:
    stmt = update(Customer).where(Customer.id == customer_id).values(tg_id=tg_id, place_id=place_id)
    await session.execute(stmt)
    await session.commit()


async def update_customer_data(session: AsyncSession, callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    customer_id = data.get('customer_id')
    tg_id = callback.from_user.id
    place_id = get_id_from_callback(callback)
    await _update_customer(
        session=session,
        customer_id=customer_id,
        tg_id=tg_id,
        place_id=place_id
    )


async def get_customer_by_id(session: AsyncSession, customer_id: int) -> Customer | None:
    return await session.get(entity=Customer, ident=customer_id)


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
            canteens = await _get_canteens(session)
            for canteen in canteens:
                print(f'{canteen.id} {canteen.name}')

            places = await get_places_by_canteen(session, 1)
            for place in places:
                print(f'{place.id} {place.name}')

            is_emp1 = await get_customer_by_phone(session, '+79856254915')
            print(is_emp1.id)
            is_emp2 = await get_customer_by_phone(session, '+79851310741')
            print(is_emp2)

        # for AsyncEngine created in function scope, close and
        # clean-up pooled connections
        await engine.dispose()


    asyncio.run(test_funcs())

