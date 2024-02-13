from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Row, RowMapping
from database_conf import engine
from models import Link, Product


async def add_link_to_db(link: str, discount: int) -> None:
    """Сохранение объекта ссылки в БД"""
    async with AsyncSession(bind=engine) as session:
        link_db = Link(link=link, discount=discount)
        session.add(link_db)
        await session.commit()
        await session.refresh(link_db)


async def get_links_list() -> Sequence[Row[Any] | RowMapping | Any]:
    """Получение списка ссылок из БД"""
    async with AsyncSession(bind=engine) as session:
        res = await session.execute(select(Link))
        links = res.scalars().all()
        return links


async def add_product_to_db(data: dict) -> None:
    """Сохрание товаров в бд"""
    async with AsyncSession(bind=engine) as session:
        print(data)
        db_prod = Product(
            name=data['name'],
            link=data['link'],
            price=data.get('price', None),
            discount=data.get('discount', None)
        )

        session.add(db_prod)
        await session.commit()
        await session.refresh(db_prod)
        print(db_prod)
