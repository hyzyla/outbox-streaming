import sqlalchemy as sa
import sqlalchemy.orm
from celery import Celery

from ..publisher import OutboxKafkaPublisher
from .storage import SQLAlchemyCeleryOutboxStorage


class SQLAlchemyCeleryOutbox:

    storage_class = SQLAlchemyCeleryOutboxStorage
    publisher_class = OutboxKafkaPublisher

    def __init__(
        self,
        *,
        app: Celery,
        engine: sa.engine.Engine,
        scoped_session: sa.orm.scoped_session | None = None,
    ) -> None:
        self.storage = self.storage_class(
            engine=engine,
            scoped_session=scoped_session,
        )
        self.publisher = self.publisher_class(
            app=app,
            storage=self.storage,
        )
        self.save = self.storage.save
