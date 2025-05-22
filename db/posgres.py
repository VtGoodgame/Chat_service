from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from src import concts as c

DATABASE_URL = f"postgresql+asyncpg://{c.DB_USER}:{c.DB_PASSWORD}@{c.DB_HOST}:{c.DB_PORT}/{c.DB_NAME}"

engine = create_async_engine(DATABASE_URL, echo=False)

async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

class Base(DeclarativeBase):
    pass

async def get_async_session() -> AsyncSession:
    async with async_session() as session:
        yield session

    