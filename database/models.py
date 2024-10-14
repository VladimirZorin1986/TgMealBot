import datetime
from decimal import Decimal
from typing import List, Optional
from sqlalchemy import ForeignKey, Identity
from sqlalchemy.types import BigInteger, String, SmallInteger, Integer, Date, DateTime, Numeric, Boolean
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Canteen(Base):
    __tablename__ = 'canteen'

    id: Mapped[int] = mapped_column(
        SmallInteger,
        primary_key=True
    )
    name: Mapped[str] = mapped_column(String(100))

    places: Mapped[List['DeliveryPlace']] = relationship()
    menus: Mapped[List['Menu']] = relationship(order_by='Menu.date')
    permissions: Mapped[List['CustomerPermission']] = relationship()


class DeliveryPlace(Base):
    __tablename__ = 'delivery_place'

    id: Mapped[int] = mapped_column(
        SmallInteger,
        primary_key=True
    )
    name: Mapped[str] = mapped_column(String(80))
    begin_date: Mapped[datetime.date] = mapped_column(Date)
    end_date: Mapped[Optional[datetime.date]] = mapped_column(Date, nullable=True)
    custom_menu: Mapped[bool] = mapped_column(Boolean, default=False)
    canteen_id: Mapped[int] = mapped_column(
        ForeignKey(column='canteen.id', ondelete='CASCADE')
    )
    orders: Mapped[List['Order']] = relationship()
    customers: Mapped[List['Customer']] = relationship()


class Customer(Base):
    __tablename__ = 'customer'

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )
    tg_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    phone_number: Mapped[str] = mapped_column(String(12), unique=True, index=True)
    place_id: Mapped[int] = mapped_column(
        ForeignKey('delivery_place.id', ondelete='SET NULL'),
        nullable=True
    )

    orders: Mapped[List['Order']] = relationship()
    permissions: Mapped[List['CustomerPermission']] = relationship()


class CustomerPermission(Base):
    __tablename__ = 'customer_permission'

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )
    beg_date: Mapped[datetime.date] = mapped_column(Date)
    end_date: Mapped[Optional[datetime.date]] = mapped_column(Date, nullable=True)
    canteen_id: Mapped[int] = mapped_column(
        ForeignKey('canteen.id', ondelete='CASCADE')
    )
    customer_id: Mapped[int] = mapped_column(
        ForeignKey('customer.id', ondelete='CASCADE')
    )


class MealType(Base):
    __tablename__ = 'meal_type'

    id: Mapped[int] = mapped_column(
        SmallInteger,
        Identity(always=True),
        primary_key=True
    )
    name: Mapped[str] = mapped_column(String(20))

    menus: Mapped[List['Menu']] = relationship()


class Menu(Base):
    __tablename__ = 'menu'

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )
    name: Mapped[str] = mapped_column(String(120))
    date: Mapped[datetime.date] = mapped_column(Date)
    beg_time: Mapped[datetime.datetime] = mapped_column(DateTime)
    end_time: Mapped[datetime.datetime] = mapped_column(DateTime)
    canteen_id: Mapped[int] = mapped_column(
        ForeignKey('canteen.id', ondelete='CASCADE')
    )
    meal_type_id: Mapped[int] = mapped_column(
        ForeignKey('meal_type.id', ondelete='RESTRICT')
    )

    positions: Mapped[List['MenuPosition']] = relationship()
    orders: Mapped[List['Order']] = relationship()


class MenuPosition(Base):
    __tablename__ = 'menu_position'

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True
    )
    name: Mapped[str] = mapped_column(String(120))
    weight: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    cost: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=10, scale=2, asdecimal=True),
        nullable=True
    )
    complex_qty: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True)
    menu_id: Mapped[int] = mapped_column(
        ForeignKey('menu.id', ondelete='CASCADE')
    )
    eis_doc_num: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True)
    color_num: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True)


class Order(Base):
    __tablename__ = 'meal_order'

    id: Mapped[int] = mapped_column(
        Integer,
        Identity(always=True),
        primary_key=True
    )
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime)
    amt: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=10, scale=2, asdecimal=True),
        nullable=True
    )
    sent_to_eis: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, nullable=True)
    customer_id: Mapped[int] = mapped_column(
        ForeignKey('customer.id', ondelete='CASCADE')
    )
    menu_id: Mapped[int] = mapped_column(
        ForeignKey('menu.id', ondelete='RESTRICT')
    )
    place_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey('delivery_place.id', ondelete='RESTRICT')
    )

    details: Mapped[List['OrderDetail']] = relationship(passive_deletes=True)


class OrderDetail(Base):
    __tablename__ = 'order_detail'

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=True),
        primary_key=True
    )
    quantity: Mapped[int] = mapped_column(SmallInteger)
    order_id: Mapped[int] = mapped_column(
        ForeignKey('meal_order.id', ondelete='CASCADE')
    )
    menu_pos_id: Mapped[int] = mapped_column(
        ForeignKey('menu_position.id', ondelete='RESTRICT')
    )
