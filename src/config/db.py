from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from config.settings import AppSettings


engine = create_async_engine(AppSettings().db.url)

new_session = async_sessionmaker(engine, expire_on_commit=False)

Base = declarative_base()


async def get_session() -> AsyncSession:
    async with new_session() as session:
        yield session