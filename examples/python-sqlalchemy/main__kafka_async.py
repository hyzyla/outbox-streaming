import asyncio
from asyncio import current_task
from pprint import pprint

from outbox_streaming.asyncio.kafka.sqlalchemy import AsyncSQLAlchemyKafkaOutboxStorage
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_scoped_session,
    AsyncSession,
)
from sqlalchemy.orm import sessionmaker

DATABASE_URL = 'postgresql+asyncpg://postgres:postgres@localhost:5432/outbox'


engine = create_async_engine(DATABASE_URL, future=True)
metadata = MetaData(bind=engine)

session_factory = sessionmaker(bind=engine, class_=AsyncSession)
session = async_scoped_session(session_factory, scopefunc=current_task)


storage = AsyncSQLAlchemyKafkaOutboxStorage(
    engine=engine,
    scoped_session=session,
)


async def main():

    await storage.create_tables()

    await storage.save(topic='test-topic', value='1')
    await storage.save(topic='test-topic', value='2')
    await session.commit()

    async for batch in storage.get_messages_batch(size=10):
        if not batch:
            return
        pprint(batch)


asyncio.run(main())



