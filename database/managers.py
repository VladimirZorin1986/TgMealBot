from sqlalchemy import select, update, ScalarResult, Executable, Result
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import *

Obj = type(Base)


class DbSessionManager:

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_obj_by_id(self, obj_cls: Obj.__class__, obj_id: int) -> Obj | None:
        return await self._session.get(obj_cls, obj_id)

    async def get_objs_by_attrs(self, obj_cls: Obj.__class__, **kwargs) -> ScalarResult[Obj]:
        raw_result = await self._get_raw_result(obj_cls, **kwargs)
        return raw_result.scalars()

    async def get_obj_by_attrs(self, obj_cls: Obj.__class__, **kwargs) -> Obj | None:
        raw_result = await self._get_raw_result(obj_cls, **kwargs)
        return raw_result.scalar_one_or_none()

    async def _get_raw_result(self, obj_cls: Obj.__class__, **kwargs) -> Result[Obj]:
        stmt = select(obj_cls)
        for attr, value in kwargs.items():
            stmt = stmt.where(getattr(obj_cls, attr) == value)
        return await self._session.execute(stmt)

    # async def execute_stmt_with_one_or_none_return(self, stmt: Executable) -> Obj | None:
    #     result = await self._session.execute(stmt)
    #     return result.scalar_one_or_none()
    #
    # async def execute_stmt_with_many_return(self, stmt: Executable) -> ScalarResult[Obj]:
    #     result = await self._session.execute(stmt)
    #     return result.scalars()

    async def save_new_obj(self, obj: Obj) -> None:
        self._session.add(obj)
        await self._session.commit()

    async def update_obj(self, obj: Obj, **kwargs) -> None:
        for (key, value) in kwargs.items():
            setattr(obj, key, value)
        await self._session.commit()

    async def delete_obj(self, obj: Obj) -> None:
        await self._session.delete(obj)
        await self._session.commit()

    async def delete_obj_by_id(self, obj_cls: Obj.__class__, obj_id: int) -> None:
        await self.delete_obj(await self.get_obj_by_id(obj_cls, obj_id))


class DatabaseManager:

    def __call__(self, session: AsyncSession) -> DbSessionManager:
        return DbSessionManager(session)




