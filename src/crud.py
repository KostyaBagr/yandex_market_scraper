from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Row, RowMapping
from database_conf import engine
from models import Link, Product


async def get_or_create(model, **kwargs) ->  Row | RowMapping :
    """GET or CREATE func"""

    async with AsyncSession(bind=engine) as session:
        result = await session.execute(select(model).filter_by(**kwargs))
        instance = result.scalars().first()
        if instance:
            return instance
        else:
            instance = model(**kwargs)
            session.add(instance)
            await session.commit()
            return instance


#
async def get_links_list() -> Sequence[Row[Any] | RowMapping | Any]:
    """Получение списка ссылок из БД"""
    async with AsyncSession(bind=engine) as session:
        res = await session.execute(select(Link))
        links = res.scalars().all()
        return links


async def add_product_to_db(data: dict) -> None:
    """Сохрание товаров в бд"""
    async with AsyncSession(bind=engine) as session:
        db_prod = Product(
            name=data['name'],
            link=data['link'],
            price=data.get('price', None),
            discount=data.get('discount', None)
        )

        session.add(db_prod)
        await session.commit()
        await session.refresh(db_prod)


async def send_tg_message(product):
    pass


async def get_or_create_product(product_price: int, data: dict):
    """Ф-ция получает или добавляет товар в БД. Если товар есть в бд, то сравнивается его актуальная цена и цена из БД
        -product_price - актуальная цена товара с сайта
    """
    async with AsyncSession(bind=engine) as session:
        instance = await session.execute(select(Product).filter_by(**data))
        product_instance = instance.scalars().first()
        if product_instance:

            if int(product_instance.price) > product_price:   # сравниваю текущую цену и цену из бд
                product_instance.price = product_price
                await session.commit()
                await send_tg_message(product_instance)

        else:
            product_instance = Product(**data)
            session.add(product_instance)
            await session.commit()

