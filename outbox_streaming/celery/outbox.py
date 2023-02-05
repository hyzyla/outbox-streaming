from typing import Any, Iterable, Mapping

import sqlalchemy as sa
import sqlalchemy.orm
from celery import Celery, Task

from .publisher import OutboxKafkaPublisher
from .sqlalchemy.storage import SQLAlchemyCeleryOutboxStorage


class SQLAlchemyCeleryOutbox:

    storage_class = SQLAlchemyCeleryOutboxStorage
    publisher_class = OutboxKafkaPublisher

    def __init__(
        self,
        celery: Celery,
        engine: sa.engine.Engine,
        scoped_session: sa.orm.scoped_session | None = None,
    ) -> None:
        self.storage = self.storage_class(
            engine=engine,
            scoped_session=scoped_session,
        )
        self.publisher = self.publisher_class(
            app=celery,
            storage=self.storage,
        )

    def save(
        self,
        task: Task,
        args: Iterable[Any] | None = None,
        kwargs: Mapping[str, Any] | None = None,
        options: Mapping[str, Any] | None = None,
        session: sa.orm.Session | None = None,
        connection: sa.engine.Connection | None = None,
    ) -> None:
        return self.storage.save(
            task=task,
            args=args,
            kwargs=kwargs,
            options=options,
            session=session,
            connection=connection,
        )
