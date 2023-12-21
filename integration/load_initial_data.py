import asyncio
import datetime
import csv
from decimal import Decimal
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from database.models import Canteen, DeliveryPlace, Customer, Menu, MenuPosition, MealType, CustomerPermission


async def async_main() -> None:
    engine = create_async_engine(
        "postgresql+asyncpg://postgres:postgres@localhost/test_pg",
        echo=True,
    )

    session_maker = async_sessionmaker(engine, expire_on_commit=False)

    async with session_maker() as session:
        canteens = []
        menus = []
        positions = []
        places = []

        meal_types = [
            MealType(name='завтрак', menus=[]),
            MealType(name='обед', menus=[]),
            MealType(name='ужин', menus=[])
        ]

        with open('static/canteen.csv', newline='') as csvfile:
            spamreader = csv.DictReader(
                csvfile,
                fieldnames=['id', 'name'],
                delimiter=';',
                quotechar='|'
            )
            for row in spamreader:
                canteen = Canteen(
                    id=int(row['id']),
                    name=row['name'],
                    places=[],
                    menus=[],
                    permissions=[]
                )
                canteens.append(canteen)

        with open('static/delivery_place.csv', newline='') as csvfile:
            spamreader = csv.DictReader(
                csvfile,
                fieldnames=['id', 'name', 'begin_date', 'end_date', 'custom_menu', 'canteen_id'],
                delimiter=';',
                quotechar='|'
            )
            for row in spamreader:
                place = DeliveryPlace(
                    id=int(row['id']),
                    name=row['name'],
                    begin_date=datetime.datetime.strptime(row['begin_date'], '%d.%m.%Y').date(),
                    end_date=datetime.datetime.strptime(row['end_date'], '%d.%m.%Y').date() if row['end_date'] else None,
                    custom_menu=False,
                    canteen_id=int(row['canteen_id']),
                    orders=[],
                    customers=[]
                )
                places.append(place)

        with open('static/menu.csv', newline='') as csvfile:
            spamreader = csv.DictReader(
                csvfile,
                fieldnames=['id', 'name', 'date', 'beg_time', 'end_time', 'meal_type_id', 'canteen_id'],
                delimiter=';',
                quotechar='|'
            )
            for row in spamreader:
                menu = Menu(
                    id=int(row['id']),
                    name=row['name'],
                    date=datetime.datetime.strptime(row['date'], '%d.%m.%Y').date(),
                    beg_time=datetime.datetime.strptime(row['beg_time'], '%d.%m.%Y %H:%M:%S'),
                    end_time=datetime.datetime.strptime(row['end_time'], '%d.%m.%Y %H:%M:%S'),
                    meal_type_id=int(row['meal_type_id']),
                    canteen_id=int(row['canteen_id']),
                    positions=[],
                    orders=[]
                )
                menus.append(menu)

        with open('static/menu_position.csv', newline='') as csvfile:
            spamreader = csv.DictReader(
                csvfile,
                fieldnames=['id', 'name', 'weight', 'cost', 'complex_qty', 'menu_id'],
                delimiter=';',
                quotechar='|'
            )
            for row in spamreader:
                position = MenuPosition(
                    id=int(row['id']),
                    name=row['name'],
                    weight=row['weight'],
                    cost=Decimal(row['cost']),
                    complex_qty=int(row['complex_qty']) if row['complex_qty'] else None,
                    menu_id=int(row['menu_id'])
                )
                positions.append(position)

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

        session.add_all(meal_types)
        session.add_all(canteens),
        session.add_all(places),
        session.add_all(menus),
        session.add_all(positions)
        session.add_all(customers)
        await session.commit()

    await engine.dispose()

if __name__ == '__main__':
    asyncio.run(async_main())



