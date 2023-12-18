import datetime
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Customer, CustomerPermission


async def is_auth(session: AsyncSession, user_id: int) -> bool:
    stmt = select(Customer).where(Customer.tg_id == user_id).where(Customer.place_id is not None)
    result = await session.execute(stmt.options(selectinload(Customer.permissions)))
    customer = result.scalar_one_or_none()
    if customer and _is_valid_customer(customer):
        return True
    return False


def _is_valid_permission(permission: CustomerPermission) -> bool:
    return permission.beg_date <= datetime.date.today() <= (permission.end_date or datetime.date.today())


def _is_valid_customer(customer: Customer) -> bool:
    return any(filter(_is_valid_permission, customer.permissions))
