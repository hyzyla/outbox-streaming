from typing import Any, Iterable, Mapping, Optional

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
        scoped_session: Optional[sa.orm.scoped_session] = None,
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
        args: Optional[Iterable[Any]] = None,
        kwargs: Optional[Mapping[str, Any]] = None,
        options: Optional[Mapping[str, Any]] = None,
        session: Optional[sa.orm.Session] = None,
        connection: Optional[sa.engine.Connection] = None,
    ) -> None:
        return self.storage.save(
            task=task,
            args=args,
            kwargs=kwargs,
            options=options,
            session=session,
            connection=connection,
        )
