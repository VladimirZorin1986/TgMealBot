from sqlalchemy import ScalarResult, select
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Base

Obj = type(Base)


async def get_obj_by_id(session: AsyncSession, obj_cls: Obj, obj_id: int) -> Obj | None:
    return await session.get(obj_cls, obj_id)


async def get_objs_by_cls(session: AsyncSession, obj_cls: Obj) -> ScalarResult[Obj]:
    stmt = select(obj_cls)
    result = await session.execute(stmt)
    return result.scalars()
