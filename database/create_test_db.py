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
                            custom_menu=True,
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
                            custom_menu=True,
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
                            id=10000,
                            beg_date=datetime.date.today(),
                            canteen_id=2
                        ),
                        CustomerPermission(
                            id=11000,
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
                            id=20000,
                            beg_date=datetime.date.today(),
                            canteen_id=4
                        ),
                        CustomerPermission(
                            id=21000,
                            beg_date=datetime.date.today(),
                            canteen_id=2
                        )
                    ]
                ),
                Customer(
                    id=30000,
                    phone_number='+79123737889',
                    orders=[],
                    permissions=[
                        CustomerPermission(
                            id=30000,
                            beg_date=datetime.date.today(),
                            canteen_id=2
                        ),
                        CustomerPermission(
                            id=31000,
                            beg_date=datetime.date.today(),
                            canteen_id=4
                        )
                    ]
                ),
                Customer(
                    id=40000,
                    phone_number='+79898248036',
                    orders=[],
                    permissions=[
                        CustomerPermission(
                            id=40000,
                            beg_date=datetime.date.today(),
                            canteen_id=2
                        ),
                        CustomerPermission(
                            id=41000,
                            beg_date=datetime.date.today(),
                            canteen_id=4
                        )
                    ]
                ),
                Customer(
                    id=50000,
                    phone_number='+79180503009',
                    orders=[],
                    permissions=[
                        CustomerPermission(
                            id=50000,
                            beg_date=datetime.date.today(),
                            canteen_id=2
                        ),
                        CustomerPermission(
                            id=51000,
                            beg_date=datetime.date.today(),
                            canteen_id=4
                        )
                    ]
                ),
                Customer(
                    id=60000,
                    phone_number='+79101918076',
                    orders=[],
                    permissions=[
                        CustomerPermission(
                            id=60000,
                            beg_date=datetime.date.today(),
                            canteen_id=2
                        ),
                        CustomerPermission(
                            id=61000,
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
                            date=datetime.date.today() + datetime.timedelta(days=1),
                            beg_time=datetime.date.today() - datetime.timedelta(days=3),
                            end_time=datetime.date.today() + datetime.timedelta(days=3),
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
                                ),
                                MenuPosition(
                                    id=4,
                                    name='Лагман по-узбекски',
                                    weight='150',
                                    cost=200.10,
                                    complex_qty=1
                                ),
                                MenuPosition(
                                    id=5,
                                    name='Фреш мандариновый',
                                    weight='100/50',
                                    cost=15.50,
                                    complex_qty=2
                                )
                            ],
                            orders=[]
                        ),
                        Menu(
                            id=2,
                            name='Меню на завтрак',
                            date=datetime.date.today() + datetime.timedelta(days=2),
                            beg_time=datetime.date.today() - datetime.timedelta(days=3),
                            end_time=datetime.date.today() + datetime.timedelta(days=3),
                            canteen_id=4,
                            positions=[
                                MenuPosition(
                                    id=6,
                                    name='Блинчики со сметаной',
                                    weight='200',
                                    cost=120.00
                                ),
                                MenuPosition(
                                    id=7,
                                    name='Яичница',
                                    weight='150',
                                    cost=80.50
                                ),
                                MenuPosition(
                                    id=8,
                                    name='Чай с сахаром',
                                    weight='100/50',
                                    cost=25.45
                                ),
                                MenuPosition(
                                    id=9,
                                    name='Лагман по-узбекски',
                                    weight='150',
                                    cost=200.10,
                                    complex_qty=1
                                ),
                                MenuPosition(
                                    id=10,
                                    name='Фреш мандариновый',
                                    weight='100/50',
                                    cost=15.50,
                                    complex_qty=2
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
                            id=3,
                            name='Меню на обед',
                            date=datetime.date.today() + datetime.timedelta(days=1),
                            beg_time=datetime.date.today() - datetime.timedelta(days=3),
                            end_time=datetime.date.today() + datetime.timedelta(days=3),
                            canteen_id=4,
                            positions=[
                                MenuPosition(
                                    id=11,
                                    name='Борщ со сметаной',
                                    weight='200',
                                    cost=110.00
                                ),
                                MenuPosition(
                                    id=12,
                                    name='Котлеты с пюре',
                                    weight='150',
                                    cost=110.00
                                ),
                                MenuPosition(
                                    id=13,
                                    name='Кофе черный',
                                    weight='100/50',
                                    cost=40.50
                                ),
                                MenuPosition(
                                    id=14,
                                    name='Лагман по-узбекски',
                                    weight='150',
                                    cost=200.10,
                                    complex_qty=1
                                ),
                                MenuPosition(
                                    id=15,
                                    name='Фреш мандариновый',
                                    weight='100/50',
                                    cost=15.50,
                                    complex_qty=2
                                )
                            ],
                            orders=[]
                        ),
                        Menu(
                            id=4,
                            name='Меню на обед',
                            date=datetime.date.today() + datetime.timedelta(days=2),
                            beg_time=datetime.date.today() - datetime.timedelta(days=3),
                            end_time=datetime.date.today() + datetime.timedelta(days=3),
                            canteen_id=4,
                            positions=[
                                MenuPosition(
                                    id=16,
                                    name='Борщ со сметаной',
                                    weight='200',
                                    cost=110.00
                                ),
                                MenuPosition(
                                    id=17,
                                    name='Котлеты с пюре',
                                    weight='150',
                                    cost=110.00
                                ),
                                MenuPosition(
                                    id=18,
                                    name='Кофе черный',
                                    weight='100/50',
                                    cost=40.50
                                ),
                                MenuPosition(
                                    id=19,
                                    name='Лагман по-узбекски',
                                    weight='150',
                                    cost=200.10,
                                    complex_qty=1
                                ),
                                MenuPosition(
                                    id=20,
                                    name='Фреш мандариновый',
                                    weight='100/50',
                                    cost=15.50,
                                    complex_qty=2
                                )
                            ],
                            orders=[]
                        ),
                        Menu(
                            id=5,
                            name='Меню на обед',
                            date=datetime.date.today() + datetime.timedelta(days=1),
                            beg_time=datetime.date.today() - datetime.timedelta(days=3),
                            end_time=datetime.date.today() + datetime.timedelta(days=3),
                            canteen_id=2,
                            positions=[
                                MenuPosition(
                                    id=21,
                                    name='Щи зеленые',
                                    weight='200',
                                    cost=120.00
                                ),
                                MenuPosition(
                                    id=22,
                                    name='Биточки с рисом',
                                    weight='150',
                                    cost=80.50
                                ),
                                MenuPosition(
                                    id=23,
                                    name='Капучино',
                                    weight='100/50',
                                    cost=25.45
                                ),
                                MenuPosition(
                                    id=24,
                                    name='Лагман по-узбекски',
                                    weight='150',
                                    cost=200.10,
                                    complex_qty=1
                                ),
                                MenuPosition(
                                    id=25,
                                    name='Фреш мандариновый',
                                    weight='100/50',
                                    cost=15.50,
                                    complex_qty=2
                                )
                            ],
                            orders=[]
                        ),
                        Menu(
                            id=6,
                            name='Меню на обед',
                            date=datetime.date.today() + datetime.timedelta(days=2),
                            beg_time=datetime.date.today() - datetime.timedelta(days=3),
                            end_time=datetime.date.today() + datetime.timedelta(days=3),
                            canteen_id=2,
                            positions=[
                                MenuPosition(
                                    id=26,
                                    name='Щи зеленые',
                                    weight='200',
                                    cost=120.00
                                ),
                                MenuPosition(
                                    id=27,
                                    name='Биточки с рисом',
                                    weight='150',
                                    cost=80.50
                                ),
                                MenuPosition(
                                    id=28,
                                    name='Капучино',
                                    weight='100/50',
                                    cost=25.45
                                ),
                                MenuPosition(
                                    id=29,
                                    name='Лагман по-узбекски',
                                    weight='150',
                                    cost=200.10,
                                    complex_qty=1
                                ),
                                MenuPosition(
                                    id=30,
                                    name='Фреш мандариновый',
                                    weight='100/50',
                                    cost=15.50,
                                    complex_qty=2
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
                            id=7,
                            name='Меню на ужин',
                            date=datetime.date.today() + datetime.timedelta(days=1),
                            beg_time=datetime.date.today() - datetime.timedelta(days=3),
                            end_time=datetime.date.today() + datetime.timedelta(days=3),
                            canteen_id=4,
                            positions=[
                                MenuPosition(
                                    id=31,
                                    name='Салат витаминный',
                                    weight='200',
                                    cost=100.80
                                ),
                                MenuPosition(
                                    id=32,
                                    name='Говядина по-испански',
                                    weight='150',
                                    cost=200.10
                                ),
                                MenuPosition(
                                    id=33,
                                    name='Компот из сухофруктов',
                                    weight='100/50',
                                    cost=15.50
                                ),
                                MenuPosition(
                                    id=34,
                                    name='Лагман по-узбекски',
                                    weight='150',
                                    cost=200.10,
                                    complex_qty=1
                                ),
                                MenuPosition(
                                    id=35,
                                    name='Фреш мандариновый',
                                    weight='100/50',
                                    cost=15.50,
                                    complex_qty=2
                                )
                            ],
                            orders=[]
                        ),
                        Menu(
                            id=8,
                            name='Меню на ужин',
                            date=datetime.date.today() + datetime.timedelta(days=2),
                            beg_time=datetime.date.today() - datetime.timedelta(days=3),
                            end_time=datetime.date.today() + datetime.timedelta(days=3),
                            canteen_id=4,
                            positions=[
                                MenuPosition(
                                    id=36,
                                    name='Салат витаминный',
                                    weight='200',
                                    cost=100.80
                                ),
                                MenuPosition(
                                    id=37,
                                    name='Говядина по-испански',
                                    weight='150',
                                    cost=200.10
                                ),
                                MenuPosition(
                                    id=38,
                                    name='Компот из сухофруктов',
                                    weight='100/50',
                                    cost=15.50
                                ),
                                MenuPosition(
                                    id=39,
                                    name='Лагман по-узбекски',
                                    weight='150',
                                    cost=200.10,
                                    complex_qty=1
                                ),
                                MenuPosition(
                                    id=40,
                                    name='Фреш мандариновый',
                                    weight='100/50',
                                    cost=15.50,
                                    complex_qty=2
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
