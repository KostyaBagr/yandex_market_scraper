from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Link(Base):
    """Таблица хранит ссылку на товрары и процент скидки, по которому нужно осуществлять поиск"""
    __tablename__ = 'links'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    link = Column(String, nullable=False)
    discount = Column(Integer, nullable=False)


class Product(Base):
    """Таблица хранит данные о товаре (название, цена, последние время обновления в бд)"""
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    link = Column(String, nullable=False)
    price = Column(String, nullable=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.current_timestamp())

