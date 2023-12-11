from sqlalchemy import select, update, ScalarResult, Executable
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import *

Obj = type(Base)


class DbSessionManager:

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_obj_by_id(self, obj_cls: Obj, obj_id: int) -> Obj | None:
        return await self._session.get(obj_cls, obj_id)

    async def get_objs_by_cls(self, obj_cls: Obj) -> ScalarResult[Obj]:
        stmt = select(obj_cls)
        return await self.execute_stmt_with_many_return(stmt)

    async def execute_stmt_with_one_or_none_return(self, stmt: Executable) -> Obj | None:
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def execute_stmt_with_many_return(self, stmt: Executable) -> ScalarResult[Obj]:
        result = await self._session.execute(stmt)
        return result.scalars()

    async def save_new_obj(self, obj: Obj) -> None:
        self._session.add(obj)
        await self._session.commit()


class DatabaseManager:

    def __call__(self, session: AsyncSession) -> DbSessionManager:
        return DbSessionManager(session)




