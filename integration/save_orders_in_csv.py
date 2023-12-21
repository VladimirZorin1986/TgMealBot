import csv
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text


async def async_main():
    engine = create_async_engine(
        "postgresql+asyncpg://postgres:postgres@localhost/test_pg",
        echo=True,
    )

    async with engine.connect() as conn:
        stmt = text('''
           SELECT mo.id,
                  menu.canteen_id,
                  mo.menu_id,
                  menu.date,
                  mo.customer_id,
                  mo.place_id,
                  mo.amt
           FROM meal_order mo JOIN menu ON (mo.menu_id=menu.id)
           WHERE mo.sent_to_eis IS NULL
             AND menu.end_time::date = now()::date
        ''')
        result = await conn.execute(stmt)
        with open('static/orders.csv', 'w', newline='') as csvfile:
            fieldnames = ['id', 'canteen_id', 'menu_id', 'date', 'customer_id', 'place_id', 'amt']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
            writer.writeheader()
            for order in result.all():
                writer.writerow(dict(zip(fieldnames, order)))

        stmt = text('''
           SELECT od.id,
                  od.order_id,
                  ROW_NUMBER() OVER (PARTITION BY od.order_id, mp.menu_id ORDER BY mp.id) AS num_of_menu,
                  od.quantity,
                  od.quantity * mp.cost AS amt
           FROM order_detail od JOIN menu_position mp ON (od.menu_pos_id=mp.id)
           WHERE mo.order_id = 29
        ''')
        result2 = await conn.execute(stmt)
        with open('static/details.csv', 'w', newline='') as csvfile:
            fieldnames = ['id', 'order_id', 'num_of_menu', 'qty', 'amt']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
            writer.writeheader()
            for detail in result2.all():
                writer.writerow(dict(zip(fieldnames, detail)))

    await engine.dispose()


if __name__ == '__main__':
    asyncio.run(async_main())
