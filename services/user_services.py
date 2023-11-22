from database.models import Customer, Canteen, DeliveryPlace
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, ScalarResult
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from services.other_services import get_id_from_callback


async def get_canteens(session: AsyncSession) -> ScalarResult[Canteen]:
    stmt = select(Canteen)
    canteens = await session.execute(stmt)
    return canteens.scalars()


async def get_places_by_canteen(session: AsyncSession, canteen_id: int) -> ScalarResult[DeliveryPlace]:
    stmt = select(DeliveryPlace).where(DeliveryPlace.canteen_id == canteen_id)
    places = await session.execute(stmt)
    return places.scalars()


async def get_customer_by_phone(session: AsyncSession, phone_number: str) -> Customer | None:
    phone_number = phone_number if len(phone_number) == 12 else f'+{phone_number}'
    stmt = select(Customer).where(Customer.phone_number == phone_number)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_customer_by_tg_id(session: AsyncSession, tg_id: int) -> Customer | None:
    stmt = select(Customer).where(Customer.tg_id == tg_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def is_auth(session: AsyncSession, user_id: int) -> bool:
    stmt = select(Customer).where(Customer.tg_id == user_id).where(Customer.place_id is not None)
    user = await session.execute(stmt)
    return bool(user.scalar_one_or_none())


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
            canteens = await get_canteens(session)
            for canteen in canteens:
                print(f'{canteen.id} {canteen.name}')

            places = await get_places_by_canteen(session, 1)
            for place in places:
                print(f'{place.id} {place.name}')

            is_emp1 = await get_customer_by_phone(session, '+79856254915')
            print(is_emp1.id)
            is_emp2 = await get_customer_by_phone(session, '+79851310741')
            print(is_emp2)

            anna = await get_test_user(session=session, user_id=2)
            print(anna.phone_number)

        # for AsyncEngine created in function scope, close and
        # clean-up pooled connections
        await engine.dispose()


    asyncio.run(test_funcs())

