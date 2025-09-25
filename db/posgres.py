from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import DeclarativeBase
from src import concts as c

DATABASE_URL: str = (
    f"postgresql+asyncpg://{c.DB_USER}:{c.DB_PASSWORD}@{c.DB_HOST}:{c.DB_PORT}/{c.DB_NAME}"
)

#Создаём движок 
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # при необходимости можно включить SQL-логи
)

#Фабрика асинхронных сессий
async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  #данные остаются доступными после commit
)


class Base(DeclarativeBase):
    """Базовый класс для всех моделей SQLAlchemy."""
    pass


async def get_async_session() -> AsyncSession:
    """Возвращает асинхронную сессию SQLAlchemy.

    Используется как зависимость в FastAPI.

    Yields:
        AsyncSession: Асинхронная сессия для работы с базой данных.
    """
    async with async_session() as session:
        yield session
