import asyncio
import datetime
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine
from database.models import Canteen, DeliveryPlace, Customer, Menu, MenuPosition, MealType, Base, CustomerPermission


async def insert_objects(async_session: async_sessionmaker[AsyncSession]) -> None:
    async with async_session() as session:
        async with session.begin():
            canteens = [
                Canteen(
                    id=2,
                    name='Столовая ТНГ',
                    places=[
                        DeliveryPlace(
                            id=1,
                            name='Причал',
                            begin_date=datetime.date(year=2023, month=9, day=18),
                            orders=[],
                            customers=[]
                        ),
                        DeliveryPlace(
                            id=2,
                            name='Столовая',
                            begin_date=datetime.date(year=2023, month=9, day=18),
                            orders=[],
                            customers=[]
                        ),
                        DeliveryPlace(
                            id=3,
                            name='Администрация',
                            begin_date=datetime.date(year=2023, month=9, day=18),
                            orders=[],
                            customers=[]
                        )
                    ],
                    menus=[],
                    permissions=[]
                ),
                Canteen(
                    id=4,
                    name='Столовая ОПС',
                    places=[
                        DeliveryPlace(
                            id=4,
                            name='Терминал',
                            begin_date=datetime.date(year=2023, month=9, day=18),
                            orders=[],
                            customers=[]
                        ),
                        DeliveryPlace(
                            id=5,
                            name='Столовая',
                            begin_date=datetime.date(year=2023, month=9, day=18),
                            orders=[],
                            customers=[]
                        ),
                        DeliveryPlace(
                            id=6,
                            name='Порт',
                            begin_date=datetime.date(year=2023, month=9, day=18),
                            orders=[],
                            customers=[]
                        )
                    ],
                    menus=[],
                    permissions=[]
                )
            ]
            customers = [
                Customer(
                    id=10000,
                    phone_number='+79856254915',
                    orders=[],
                    permissions=[
                        CustomerPermission(
                            beg_date=datetime.date.today(),
                            canteen_id=2
                        ),
                        CustomerPermission(
                            beg_date=datetime.date.today(),
                            canteen_id=4
                        )
                    ]
                ),
                Customer(
                    id=20000,
                    phone_number='+79191399333',
                    orders=[],
                    permissions=[
                        CustomerPermission(
                            beg_date=datetime.date.today(),
                            canteen_id=4
                        )
                    ]
                )
            ]
            meal_types = [
                MealType(
                    name='завтрак',
                    menus=[
                        Menu(
                            id=1,
                            name='Меню на завтрак',
                            date=datetime.date.fromisoformat('2023-11-20'),
                            beg_time=datetime.datetime.fromisoformat('2023-11-16'),
                            end_time=datetime.datetime.fromisoformat('2023-11-25'),
                            canteen_id=4,
                            positions=[
                                MenuPosition(
                                    id=1,
                                    name='Блинчики со сметаной',
                                    weight='200',
                                    cost=120.00
                                ),
                                MenuPosition(
                                    id=2,
                                    name='Яичница',
                                    weight='150',
                                    cost=80.50
                                ),
                                MenuPosition(
                                    id=3,
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
                            id=2,
                            name='Меню на обед',
                            date=datetime.date.fromisoformat('2023-11-19'),
                            beg_time=datetime.datetime.fromisoformat('2023-11-16'),
                            end_time=datetime.datetime.fromisoformat('2023-11-30'),
                            canteen_id=4,
                            positions=[
                                MenuPosition(
                                    id=4,
                                    name='Борщ со сметаной',
                                    weight='200',
                                    cost=110.00
                                ),
                                MenuPosition(
                                    id=5,
                                    name='Котлеты с пюре',
                                    weight='150',
                                    cost=110.00
                                ),
                                MenuPosition(
                                    id=6,
                                    name='Кофе черный',
                                    weight='100/50',
                                    cost=40.50
                                )
                            ],
                            orders=[]
                        ),
                        Menu(
                            id=3,
                            name='Меню на обед',
                            date=datetime.date.fromisoformat('2023-11-20'),
                            beg_time=datetime.datetime.fromisoformat('2023-11-16'),
                            end_time=datetime.datetime.fromisoformat('2023-11-30'),
                            canteen_id=2,
                            positions=[
                                MenuPosition(
                                    id=7,
                                    name='Щи зеленые',
                                    weight='200',
                                    cost=120.00
                                ),
                                MenuPosition(
                                    id=8,
                                    name='Биточки с рисом',
                                    weight='150',
                                    cost=80.50
                                ),
                                MenuPosition(
                                    id=9,
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
                            id=4,
                            name='Меню на ужин',
                            date=datetime.date.fromisoformat('2023-11-19'),
                            beg_time=datetime.datetime.fromisoformat('2023-11-16'),
                            end_time=datetime.datetime.fromisoformat('2023-11-30'),
                            canteen_id=4,
                            positions=[
                                MenuPosition(
                                    id=10,
                                    name='Салат витаминный',
                                    weight='200',
                                    cost=100.80
                                ),
                                MenuPosition(
                                    id=11,
                                    name='Говядина по-испански',
                                    weight='150',
                                    cost=200.10
                                ),
                                MenuPosition(
                                    id=12,
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

    # for AsyncEngine created in function scope, close and
    # clean-up pooled connections
    await engine.dispose()


if __name__ == '__main__':
    asyncio.run(async_main())
