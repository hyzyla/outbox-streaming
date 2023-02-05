from typing import Any, Iterable, Mapping, Optional

import sqlalchemy as sa
import sqlalchemy.orm
from celery import Celery, Task
from sqlalchemy.ext.asyncio import AsyncEngine, async_scoped_session

from .storage import AsyncSQLAlchemyCeleryOutboxStorage
from ..publisher import AsyncOutboxCeleryPublisher


class AsyncSQLAlchemyCeleryOutbox:

    storage_class = AsyncSQLAlchemyCeleryOutboxStorage
    publisher_class = AsyncOutboxCeleryPublisher

    def __init__(
        self,
        celery: Celery,
        engine: AsyncEngine,
        scoped_session: Optional[async_scoped_session] = None,
    ) -> None:
        self.storage = self.storage_class(engine=engine, scoped_session=scoped_session)
        self.publisher = self.publisher_class(
            celery=celery,
            storage=self.storage,
        )

    async def save(
        self,
        task: Task,
        args: Optional[Iterable[Any]] = None,
        kwargs: Optional[Mapping[str, Any]] = None,
        options: Optional[Mapping[str, Any]] = None,
        session: Optional[sa.orm.Session] = None,
        connection: Optional[sa.engine.Connection] = None,
    ) -> None:
        return await self.storage.save(
            task=task,
            args=args,
            kwargs=kwargs,
            options=options,
            session=session,
            connection=connection,
        )
