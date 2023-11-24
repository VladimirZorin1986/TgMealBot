import asyncio
import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine
from sqlalchemy.orm import selectinload
from database.models import Canteen, DeliveryPlace, Customer, Menu, MenuPosition, MealType, Base, CustomerPermission


async def insert_objects(async_session: async_sessionmaker[AsyncSession]) -> None:
    async with async_session() as session:
        async with session.begin():
            canteens = [
                Canteen(
                    name='Столовая ТНГ',
                    places=[
                        DeliveryPlace(
                            name='Причал',
                            begin_date=datetime.date(year=2023, month=9, day=18),
                            customers=[]
                        ),
                        DeliveryPlace(
                            name='Столовая',
                            begin_date=datetime.date(year=2023, month=9, day=18),
                            customers=[]
                        ),
                        DeliveryPlace(
                            name='Администрация',
                            begin_date=datetime.date(year=2023, month=9, day=18),
                            customers=[]
                        )
                    ],
                    menus=[]
                ),
                Canteen(
                    name='Столовая ОПС',
                    places=[
                        DeliveryPlace(
                            name='Терминал',
                            begin_date=datetime.date(year=2023, month=9, day=18),
                            customers=[]
                        ),
                        DeliveryPlace(
                            name='Столовая',
                            begin_date=datetime.date(year=2023, month=9, day=18),
                            customers=[]
                        ),
                        DeliveryPlace(
                            name='Порт',
                            begin_date=datetime.date(year=2023, month=9, day=18),
                            customers=[]
                        )
                    ],
                    menus=[]
                )
            ]
            customers = [
                Customer(
                    eis_id=10000,
                    phone_number='+79856254915',
                    orders=[],
                    permissions=[
                        CustomerPermission(
                            beg_date=datetime.date.today(),
                            canteen_id=1
                        ),
                        CustomerPermission(
                            beg_date=datetime.date.today(),
                            canteen_id=2
                        )
                    ]
                ),
                Customer(
                    eis_id=20000,
                    phone_number='+79191399333',
                    orders=[],
                    permissions=[
                        CustomerPermission(
                            beg_date=datetime.date.today(),
                            canteen_id=2
                        )
                    ]
                )
            ]
            meal_types = [
                MealType(
                    name='завтрак',
                    menus=[
                        Menu(
                            name='Меню на завтрак',
                            date=datetime.date.fromisoformat('2023-11-20'),
                            beg_time=datetime.datetime.fromisoformat('2023-11-16'),
                            end_time=datetime.datetime.fromisoformat('2023-11-25'),
                            canteen_id=2,
                            positions=[
                                MenuPosition(
                                    name='Блинчики со сметаной',
                                    weight='200',
                                    cost=120.00
                                ),
                                MenuPosition(
                                    name='Яичница',
                                    weight='150',
                                    cost=80.50
                                ),
                                MenuPosition(
                                    name='Чай с сахаром',
                                    weight='100/50',
                                    cost=25.45
                                )
                            ],
                            orders=[]
                        )
                    ]
                ),
                MealType(
                    name='обед',
                    menus=[
                        Menu(
                            name='Меню на обед',
                            date=datetime.date.fromisoformat('2023-11-19'),
                            beg_time=datetime.datetime.fromisoformat('2023-11-16'),
                            end_time=datetime.datetime.fromisoformat('2023-11-25'),
                            canteen_id=2,
                            positions=[
                                MenuPosition(
                                    name='Борщ со сметаной',
                                    weight='200',
                                    cost=110.00
                                ),
                                MenuPosition(
                                    name='Котлеты с пюре',
                                    weight='150',
                                    cost=110.00
                                ),
                                MenuPosition(
                                    name='Кофе черный',
                                    weight='100/50',
                                    cost=40.50
                                )
                            ],
                            orders=[]
                        ),
                        Menu(
                            name='Меню на обед',
                            date=datetime.date.fromisoformat('2023-11-20'),
                            beg_time=datetime.datetime.fromisoformat('2023-11-16'),
                            end_time=datetime.datetime.fromisoformat('2023-11-25'),
                            canteen_id=1,
                            positions=[
                                MenuPosition(
                                    name='Щи зеленые',
                                    weight='200',
                                    cost=120.00
                                ),
                                MenuPosition(
                                    name='Биточки с рисом',
                                    weight='150',
                                    cost=80.50
                                ),
                                MenuPosition(
                                    name='Капучино',
                                    weight='100/50',
                                    cost=25.45
                                )
                            ],
                            orders=[]
                        )
                    ]
                ),
                MealType(
                    name='ужин',
                    menus=[
                        Menu(
                            name='Меню на ужин',
                            date=datetime.date.fromisoformat('2023-11-19'),
                            beg_time=datetime.datetime.fromisoformat('2023-11-16'),
                            end_time=datetime.datetime.fromisoformat('2023-11-25'),
                            canteen_id=2,
                            positions=[
                                MenuPosition(
                                    name='Салат витаминный',
                                    weight='200',
                                    cost=100.80
                                ),
                                MenuPosition(
                                    name='Говядина по-испански',
                                    weight='150',
                                    cost=200.10
                                ),
                                MenuPosition(
                                    name='Компот из сухофруктов',
                                    weight='100/50',
                                    cost=15.50
                                )
                            ],
                            orders=[]
                        )
                    ]
                )
            ]

            session.add_all(canteens)
            session.add_all(customers)
            session.add_all(meal_types)


async def select_and_update_objects(
    async_session: async_sessionmaker[AsyncSession],
) -> None:
    async with async_session() as session:
        stmt = select(Canteen).options(selectinload(Canteen.places))

        result = await session.execute(stmt)

        for canteen in result.scalars():
            print(canteen)
            print(f"name: {canteen.name}")
            for place in canteen.places:
                print(place)

        result = await session.execute(select(Canteen).order_by(Canteen.id).limit(1))

        tng = result.scalars().one()

        tng.name = 'Столовая ТНГ'

        await session.commit()

        # access attribute subsequent to commit; this is what
        # expire_on_commit=False allows
        print(tng.name)

        # alternatively, AsyncAttrs may be used to access any attribute
        # as an awaitable (new in 2.0.13)
        for place in await tng.awaitable_attrs.places:
            print(place.name)


async def async_main() -> None:
    engine = create_async_engine(
        "postgresql+asyncpg://postgres:postgres@localhost/test_pg",
        echo=True,
    )

    # async_sessionmaker: a factory for new AsyncSession objects.
    # expire_on_commit - don't expire objects after transaction commit
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    await insert_objects(async_session)
    # await select_and_update_objects(async_session)

    # for AsyncEngine created in function scope, close and
    # clean-up pooled connections
    await engine.dispose()


if __name__ == '__main__':
    asyncio.run(async_main())
