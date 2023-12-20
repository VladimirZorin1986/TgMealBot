import csv
import asyncio
import datetime
from decimal import Decimal
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy import select, text
from database.models import Order, OrderDetail, Menu, MenuPosition


async def async_main():
    engine = create_async_engine(
        "postgresql+asyncpg://postgres:postgres@localhost/test_pg",
        echo=True,
    )

    async with engine.connect() as conn:
        stmt = select(
            Order.id,
            Menu.canteen_id,
            Order.menu_id,
            Menu.date,
            Order.customer_id,
            Order.place_id,
            Order.amt
        ).join(Menu)
        result = await conn.execute(stmt)
        with open('orders.csv', 'w', newline='') as csvfile:
            fieldnames = ['id', 'canteen_id', 'menu_id', 'date', 'customer_id', 'place_id', 'amt']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
            writer.writeheader()
            for order in result.all():
                writer.writerow(dict(zip(fieldnames, order)))

        stmt = text('''SELECT od.id,
       od.order_id,
       ROW_NUMBER() OVER (PARTITION BY od.order_id, mp.menu_id ORDER BY mp.id) AS num_of_menu,
       od.quantity,
       od.quantity * mp.cost AS amt
FROM order_detail od join menu_position mp ON (od.menu_pos_id=mp.id)''')
        result2 = await conn.execute(stmt)
        with open('details.csv', 'w', newline='') as csvfile:
            fieldnames = ['id', 'order_id', 'num_of_menu', 'qty', 'amt']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
            writer.writeheader()
            for detail in result2.all():
                writer.writerow(dict(zip(fieldnames, detail)))

    await engine.dispose()


if __name__ == '__main__':
    asyncio.run(async_main())
