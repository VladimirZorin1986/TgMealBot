from typing import Any
from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import text
from database.models import HdRequest, HdType


class HDRepository:
    model = HdRequest

    @classmethod
    async def get_all_types(cls, session: AsyncSession):
        query = select(HdType).order_by(HdType.id)
        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_requests_by_filter(cls, session: AsyncSession, filter_data: dict[str, Any]):
        query = select(cls.model).filter_by(**filter_data).order_by(cls.model.id.desc())
        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def save_new_request(cls, session: AsyncSession, request_data: dict[str, Any]):
        query = insert(cls.model).values(**request_data).returning(cls.model.id)
        result = await session.execute(query)
        await session.commit()
        return result.scalar()

    @classmethod
    async def update_request(cls, session: AsyncSession, request_id: int, update_data: dict[str, Any]):
        query = update(cls.model).values(**update_data).where(cls.model.id == request_id)
        await session.execute(query)
        await session.commit()

    @classmethod
    async def delete_request(cls, session: AsyncSession, request_id: int):
        query = delete(cls.model).where(cls.model.id == request_id)
        await session.execute(query)
        await session.commit()

    @classmethod
    async def get_requests_by_user_with_boundaries(cls, session: AsyncSession, user_id: int):
        query = text(
            '''
            select y.*
            from
             (select x.*,
                     coalesce(lag(x.id) over (order by x.id), max(x.id) over ()) as prev_id,
                     coalesce(lead(x.id) over (order by x.id), min(x.id) over ()) as next_id
              from 
               (select hr.id, 
                       ht.name, 
                       hr.request_text, 
                       hr.user_id, 
                       hr.solution_text, 
                       hr.created_at, 
                       hr.done_at
                from hd_request hr join hd_type ht on (hr.type_id = ht.id)
                where hr.user_id = :user_id) x) y 
            order by y.id desc
            '''
        )
        result = await session.execute(query, {'user_id': user_id})
        return result.mappings().all()

    @classmethod
    async def get_new_requests_with_boundaries(cls, session: AsyncSession):
        query = text('''
                select y.*
                from
                 (select x.*,
                   coalesce(lag(x.id) over (order by x.id), max(x.id) over ()) as prev_id,
        	       coalesce(lead(x.id) over (order by x.id), min(x.id) over ()) as next_id
                  from       
                   (select hr.id, ht.name, hr.request_text, hr.user_id, hr.solution_text, hr.created_at, hr.done_at
                    from hd_request hr join hd_type ht on (hr.type_id = ht.id)
                    where hr.done_at is null) x) y
                order by y.id desc
                ''')
        result = await session.execute(query)
        return result.mappings().all()

    @classmethod
    async def get_all_requests_with_boundaries(cls, session: AsyncSession):
        query = text('''
                select y.*
                from
                 (select x.*,
                    coalesce(lag(x.id) over (order by x.id), max(x.id) over ()) as prev_id,
                	coalesce(lead(x.id) over (order by x.id), min(x.id) over ()) as next_id
                 from       
                  (select hr.id, ht.name, hr.request_text, hr.user_id, hr.solution_text, hr.created_at, hr.done_at
                   from hd_request hr join hd_type ht on (hr.type_id = ht.id)) x) y
                order by y.id desc
                ''')
        result = await session.execute(query)
        return result.mappings().all()

    @classmethod
    async def get_bot_users(cls, session: AsyncSession):
        query = text(
            '''
            select distinct tg_id 
            from customer c join customer_permission p on (c.id = p.customer_id)
            where c.tg_id is not null 
              and coalesce(p.end_date, current_date) >= current_date
              and p.beg_date <= current_date
            '''
        )
        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def auth_user_check(cls, session: AsyncSession, user_id: int):
        query = text(
            '''
             select * from customer c 
             where c.tg_id is not null
               and c.tg_id = :user_id
               and exists(select null from customer_permission p 
			              where p.customer_id=c.id
			                and coalesce(p.end_date, current_date) >= current_date
                            and p.beg_date <= current_date)
            '''
        )
        result = await session.execute(query, {'user_id': user_id})
        return result.scalars().one_or_none()
